from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ComplaintCreate(BaseModel):
    title: str
    description: str
    latitude: float
    longitude: float
    category: str = "Pothole"
    reported_by: str = "Anonymous"

class ComplaintUpdate(BaseModel):
    status: str
    admin_notes: Optional[str] = None

class ComplaintResponse(BaseModel):
    id: str
    title: str
    description: str
    latitude: float
    longitude: float
    photo_url: Optional[str]
    status: str
    category: str
    reported_at: datetime
    priority: int