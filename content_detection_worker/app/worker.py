import os
import time
import pika
import json

QUEUE_NAME = os.getenv("QUEUE_DETECT", "detect")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")

def connect_to_rabbitmq(host=RABBITMQ_HOST, retries=10, delay=10):
    for attempt in range(retries):
        try:
            return pika.BlockingConnection(pika.ConnectionParameters(host=host))
        except pika.exceptions.AMQPConnectionError as e:
            print(f"[WARN] Conexión fallida a RabbitMQ. Reintentando en {delay}s...")
            time.sleep(delay)
    raise Exception("No se pudo conectar a RabbitMQ después de varios intentos.")

def process_image(image_id):
    print(f"[Detect] Procesando imagen: {image_id}")
    time.sleep(2)  # Simula tiempo de procesamiento
    update_status(image_id, "shi")

def update_status(image_id, new_status):
    status_file = f"/shared/status/{image_id}.txt"
    with open(status_file, "a") as f:
        f.write(f"detect:{new_status}\n")
    print(f"[Detect] Estado actualizado para {image_id}: {new_status}")

def callback(ch, method, properties, body):
    data = json.loads(body)
    image_id = data["image_id"]
    process_image(image_id)
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    print("[Detect] Conectando a RabbitMQ...")
    connection = connect_to_rabbitmq()
    print("[Detect] Conexión exitosa a RabbitMQ.")
    channel = connection.channel()

    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)

    print(f"[Detect] Esperando mensajes en la cola '{QUEUE_NAME}'...")
    channel.start_consuming()

if __name__ == "__main__":
    main()
