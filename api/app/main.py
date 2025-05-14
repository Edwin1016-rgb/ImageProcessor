from http.client import HTTPException
import os
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from .models import UploadResponse, StatusResponse
from .services import publish_event, save_image_locally, send_to_queue
from .utils import generate_image_id

app = FastAPI()
fake_db = {}

@app.post("/upload", response_model=UploadResponse)
async def upload_image(file: UploadFile = File(...)):
    image_id = generate_image_id()
    save_image_locally(file, image_id)
    fake_db[image_id] = {"status": "uploaded", "metadata": {}}
    for stage in ["resize", "watermark", "detect"]:
        send_to_queue(image_id, stage)
    fake_db[image_id]["status"] = "processing"
    return UploadResponse(image_id=image_id, status="processing")

@app.get("/status/{image_id}", response_model=StatusResponse)
def get_status(image_id: str):
    status_file = f"/shared/status/{image_id}.txt"
    if not os.path.exists(status_file):
        raise HTTPException(status_code=404, detail="Image not found")

    with open(status_file, "r") as f:
        lines = f.readlines()

    stages = {line.strip().split(":")[0]: line.strip().split(":")[1] for line in lines}
    expected_stages = ["resize", "watermark", "detect"]

    if all(stage in stages for stage in expected_stages):
        publish_event(image_id)
        return {
            "image_id": image_id,
            "status": "complete",
            "metadata": stages
        }
    else:
        return {
            "image_id": image_id,
            "status": "processing",
            "metadata": stages
        }