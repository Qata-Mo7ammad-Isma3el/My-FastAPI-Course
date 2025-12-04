from fastapi import FastAPI, status, Depends
from src.books.routes import book_router
from src.auth.routes import auth_router
from src.reviews.routes import Reviews_router
from src.tags.routes import tags_router
from contextlib import asynccontextmanager
from src.db.main import init_db
from src.errors import register_all_errors
from src.middleware import register_middleware
from src.db.main import check_db_health
from src.db.redis import RedisClient, get_redis
from datetime import datetime, timezone
from src.config import settings
import importlib.metadata

# NOTE to create database using sql shell write the following command
# > CREATE DATABASE bookly_db;
#! always use acyncpg with postgresql for async operations
# main.py
openapi_tags = [
    {
        "name": "Authentication",
        "description": "User registration, login, token management",
    },
    {
        "name": "Books",
        "description": "Create, read, update, and delete books",
    },
    {
        "name": "Reviews",
        "description": "Book reviews and ratings",
    },
    {
        "name": "Tags",
        "description": "Tag management for books",
    },
    {
        "name": "Health",
        "description": "API health checks",
    },
]

description = """
    # Book Management API
    
    ## Features
    - 🔐 **JWT-based authentication** with token refresh
    - 📚 **Book management** (Create, Read, Update, Delete)
    - ⭐ **Book reviews and ratings** system
    - 🏷️ **Tag system** for organizing books
    - 👥 **User roles** (admin/user) with role-based access control
    - 🔄 **Refresh token rotation** for enhanced security
    - 🚫 **Token revocation** (logout) functionality
    
    ## Authentication Flow
    
    Most endpoints require authentication using Bearer tokens.
    
    1. **Register**: `POST /api/v1/auth/signup`
    2. **Login**: `POST /api/v1/auth/login` - Get access and refresh tokens
    3. **Use Access Token**: Include in Authorization header: `Bearer <access_token>`
    4. **Refresh Token**: `GET /api/v1/auth/refresh_token` when access token expires
    5. **Logout**: `POST /api/v1/auth/logout` to revoke tokens
    6. **Get Profile**: `GET /api/v1/auth/me` to get current user info
    
    ## API Endpoints
    
    ### Authentication (`/api/v1/auth`)
    - `POST /signup` - Register new user
    - `POST /login` - Login and get tokens
    - `GET /refresh_token` - Refresh access token
    - `POST /logout` - Revoke token
    - `GET /me` - Get current user profile
    
    ### Books (`/api/v1/books`)
    - `GET /` - Get all books
    - `GET /{book_uid}` - Get specific book with reviews and tags
    - `GET /user/{user_uid}` - Get user's books
    - `POST /` - Create new book
    - `PATCH /{book_uid}` - Update book
    - `DELETE /{book_uid}` - Delete book
    
    ### Reviews (`/api/v1/reviews`)
    - `GET /` - Get all reviews
    - `GET /{review_uid}` - Get specific review
    - `POST /book/{book_uid}` - Add review to book
    - `PATCH /{review_uid}` - Update review
    - `DELETE /{review_uid}` - Delete review
    
    ### Tags (`/api/v1/tags`)
    - `GET /` - Get all tags
    - `POST /` - Create new tag
    - `POST /book/{book_uid}/tags` - Add tags to book
    - `PUT /{tag_uid}` - Update tag
    - `DELETE /{tag_uid}` - Delete tag
    
    ## Error Responses
    
    All errors follow this format:
    ```json
    {
      "detail": {
        "message": "Error description",
        "error_code": "specific_error_code",
        "resolution": "How to fix it"
      }
    }
    ```
    
    ## Getting Started
    
    1. Register a new user account
    2. Login to get your tokens
    3. Use the access token for authenticated requests
    4. Refresh token when it expires (1 hour by default)
    5. Logout when done to revoke tokens
    """


# main.py
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan with proper startup/shutdown"""
    from src.db.redis import redis_client

    # Startup
    print(
        f"Starting {settings.PROJECT_NAME} v{__version__} in {settings.ENVIRONMENT} mode..."
    )

    try:
        # Initialize database
        await init_db()
        print("✓ Database initialized")

        # Connect to Redis
        await redis_client.connect()
        print("✓ Redis connected")

        yield

    except Exception as e:
        print(f"✗ Startup failed: {e}")
        raise

    finally:
        # Shutdown
        print("Shutting down...")
        await redis_client.disconnect()
        print("✓ Redis disconnected")


try:
    __version__ = importlib.metadata.version("bookly")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.1.0"

version = "v1"

app = FastAPI(
    version=__version__,  # Use package version
    title=settings.PROJECT_NAME,
    # description=description,
    lifespan=lifespan,
    openapi_url=(
        f"{settings.API_PREFIX}/openapi.json" if not settings.DEBUG else "/openapi.json"
    ),
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    contact={
        "name": "API Support",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    servers=[{"url": "http://localhost:8000", "description": "Development server"}],
    openapi_tags=openapi_tags,
)

## Adding exception handlers
register_all_errors(app)

## Middleware registration
register_middleware(app)

# main.py - Use settings
app.include_router(book_router, prefix=f"{settings.API_PREFIX}/books", tags=["Books"])
app.include_router(
    auth_router, prefix=f"{settings.API_PREFIX}/auth", tags=["Authentication"]
)
app.include_router(
    Reviews_router, prefix=f"{settings.API_PREFIX}/reviews", tags=["Reviews"]
)
app.include_router(tags_router, prefix=f"{settings.API_PREFIX}/tags", tags=["Tags"])


@app.get("/", include_in_schema=False)
async def root():
    return {
        "message": "Book Management API",
        "version": version,
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health", tags=["Health"])
async def health_check(redis_client: RedisClient = Depends(get_redis)):
    """Health check endpoint for monitoring"""

    db_health = await check_db_health()
    redis_health = await redis_client.ping()

    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "services": {
            "database": db_health,
            "redis": "connected" if redis_health else "disconnected",
            "api": "running",
        },
        "version": version,
    }
