from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class CustomVideo(BaseModel):
    id: str
    title: str
    description: str
    video_path: str
    thumbnail_path: Optional[str] = None
    category: str = 'custom'
    year: int = 2024
    rating: str = 'TV-14'
    match: int = 90
    duration: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CustomVideoCreate(BaseModel):
    title: str
    description: str
    category: str = 'custom'
    year: int = 2024
    rating: str = 'TV-14'
    match: int = 90
