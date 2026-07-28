from __future__ import annotations

import argparse
import json
import os
import sqlite3
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any, Protocol


TABLE_NAME = "inventario"
DEFAULT_ENDPOINT_URL = "http://localhost:4566"


class InventoryStore(Protocol):
    def create_table(self) -> None:
        ...

    def put_item(self, item: dict[str, Any]) -> dict[str, Any]:
        ...

    def get_item(self, sku: str) -> dict[str, Any] | None:
        ...

    def update_item(self, sku: str, changes: dict[str, Any]) -> dict[str, Any] | None:
        ...

    def delete_item(self, sku: str) -> bool:
        ...


def _normalize_item(item: dict[str, Any]) -> dict[str, Any]:
    required = {"sku", "nombre", "precio", "stock"}
    missing = required - set(item)
    if missing:
        raise ValueError(f"Campos requeridos faltantes: {', '.join(sorted(missing))}")

    normalized = dict(item)
    normalized["sku"] = str(normalized["sku"])
    normalized["nombre"] = str(normalized["nombre"])
    normalized["precio"] = Decimal(str(normalized["precio"]))
    normalized["stock"] = int(normalized["stock"])
    return normalized


def _json_ready(value: Any) -> Any:
    if isinstance(value, Decimal):
        return int(value) if value % 1 == 0 else float(value)
    if isinstance(value, dict):
        return {key: _json_ready(val) for key, val in value.items()}
    if isinstance(value, list):
        return [_json_ready(val) for val in value]
    return value


@dataclass
class DynamoInventoryStore:
    endpoint_url: str = DEFAULT_ENDPOINT_URL
    table_name: str = TABLE_NAME
    region_name: str = "us-east-1"

    def __post_init__(self) -> None:
        import boto3
        from botocore.exceptions import ClientError

        self._client_error = ClientError
        self.resource = boto3.resource(
            "dynamodb",
            endpoint_url=self.endpoint_url,
            region_name=self.region_name,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "test"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "test"),
        )
        self.table = self.resource.Table(self.table_name)

    def create_table(self) -> None:
        try:
            self.resource.create_table(
                TableName=self.table_name,
                AttributeDefinitions=[{"AttributeName": "sku", "AttributeType": "S"}],
                KeySchema=[{"AttributeName": "sku", "KeyType": "HASH"}],
                BillingMode="PAY_PER_REQUEST",
            )
            self.table.wait_until_exists()
        except self._client_error as exc:
            if exc.response.get("Error", {}).get("Code") != "ResourceInUseException":
                raise

    def put_item(self, item: dict[str, Any]) -> dict[str, Any]:
        normalized = _normalize_item(item)
        self.table.put_item(Item=normalized)
        return normalized

    def get_item(self, sku: str) -> dict[str, Any] | None:
        response = self.table.get_item(Key={"sku": sku})
        return response.get("Item")

    def update_item(self, sku: str, changes: dict[str, Any]) -> dict[str, Any] | None:
        if not self.get_item(sku):
            return None
        if not changes:
            return self.get_item(sku)

        names = {f"#k{i}": key for i, key in enumerate(changes)}
        values = {f":v{i}": Decimal(str(value)) if key == "precio" else value for i, (key, value) in enumerate(changes.items())}
        expression = "SET " + ", ".join(f"{alias} = :v{i}" for i, alias in enumerate(names))
        response = self.table.update_item(
            Key={"sku": sku},
            UpdateExpression=expression,
            ExpressionAttributeNames=names,
            ExpressionAttributeValues=values,
            ReturnValues="ALL_NEW",
        )
        return response["Attributes"]

    def delete_item(self, sku: str) -> bool:
        existed = self.get_item(sku) is not None
        self.table.delete_item(Key={"sku": sku})
        return existed


@dataclass
class SQLiteInventoryStore:
    db_path: str = "inventario.db"

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def create_table(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS inventario (
                    sku TEXT PRIMARY KEY,
                    nombre TEXT NOT NULL,
                    precio REAL NOT NULL,
                    stock INTEGER NOT NULL
                )
                """
            )

    def put_item(self, item: dict[str, Any]) -> dict[str, Any]:
        normalized = _normalize_item(item)
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO inventario (sku, nombre, precio, stock)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(sku) DO UPDATE SET
                    nombre = excluded.nombre,
                    precio = excluded.precio,
                    stock = excluded.stock
                """,
                (
                    normalized["sku"],
                    normalized["nombre"],
                    float(normalized["precio"]),
                    normalized["stock"],
                ),
            )
        return normalized

    def get_item(self, sku: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute("SELECT sku, nombre, precio, stock FROM inventario WHERE sku = ?", (sku,)).fetchone()
        return dict(row) if row else None

    def update_item(self, sku: str, changes: dict[str, Any]) -> dict[str, Any] | None:
        current = self.get_item(sku)
        if not current:
            return None
        updated = {**current, **changes}
        self.put_item(updated)
        return self.get_item(sku)

    def delete_item(self, sku: str) -> bool:
        with self._connect() as conn:
            cursor = conn.execute("DELETE FROM inventario WHERE sku = ?", (sku,))
        return cursor.rowcount > 0


def build_store(kind: str, db_path: str, endpoint_url: str) -> InventoryStore:
    if kind == "sqlite":
        return SQLiteInventoryStore(db_path=db_path)
    if kind == "dynamodb":
        return DynamoInventoryStore(endpoint_url=endpoint_url)
    raise ValueError("El backend debe ser 'dynamodb' o 'sqlite'")


def main() -> None:
    parser = argparse.ArgumentParser(description="CRUD de inventario para DynamoDB compatible o SQLite fallback.")
    parser.add_argument("action", choices=["init", "put", "get", "update", "delete"])
    parser.add_argument("--backend", choices=["dynamodb", "sqlite"], default=os.getenv("INVENTORY_BACKEND", "dynamodb"))
    parser.add_argument("--endpoint-url", default=os.getenv("DYNAMODB_ENDPOINT_URL", DEFAULT_ENDPOINT_URL))
    parser.add_argument("--db-path", default=os.getenv("SQLITE_DB_PATH", "inventario.db"))
    parser.add_argument("--sku")
    parser.add_argument("--nombre")
    parser.add_argument("--precio", type=float)
    parser.add_argument("--stock", type=int)
    args = parser.parse_args()

    store = build_store(args.backend, args.db_path, args.endpoint_url)
    if args.action == "init":
        store.create_table()
        print(json.dumps({"table": TABLE_NAME, "backend": args.backend, "status": "ready"}))
        return

    if not args.sku:
        parser.error("--sku es obligatorio para operaciones CRUD")

    if args.action == "put":
        result = store.put_item({"sku": args.sku, "nombre": args.nombre, "precio": args.precio, "stock": args.stock})
    elif args.action == "get":
        result = store.get_item(args.sku)
    elif args.action == "update":
        changes = {key: value for key, value in {"nombre": args.nombre, "precio": args.precio, "stock": args.stock}.items() if value is not None}
        result = store.update_item(args.sku, changes)
    else:
        result = {"deleted": store.delete_item(args.sku)}

    print(json.dumps(_json_ready(result), ensure_ascii=False))


if __name__ == "__main__":
    main()

