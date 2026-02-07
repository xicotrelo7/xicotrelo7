# Netflix Clone - API Contracts

## Backend Implementation Plan

### TMDB API Integration
- **API Keys**: c8dea14dc917687ac631a52620e4f7ad, 3cb41ecea3bf606c56552db3d17adefd
- **Base URL**: https://api.themoviedb.org/3
- **Image Base URL**: https://image.tmdb.org/t/p/original

### API Endpoints to Implement

#### 1. GET /api/movies/trending
- **Purpose**: Get trending movies/series for hero banner and trending section
- **Response**: List of movies with id, title, description, backdrop, poster, rating, year, match%

#### 2. GET /api/movies/category/{category}
- **Purpose**: Get movies by category (popular, action, comedy, documentary, etc.)
- **Categories**: trending, popular, action, comedy, documentary, horror, romance
- **Response**: List of movies with id, title, poster, rating, year, match%

#### 3. GET /api/movies/search?q={query}
- **Purpose**: Search movies by title
- **Response**: List of matching movies

#### 4. GET /api/movies/{id}
- **Purpose**: Get detailed movie information including trailer
- **Response**: Full movie details + YouTube trailer URL

#### 5. GET /api/movies/{id}/trailer
- **Purpose**: Get YouTube trailer for a specific movie
- **Response**: YouTube video ID or URL

### Mock Data to Replace

**In mockData.js:**
- heroMovies → API call to /api/movies/trending (limit 3)
- trendingNow → API call to /api/movies/category/trending
- popularOnNetflix → API call to /api/movies/category/popular
- actionThrillers → API call to /api/movies/category/action
- comedies → API call to /api/movies/category/comedy
- documentaries → API call to /api/movies/category/documentary

### Frontend Integration Changes

**Files to update:**
1. **src/pages/Home.jsx** - Fetch categories from API instead of mock
2. **src/components/HeroBanner.jsx** - Fetch hero movies from API
3. **src/pages/Search.jsx** - Use API search endpoint
4. **src/pages/Watch.jsx** - Fetch movie details and trailer from API

### TMDB API Mappings

**Movie Object Mapping:**
- TMDB `id` → `id`
- TMDB `title` / `name` → `title`
- TMDB `overview` → `description`
- TMDB `backdrop_path` → `backdrop` (with image base URL)
- TMDB `poster_path` → `poster` (with image base URL)
- TMDB `vote_average` → `match` (convert 0-10 to 0-100%)
- TMDB `release_date` / `first_air_date` → `year`
- TMDB `adult` → `rating` (R/PG-13/TV-MA mapping)

### Implementation Order
1. ✅ Create backend TMDB service helper
2. ✅ Implement all API endpoints
3. ✅ Update frontend to consume APIs
4. ✅ Test all flows (browse, search, details, my list)
