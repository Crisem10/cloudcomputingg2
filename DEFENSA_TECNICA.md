# Defensa tecnica - Grupo 2

## Decision de diseno principal

Se uso `sku` como clave primaria de la tabla `inventario`.

Motivo: en un catalogo de productos, el SKU identifica de forma unica cada producto. Esto permite buscar, actualizar y eliminar items sin depender del nombre del producto, que podria repetirse o cambiar.

## Por que DynamoDB compatible

La consigna pide usar DynamoDB compatible con Floci/MiniStack. Por eso la clase `DynamoInventoryStore` crea una tabla con:

- Tabla: `inventario`
- Clave primaria: `sku`
- Tipo de clave: `S`
- Modo de cobro: `PAY_PER_REQUEST`
- Endpoint local: `http://localhost:4566`

## Por que existe fallback SQLite

La consigna permite usar SQLite si DynamoDB no esta disponible en la version instalada. El fallback mantiene el mismo esquema funcional:

- `sku TEXT PRIMARY KEY`
- `nombre TEXT NOT NULL`
- `precio REAL NOT NULL`
- `stock INTEGER NOT NULL`

Esto permite demostrar el CRUD y correr pruebas automatizadas aunque el emulador no este activo.

## Idempotencia de `put_item`

La operacion `put_item` puede ejecutarse dos veces con el mismo `sku` sin crear duplicados. Si el producto ya existe, se reemplaza/actualiza el registro. Esto cumple la prueba idempotente pedida.

## Error depurado durante la sesion

Problema: el push a GitHub por SSH fallo con:

```text
Permission denied (publickey)
```

Causa: la maquina no tenia una clave SSH autorizada para escribir en el repositorio.

Solucion: se creo una deploy key dedicada para el repositorio y se activo `Permitir acceso de escritura` en GitHub. Despues de eso, `git push` funciono correctamente.

## Como explicar el flujo CRUD

1. Crear: `put_item` inserta un producto con `sku`, `nombre`, `precio` y `stock`.
2. Leer: `get_item` consulta un producto por `sku`.
3. Actualizar: `update_item` modifica campos de un producto existente.
4. Eliminar: `delete_item` borra el producto por `sku`.

