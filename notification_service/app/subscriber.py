import pika
import json
import os
import time

QUEUE_NAME = os.getenv("QUEUE_NOTIFICATION", "notification")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")

def connect_to_rabbitmq(host=RABBITMQ_HOST, retries=10, delay=3):
    for attempt in range(retries):
        try:
            return pika.BlockingConnection(pika.ConnectionParameters(host=host))
        except pika.exceptions.AMQPConnectionError as e:
            print(f"[WARN] Conexión fallida a RabbitMQ. Reintentando en {delay}s...")
            time.sleep(delay)
    raise Exception("No se pudo conectar a RabbitMQ después de varios intentos.")

def callback(ch, method, properties, body):
    message = json.loads(body)
    print(f"[NOTIFY] Imagen procesada: {message['image_id']}")

def main():
    connection = connect_to_rabbitmq()
    channel = connection.channel()
    channel.exchange_declare(exchange="processed_images", exchange_type="fanout", durable=True)
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.queue_bind(exchange="processed_images", queue=QUEUE_NAME)

    print(f"[NOTIFY] Suscrito a 'processed_images' en cola '{QUEUE_NAME}'...")

    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

if __name__ == "__main__":
    main()
