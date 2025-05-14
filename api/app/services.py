import os
import shutil
import pika
import json
from fastapi import UploadFile
from .utils import generate_image_id


UPLOAD_FOLDER = "uploaded_images"

def save_image_locally(file: UploadFile, image_id: str) -> str:
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    file_path = os.path.join(UPLOAD_FOLDER, f"{image_id}.jpg")
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return file_path

def send_to_queue(image_id: str, stage: str):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
    channel = connection.channel()

    channel.queue_declare(queue=stage, durable=True)
    message = json.dumps({"image_id": image_id})
    channel.basic_publish(
        exchange="",
        routing_key=stage,
        body=message,
        properties=pika.BasicProperties(delivery_mode=2)
    )
    connection.close()
    
def publish_event(image_id: str):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
    channel = connection.channel()

    channel.exchange_declare(exchange="processed_images", exchange_type="fanout", durable=True)

    message = json.dumps({
        "image_id": image_id,
        "status": "complete"
    })

    channel.basic_publish(
        exchange="processed_images",
        routing_key="",
        body=message,
        properties=pika.BasicProperties(delivery_mode=2)
    )
    connection.close()
    print(f"[API] Imagen {image_id} publicada en 'processed_images'")