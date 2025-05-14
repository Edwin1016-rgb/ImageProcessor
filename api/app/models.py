from pydantic import BaseModel
from typing import Optional, Dict

class UploadResponse(BaseModel):
    image_id: str
    status: str

class StatusResponse(BaseModel):
    image_id: str
    status: str
    metadata: Optional[Dict[str, str]] = None
