# Registro de prompts - Grupo 2

## 1. Prompt inicial

Actua como asistente de desarrollo para una practica de computacion en la nube. Lee la consigna del PDF y extrae solamente lo que corresponde al Grupo 2. Identifica servicios, producto minimo, pruebas obligatorias y entregables.

Resultado esperado: confirmar que el Grupo 2 debe implementar un inventario NoSQL con DynamoDB compatible, operaciones CRUD completas y pruebas positiva, negativa e idempotente.

## 3. Prompt de diseno tecnico

Disena una solucion sencilla para una tienda en linea que necesita gestionar productos por `sku`. La solucion debe funcionar con DynamoDB compatible en `http://localhost:4566`, pero tambien debe tener un fallback con SQLite si DynamoDB o MiniStack/Floci no estan disponibles.

Incluye:

- Tabla `inventario` con clave primaria `sku`.
- Operaciones crear, leer, actualizar y eliminar.
- Validacion de campos `sku`, `nombre`, `precio` y `stock`.
- Separacion entre logica de almacenamiento y comandos de consola.

## 4. Prompt de pruebas

Crea pruebas automatizadas con `pytest` para validar:

- Caso positivo: se inserta un producto y luego se consulta por `sku`.
- Caso negativo: se consulta, actualiza y elimina un producto inexistente.
- Caso idempotente: ejecutar `put_item` dos veces con el mismo `sku` no duplica datos ni produce error.
- Flujo CRUD completo: crear, actualizar, eliminar y verificar que ya no existe.

## 5. Prompt de depuracion

Al intentar subir el repositorio por SSH aparece `Permission denied (publickey)`. Diagnostica la causa y propone una solucion segura para GitHub.

Solucion aplicada: se genero una clave SSH dedicada como deploy key del repositorio y se activo permiso de escritura para poder hacer `git push`.

## 6. Prompt de mejora visual

El entregable funciona por consola, pero se necesita algo visual para presentarlo. Crea una interfaz web estatica que permita demostrar el inventario con formulario, tabla, acciones de editar/eliminar, metricas y evidencia de pruebas.

Condiciones:

- Debe abrirse directamente desde `index.html`.
- No debe requerir backend para la demostracion visual.
- Puede usar `localStorage` para persistencia del navegador.
- Debe mostrar la salida de pruebas y los criterios cubiertos.

## 7. Revision critica

Verifica que el repositorio tenga codigo, README, pruebas automatizadas, reporte visible de pruebas, registro de prompts y una explicacion clara para defensa tecnica.

Decision principal para defender: `sku` es la clave primaria porque identifica cada producto de forma unica. `put_item` es idempotente porque repetir el mismo `sku` actualiza el item sin duplicarlo. SQLite se usa como fallback para demostrar la practica aunque el emulador DynamoDB no este disponible.

## 8. Prompt de cierre

Revisa que se cumplan todos los entregables obligatorios:

- Repositorio Git con codigo.
- README con decisiones tecnicas y reproduccion del entorno.
- Reporte de pruebas con salida de `pytest`.
- Defensa tecnica con una decision de diseno y un error depurado.
- Archivo `prompts.md` con prompt inicial, revision critica y prompt de depuracion.
