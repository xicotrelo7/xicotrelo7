import requests
import json
import sys
import os

# Get backend URL from frontend env (as per instructions)
backend_base_url = "https://streambox-129.preview.emergentagent.com/api"

print("=== Netflix Clone Backend API Testing ===")
print(f"Testing against: {backend_base_url}")
print()

def test_endpoint(method, endpoint, expected_status=200, params=None, description=""):
    """Test an API endpoint and return response data"""
    url = f"{backend_base_url}{endpoint}"
    
    print(f"🔍 Testing: {method} {endpoint}")
    if description:
        print(f"   Description: {description}")
    
    try:
        if method == "GET":
            response = requests.get(url, params=params, timeout=30)
        else:
            response = requests.request(method, url, params=params, timeout=30)
            
        print(f"   Status: {response.status_code}")
        
        if response.status_code == expected_status:
            print("   ✅ Status code matches expected")
        else:
            print(f"   ❌ Expected {expected_status}, got {response.status_code}")
            
        # Try to parse JSON response
        try:
            data = response.json()
            print(f"   Response size: {len(json.dumps(data))} characters")
            return response.status_code, data
        except:
            print("   ⚠️  Response is not valid JSON")
            print(f"   Raw response: {response.text[:200]}")
            return response.status_code, response.text
            
    except requests.exceptions.Timeout:
        print("   ❌ Request timed out")
        return None, "Timeout"
    except requests.exceptions.ConnectionError:
        print("   ❌ Connection error")
        return None, "Connection Error"
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return None, str(e)

def validate_movie_structure(movie, required_fields):
    """Validate that a movie object has required fields"""
    missing_fields = []
    for field in required_fields:
        if field not in movie:
            missing_fields.append(field)
    return missing_fields

