from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
import os
import uuid
import shutil
from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

# Load environment variables
load_dotenv()

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL', '')
db_name = os.environ.get('DB_NAME', 'netflix_clone')
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]

router = APIRouter(prefix="/custom-videos", tags=["custom-videos"])

# Upload directory
UPLOAD_DIR = Path("/app/backend/uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/upload")
async def upload_video(
    title: str = Form(...),
    description: str = Form(...),
    category: str = Form("My Videos"),
    year: int = Form(2024),
    rating: str = Form("TV-14"),
    match: int = Form(90),
    video: UploadFile = File(...),
    thumbnail: Optional[UploadFile] = File(None)
):
    """Upload custom video with metadata"""
    try:
        video_id = str(uuid.uuid4())
        
        # Save video file
        video_ext = os.path.splitext(video.filename)[1]
        video_filename = f"{video_id}{video_ext}"
        video_path = UPLOAD_DIR / video_filename
        
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(video.file, buffer)
        
        # Save thumbnail if provided
        thumbnail_filename = None
        if thumbnail:
            thumb_ext = os.path.splitext(thumbnail.filename)[1]
            thumbnail_filename = f"{video_id}_thumb{thumb_ext}"
            thumb_path = UPLOAD_DIR / thumbnail_filename
            
            with open(thumb_path, "wb") as buffer:
                shutil.copyfileobj(thumbnail.file, buffer)
        
        # Save metadata to MongoDB
        video_doc = {
            "id": video_id,
            "title": title,
            "description": description,
            "video_path": str(video_filename),
            "thumbnail_path": str(thumbnail_filename) if thumbnail_filename else None,
            "category": category,
            "year": year,
            "rating": rating,
            "match": match,
            "media_type": "custom"
        }
        
        await db.custom_videos.insert_one(video_doc)
        
        return {
            "success": True,
            "message": "Video uploaded successfully",
            "video_id": video_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list")
async def list_custom_videos():
    """Get all custom uploaded videos"""
    try:
        videos = await db.custom_videos.find().to_list(100)
        
        # Format videos for frontend
        formatted_videos = []
        for video in videos:
            formatted_videos.append({
                "id": video["id"],
                "title": video["title"],
                "description": video["description"],
                "poster": f"/api/custom-videos/thumbnail/{video['thumbnail_path']}" if video.get('thumbnail_path') else None,
                "backdrop": f"/api/custom-videos/thumbnail/{video['thumbnail_path']}" if video.get('thumbnail_path') else None,
                "category": video.get("category", "My Videos"),
                "year": video.get("year", 2024),
                "rating": video.get("rating", "TV-14"),
                "match": video.get("match", 90),
                "media_type": "custom",
                "video_url": f"/api/custom-videos/stream/{video['video_path']}"
            })
        
        return {"success": True, "data": formatted_videos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stream/{filename}")
async def stream_video(filename: str):
    """Stream video file"""
    file_path = UPLOAD_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Video not found")
    
    return FileResponse(file_path, media_type="video/mp4")

@router.get("/thumbnail/{filename}")
async def get_thumbnail(filename: str):
    """Get thumbnail image"""
    if not filename or filename == "None":
        raise HTTPException(status_code=404, detail="Thumbnail not found")
    
    file_path = UPLOAD_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Thumbnail not found")
    
    return FileResponse(file_path)

@router.get("/{video_id}")
async def get_custom_video(video_id: str):
    """Get custom video details"""
    try:
        video = await db.custom_videos.find_one({"id": video_id})
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        return {
            "success": True,
            "data": {
                "id": video["id"],
                "title": video["title"],
                "description": video["description"],
                "poster": f"/api/custom-videos/thumbnail/{video['thumbnail_path']}" if video.get('thumbnail_path') else None,
                "backdrop": f"/api/custom-videos/thumbnail/{video['thumbnail_path']}" if video.get('thumbnail_path') else None,
                "category": video.get("category", "My Videos"),
                "year": video.get("year", 2024),
                "rating": video.get("rating", "TV-14"),
                "match": video.get("match", 90),
                "media_type": "custom",
                "video_url": f"/api/custom-videos/stream/{video['video_path']}",
                "genres": [video.get("category", "My Videos")]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{video_id}")
async def delete_custom_video(video_id: str):
    """Delete custom video"""
    try:
        video = await db.custom_videos.find_one({"id": video_id})
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        # Delete files
        video_path = UPLOAD_DIR / video["video_path"]
        if video_path.exists():
            os.remove(video_path)
        
        if video.get("thumbnail_path"):
            thumb_path = UPLOAD_DIR / video["thumbnail_path"]
            if thumb_path.exists():
                os.remove(thumb_path)
        
        # Delete from database
        await db.custom_videos.delete_one({"id": video_id})
        
        return {"success": True, "message": "Video deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
