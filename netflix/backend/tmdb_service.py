import requests
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

# TMDB API Configuration
TMDB_API_KEYS = [
    'c8dea14dc917687ac631a52620e4f7ad',
    '3cb41ecea3bf606c56552db3d17adefd'
]
CURRENT_KEY_INDEX = 0
TMDB_BASE_URL = 'https://api.themoviedb.org/3'
TMDB_IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/original'

def get_api_key():
    """Get current TMDB API key with rotation on rate limit"""
    return TMDB_API_KEYS[CURRENT_KEY_INDEX]

def rotate_api_key():
    """Rotate to next API key on rate limit"""
    global CURRENT_KEY_INDEX
    CURRENT_KEY_INDEX = (CURRENT_KEY_INDEX + 1) % len(TMDB_API_KEYS)
    logger.info(f"Rotated to API key index: {CURRENT_KEY_INDEX}")

def make_tmdb_request(endpoint: str, params: Dict = None) -> Optional[Dict]:
    """Make request to TMDB API with error handling and key rotation"""
    if params is None:
        params = {}
    
    params['api_key'] = get_api_key()
    url = f"{TMDB_BASE_URL}{endpoint}"
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 429:  # Rate limit
            rotate_api_key()
            params['api_key'] = get_api_key()
            response = requests.get(url, params=params, timeout=10)
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"TMDB API request failed: {e}")
        return None

def map_movie_to_frontend(movie: Dict, media_type: str = 'movie') -> Dict:
    """Map TMDB movie/series object to frontend format"""
    title = movie.get('title') or movie.get('name', 'Unknown')
    year = movie.get('release_date', movie.get('first_air_date', ''))
    year = year[:4] if year else '2024'
    
    # Convert vote_average (0-10) to match percentage (0-100)
    vote_avg = movie.get('vote_average', 7.0)
    match = int(vote_avg * 10)
    
    # Determine rating based on adult flag and vote
    if movie.get('adult', False):
        rating = 'R'
    elif vote_avg >= 8:
        rating = 'TV-MA'
    elif vote_avg >= 6:
        rating = 'TV-14'
    else:
        rating = 'PG-13'
    
    backdrop = movie.get('backdrop_path')
    poster = movie.get('poster_path')
    
    return {
        'id': movie.get('id'),
        'title': title,
        'description': movie.get('overview', ''),
        'backdrop': f"{TMDB_IMAGE_BASE_URL}{backdrop}" if backdrop else None,
        'poster': f"{TMDB_IMAGE_BASE_URL}{poster}" if poster else None,
        'rating': rating,
        'year': int(year),
        'match': match,
        'media_type': media_type
    }

def get_trending_movies(limit: int = 20) -> List[Dict]:
    """Get trending movies and series"""
    data = make_tmdb_request('/trending/all/week')
    if not data or 'results' not in data:
        return []
    
    movies = []
    for item in data['results'][:limit]:
        media_type = item.get('media_type', 'movie')
        movies.append(map_movie_to_frontend(item, media_type))
    
    return movies

def get_popular_movies(limit: int = 20) -> List[Dict]:
    """Get popular movies"""
    data = make_tmdb_request('/movie/popular')
    if not data or 'results' not in data:
        return []
    
    return [map_movie_to_frontend(movie, 'movie') for movie in data['results'][:limit]]

def get_movies_by_genre(genre_id: int, limit: int = 20) -> List[Dict]:
    """Get movies by genre ID"""
    params = {
        'with_genres': genre_id,
        'sort_by': 'popularity.desc'
    }
    data = make_tmdb_request('/discover/movie', params)
    if not data or 'results' not in data:
        return []
    
    return [map_movie_to_frontend(movie, 'movie') for movie in data['results'][:limit]]

def get_category_movies(category: str, limit: int = 20) -> List[Dict]:
    """Get movies by category name"""
    # TMDB Genre IDs
    genre_map = {
        'action': 28,
        'comedy': 35,
        'documentary': 99,
        'horror': 27,
        'romance': 10749,
        'thriller': 53,
        'drama': 18,
        'scifi': 878
    }
    
    if category == 'trending':
        return get_trending_movies(limit)
    elif category == 'popular':
        return get_popular_movies(limit)
    elif category in genre_map:
        return get_movies_by_genre(genre_map[category], limit)
    else:
        return get_popular_movies(limit)

def search_movies(query: str, limit: int = 20) -> List[Dict]:
    """Search movies and series by query"""
    params = {'query': query}
    data = make_tmdb_request('/search/multi', params)
    if not data or 'results' not in data:
        return []
    
    results = []
    for item in data['results'][:limit]:
        if item.get('media_type') in ['movie', 'tv']:
            results.append(map_movie_to_frontend(item, item.get('media_type')))
    
    return results

def get_movie_details(movie_id: int, media_type: str = 'movie') -> Optional[Dict]:
    """Get detailed movie information"""
    endpoint = f'/{media_type}/{movie_id}'
    data = make_tmdb_request(endpoint)
    if not data:
        return None
    
    movie = map_movie_to_frontend(data, media_type)
    
    # Add additional details
    if media_type == 'tv':
        movie['seasons'] = data.get('number_of_seasons', 0)
    else:
        runtime = data.get('runtime', 0)
        if runtime:
            hours = runtime // 60
            minutes = runtime % 60
            movie['duration'] = f"{hours}h {minutes}m"
    
    # Get genres
    genres = data.get('genres', [])
    movie['genres'] = [g['name'] for g in genres]
    
    return movie

def get_movie_trailer(movie_id: int, media_type: str = 'movie') -> Optional[str]:
    """Get YouTube trailer URL for a movie"""
    endpoint = f'/{media_type}/{movie_id}/videos'
    data = make_tmdb_request(endpoint)
    if not data or 'results' not in data:
        return None
    
    # Find YouTube trailer
    for video in data['results']:
        if video.get('site') == 'YouTube' and video.get('type') in ['Trailer', 'Teaser']:
            video_key = video.get('key')
            if video_key:
                return f"https://www.youtube.com/watch?v={video_key}"
    
    return None