def main():
    print("Starting Netflix Clone Backend API Tests...")
    print("=" * 60)
    
    # Test 1: Basic health check
    print("\n1. Testing basic health check endpoint")
    status, data = test_endpoint("GET", "/", 
                                description="Basic health check endpoint")
    
    if status == 200 and isinstance(data, dict):
        print("   ✅ Health check endpoint working")
    else:
        print("   ❌ Health check endpoint failed")
    
    print("-" * 40)
    
    # Test 2: Get trending movies
    print("\n2. Testing GET /api/movies/trending")
    status, data = test_endpoint("GET", "/movies/trending",
                                description="Should return list of trending movies from TMDB")
    
    if status == 200 and isinstance(data, dict):
        if data.get('success') == True:
            print("   ✅ Response has success: true")
        else:
            print("   ❌ Response missing success: true")
            
        if 'data' in data and isinstance(data['data'], list):
            print(f"   ✅ Data array present with {len(data['data'])} movies")
            
            # Validate movie structure
            if len(data['data']) > 0:
                movie = data['data'][0]
                required_fields = ['id', 'title', 'description', 'backdrop', 'poster', 'rating', 'year', 'match', 'media_type']
                missing_fields = validate_movie_structure(movie, required_fields)
                
                if not missing_fields:
                    print("   ✅ Movie objects have all required fields")
                else:
                    print(f"   ❌ Movie objects missing fields: {missing_fields}")
                    
                # Check specific field values
                print(f"   Sample movie: {movie.get('title', 'No title')}")
                print(f"   Match percentage: {movie.get('match', 'Missing')}")
                print(f"   Media type: {movie.get('media_type', 'Missing')}")
        else:
            print("   ❌ Response missing data array")
    else:
        print(f"   ❌ Trending movies endpoint failed")
    
    print("-" * 40)
    
    # Test 3: Get popular movies
    print("\n3. Testing GET /api/movies/category/popular")
    status, data = test_endpoint("GET", "/movies/category/popular",
                                description="Should return popular movies")
    
    if status == 200 and isinstance(data, dict):
        if data.get('success') == True:
            print("   ✅ Popular movies endpoint working")
            print(f"   Category: {data.get('category', 'Missing')}")
            
            if 'data' in data and len(data['data']) > 0:
                print(f"   ✅ Returned {len(data['data'])} popular movies")
            else:
                print("   ❌ No popular movies returned")
        else:
            print("   ❌ Popular movies response invalid")
    else:
        print("   ❌ Popular movies endpoint failed")
    
    print("-" * 40)
    
    # Test 4: Get action movies
    print("\n4. Testing GET /api/movies/category/action")
    status, data = test_endpoint("GET", "/movies/category/action",
                                description="Should return action movies")
    
    if status == 200 and isinstance(data, dict):
        if data.get('success') == True and 'data' in data:
            print("   ✅ Action movies endpoint working")
            print(f"   ✅ Returned {len(data['data'])} action movies")
        else:
            print("   ❌ Action movies response invalid")
    else:
        print("   ❌ Action movies endpoint failed")
    
    print("-" * 40)
    
    # Test 5: Search for Avengers movies
    print("\n5. Testing GET /api/movies/search?q=Avengers")
    status, data = test_endpoint("GET", "/movies/search", 
                                params={"q": "Avengers"},
                                description="Should search and return Avengers movies")
    
    if status == 200 and isinstance(data, dict):
        if data.get('success') == True:
            print("   ✅ Search endpoint working")
            print(f"   Query: {data.get('query', 'Missing')}")
            print(f"   Count: {data.get('count', 'Missing')}")
            
            if 'data' in data:
                search_results = data['data']
                if len(search_results) > 0:
                    print(f"   ✅ Found {len(search_results)} movies")
                    
                    # Check if results are relevant
                    avengers_found = False
                    for movie in search_results:
                        if 'avengers' in movie.get('title', '').lower():
                            avengers_found = True
                            print(f"   ✅ Found relevant result: {movie.get('title')}")
                            break
                    
                    if not avengers_found:
                        print("   ⚠️  No movies with 'Avengers' in title found")
                        
                    # Verify count field matches results
                    if data.get('count') == len(search_results):
                        print("   ✅ Count field matches results length")
                    else:
                        print("   ❌ Count field doesn't match results")
                else:
                    print("   ⚠️  No search results returned")
            else:
                print("   ❌ Search response missing data field")
        else:
            print("   ❌ Search response invalid")
    else:
        print("   ❌ Search endpoint failed")
    
    print("-" * 40)
    
    # Test 6: Get specific movie details (Shawshank Redemption)
    print("\n6. Testing GET /api/movies/278?media_type=movie")
    status, data = test_endpoint("GET", "/movies/278", 
                                params={"media_type": "movie"},
                                description="Get specific movie details (Shawshank Redemption ID: 278)")
    
    if status == 200 and isinstance(data, dict):
        if data.get('success') == True and 'data' in data:
            movie_data = data['data']
            print("   ✅ Movie details endpoint working")
            print(f"   Movie title: {movie_data.get('title', 'Missing')}")
            
            # Check for detailed info
            if 'genres' in movie_data:
                print(f"   ✅ Genres included: {movie_data.get('genres')}")
            else:
                print("   ❌ Genres missing from movie details")
                
            if 'trailer' in movie_data:
                trailer_url = movie_data.get('trailer')
                if trailer_url and 'youtube.com' in str(trailer_url):
                    print(f"   ✅ YouTube trailer URL: {trailer_url}")
                elif trailer_url is None:
                    print("   ⚠️  No trailer available for this movie")
                else:
                    print(f"   ❌ Invalid trailer URL: {trailer_url}")
            else:
                print("   ❌ Trailer field missing from response")
        else:
            print("   ❌ Movie details response invalid")
    else:
        print(f"   ❌ Movie details endpoint failed")
    
    print("-" * 40)
    
    # Test 7: Test image URL format
    print("\n7. Validating TMDB image URLs")
    status, data = test_endpoint("GET", "/movies/trending")
    
    if status == 200 and isinstance(data, dict) and 'data' in data and len(data['data']) > 0:
        movie = data['data'][0]
        backdrop = movie.get('backdrop')
        poster = movie.get('poster')
        
        if backdrop and 'image.tmdb.org' in backdrop:
            print("   ✅ Backdrop URL uses TMDB image base URL")
        else:
            print(f"   ❌ Invalid backdrop URL: {backdrop}")
            
        if poster and 'image.tmdb.org' in poster:
            print("   ✅ Poster URL uses TMDB image base URL")  
        else:
            print(f"   ❌ Invalid poster URL: {poster}")
            
        # Validate match percentage calculation
        match_percentage = movie.get('match')
        if isinstance(match_percentage, int) and 0 <= match_percentage <= 100:
            print(f"   ✅ Match percentage valid: {match_percentage}%")
        else:
            print(f"   ❌ Invalid match percentage: {match_percentage}")
    else:
        print("   ❌ Cannot validate image URLs - no movie data available")
    
    print("\n" + "=" * 60)
    print("Netflix Clone Backend API Testing Complete")
    
if __name__ == "__main__":
    main()