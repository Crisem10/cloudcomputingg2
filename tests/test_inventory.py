from inventory import SQLiteInventoryStore


def test_positive_existing_item(tmp_path):
    store = SQLiteInventoryStore(db_path=str(tmp_path / "inventario.db"))
    store.create_table()

    store.put_item({"sku": "CAM-001", "nombre": "Camisa", "precio": 19.99, "stock": 8})

    item = store.get_item("CAM-001")
    assert item is not None
    assert item["nombre"] == "Camisa"
    assert item["stock"] == 8


def test_negative_missing_item(tmp_path):
    store = SQLiteInventoryStore(db_path=str(tmp_path / "inventario.db"))
    store.create_table()

    assert store.get_item("NO-EXISTE") is None
    assert store.update_item("NO-EXISTE", {"stock": 1}) is None
    assert store.delete_item("NO-EXISTE") is False


def test_idempotent_put_item_twice(tmp_path):
    store = SQLiteInventoryStore(db_path=str(tmp_path / "inventario.db"))
    store.create_table()
    item = {"sku": "TEC-002", "nombre": "Teclado", "precio": 35.5, "stock": 12}

    first = store.put_item(item)
    second = store.put_item(item)

    assert first["sku"] == second["sku"]
    assert store.get_item("TEC-002")["stock"] == 12


def test_complete_crud_flow(tmp_path):
    store = SQLiteInventoryStore(db_path=str(tmp_path / "inventario.db"))
    store.create_table()

    store.put_item({"sku": "MOU-003", "nombre": "Mouse", "precio": 12.0, "stock": 20})
    updated = store.update_item("MOU-003", {"stock": 15})
    deleted = store.delete_item("MOU-003")

    assert updated["stock"] == 15
    assert deleted is True
    assert store.get_item("MOU-003") is None

