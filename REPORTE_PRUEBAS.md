# Reporte de pruebas - Grupo 2

## Comando ejecutado

```bash
python -m pytest -q
```

## Salida obtenida

```text
....                                                                     [100%]
4 passed in 0.06s
```

## Evidencia por requisito

| Requisito | Prueba | Archivo |
| --- | --- | --- |
| Prueba positiva: item existente | `test_positive_existing_item` | `tests/test_inventory.py` |
| Prueba negativa: item inexistente | `test_negative_missing_item` | `tests/test_inventory.py` |
| Prueba idempotente: `put_item` dos veces | `test_idempotent_put_item_twice` | `tests/test_inventory.py` |
| CRUD completo | `test_complete_crud_flow` | `tests/test_inventory.py` |

## Interpretacion

La salida `4 passed` confirma que las operaciones requeridas funcionan correctamente usando el fallback SQLite. El mismo contrato de metodos se mantiene para DynamoDB compatible mediante `DynamoInventoryStore`.

## Prueba negativa con AWS CLI

Cuando DynamoDB compatible este activo en `http://localhost:4566`, la prueba negativa solicitada por la consigna se puede ejecutar con:

```bash
aws dynamodb get-item \
  --table-name inventario \
  --key '{"sku":{"S":"NO-EXISTE"}}' \
  --endpoint-url http://localhost:4566
```

Respuesta esperada: no debe devolver `Item`, porque el SKU `NO-EXISTE` no esta registrado.

