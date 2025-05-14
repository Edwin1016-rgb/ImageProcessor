import os
import time
import pika
import json

QUEUE_NAME = os.getenv("QUEUE_WATERMARK", "watermark")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")

def connect_to_rabbitmq(host=RABBITMQ_HOST, retries=10, delay=3):
    for attempt in range(retries):
        try:
            return pika.BlockingConnection(pika.ConnectionParameters(host=host))
        except pika.exceptions.AMQPConnectionError as e:
            print(f"[WARN] Conexión fallida a RabbitMQ. Reintentando en {delay}s...")
            time.sleep(delay)
    raise Exception("No se pudo conectar a RabbitMQ después de varios intentos.")

def process_image(image_id):
    print(f"[Watermark] Procesando imagen: {image_id}")
    time.sleep(2)
    update_status(image_id, "watermarked")

def update_status(image_id, new_status):
    status_file = f"/shared/status/{image_id}.txt"
    with open(status_file, "a") as f:
        f.write(f"watermark:{new_status}\n")
    print(f"[Watermark] Estado actualizado para {image_id}: {new_status}")

def callback(ch, method, properties, body):
    data = json.loads(body)
    image_id = data["image_id"]
    process_image(image_id)
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    print("[Watermark] Conectando a RabbitMQ...")
    connection = connect_to_rabbitmq()
    print("[Watermark] Conexión exitosa a RabbitMQ.")
    channel = connection.channel()

    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)

    print(f"[Watermark] Esperando mensajes en la cola '{QUEUE_NAME}'...")
    channel.start_consuming()

if __name__ == "__main__":
    main()
    