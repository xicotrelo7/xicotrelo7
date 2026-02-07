from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import sys
sys.path.append('/app/backend')
from tmdb_service import (
    get_trending_movies,
    get_category_movies,
    search_movies,
    get_movie_details,
    get_movie_trailer
)

router = APIRouter(prefix="/movies", tags=["movies"])

@router.get("/trending")
async def get_trending(limit: int = Query(default=20, ge=1, le=50)):
    """Get trending movies and series"""
    try:
        movies = get_trending_movies(limit)
        return {"success": True, "data": movies}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/category/{category}")
async def get_by_category(
    category: str,
    limit: int = Query(default=20, ge=1, le=50)
):
    """Get movies by category"""
    try:
        movies = get_category_movies(category, limit)
        return {"success": True, "data": movies, "category": category}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
async def search(
    q: str = Query(..., min_length=1),
    limit: int = Query(default=20, ge=1, le=50)
):
    """Search movies and series"""
    try:
        results = search_movies(q, limit)
        return {"success": True, "data": results, "query": q, "count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{movie_id}")
async def get_movie(
    movie_id: int,
    media_type: str = Query(default="movie", regex="^(movie|tv)$")
):
    """Get detailed movie information"""
    try:
        movie = get_movie_details(movie_id, media_type)
        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")
        
        # Get trailer
        trailer = get_movie_trailer(movie_id, media_type)
        movie['trailer'] = trailer
        
        return {"success": True, "data": movie}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/categories/list")
async def list_categories():
    """List all available categories"""
    categories = [
        {"id": "trending", "name": "Trending Now"},
        {"id": "popular", "name": "Popular on Netflix"},
        {"id": "action", "name": "Action Thrillers"},
        {"id": "comedy", "name": "Comedies"},
        {"id": "documentary", "name": "Documentaries"},
        {"id": "horror", "name": "Horror Movies"},
        {"id": "romance", "name": "Romance"},
        {"id": "drama", "name": "Drama Series"}
    ]
    return {"success": True, "data": categories}
