# Inventario NoSQL con DynamoDB compatible - Grupo 2

Actividad 14: CRUD de inventario para una tienda en línea.

## Objetivo

Crear una tabla `inventario` con llave primaria `sku`, implementar operaciones CRUD completas y validar:

- Prueba positiva: consultar un ítem existente.
- Prueba negativa: consultar/modificar/eliminar un ítem inexistente.
- Prueba idempotente: ejecutar `put_item` dos veces con el mismo `sku`.

## Estructura

- `inventory.py`: script CLI y clases de acceso a datos.
- `tests/test_inventory.py`: pruebas automatizadas con `pytest`.
- `requirements.txt`: dependencias para DynamoDB compatible y pruebas.
- `prompts.md`: registro de prompts usado en la solución.

## Backend principal: DynamoDB compatible

El script usa por defecto un endpoint compatible con DynamoDB en `http://localhost:4566`, como Floci/MiniStack o un emulador equivalente.

```bash
pip install -r requirements.txt
python inventory.py init --backend dynamodb --endpoint-url http://localhost:4566
python inventory.py put --backend dynamodb --sku CAM-001 --nombre Camisa --precio 19.99 --stock 8
python inventory.py get --backend dynamodb --sku CAM-001
python inventory.py update --backend dynamodb --sku CAM-001 --stock 6
python inventory.py delete --backend dynamodb --sku CAM-001
```

Comando AWS CLI equivalente para crear la tabla:

```bash
aws dynamodb create-table \
  --table-name inventario \
  --attribute-definitions AttributeName=sku,AttributeType=S \
  --key-schema AttributeName=sku,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --endpoint-url http://localhost:4566
```

Prueba negativa solicitada:

```bash
aws dynamodb get-item \
  --table-name inventario \
  --key '{"sku":{"S":"NO-EXISTE"}}' \
  --endpoint-url http://localhost:4566
```

## Fallback: SQLite

Si DynamoDB compatible no está disponible, se usa SQLite con un esquema equivalente.

```bash
python inventory.py init --backend sqlite --db-path inventario.db
python inventory.py put --backend sqlite --sku TEC-002 --nombre Teclado --precio 35.50 --stock 12
python inventory.py get --backend sqlite --sku TEC-002
```

## Ejecutar pruebas

```bash
pip install -r requirements.txt
pytest -q
```

Salida esperada:

```text
4 passed
```

## Decisiones técnicas

- `sku` es la clave primaria porque identifica de forma única cada producto.
- `put_item` se implementa como operación idempotente: repetir el mismo `sku` actualiza el registro sin duplicarlo.
- Se separó la lógica de almacenamiento en dos clases: `DynamoInventoryStore` y `SQLiteInventoryStore`.
- Las pruebas usan SQLite para poder ejecutarse aun cuando el emulador DynamoDB no esté activo.

## Error depurado durante la sesión

Al leer el PDF, la consola de Windows no pudo imprimir algunos caracteres Unicode. Se corrigió forzando la salida de Python a UTF-8 para extraer correctamente las instrucciones.

