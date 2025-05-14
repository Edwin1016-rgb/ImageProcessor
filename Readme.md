# Como levantar el proyecto
git clone https://github.com/Edwin1016-rgb/ImageProcessor

# como ejecutar
docker-compose up --build

## Accede a la API:
   - Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
   - RabbitMQ dashboard: [http://localhost:15672](http://localhost:15672)
     - Usuario: `guest`
     - Contraseña: `guest`

##  Endpoints disponibles

### POST `/upload`
Envía una imagen para ser procesada.
```json
Response:
{
  "image_id": "uuid",
  "status": "processing"
}
```

### GET `/status/{image_id}`
Devuelve el estado de procesamiento de la imagen.
```json
{
  "image_id": "uuid",
  "status": "processing" | "completed",
  "metadata": {}
}
```
## Consideraciones

- RabbitMQ puede tardar unos segundos en estar disponible. Todos los workers usan reintentos automáticos para conectarse.
- Las imágenes se guardan en `/shared/images/` y los estados en `/shared/status/`.