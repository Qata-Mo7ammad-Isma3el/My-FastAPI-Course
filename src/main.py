from fastapi import FastAPI
from src.books.routes import book_router
from src.auth.routes import auth_router
from contextlib import asynccontextmanager
from src.db.main import init_db

#NOTE to create database using sql shell write the following command
#> CREATE DATABASE bookly_db;
#! always use acyncpg with postgresql for async operations

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")
    await init_db()
    yield
    print("Shutting down...")

version='v1'
app = FastAPI(
    version=version,
    title="Book Management API",
    description="An API to manage books using FastAPI routers",
    #//lifespan=lifespan
)

app.include_router(book_router,prefix=f"/api/{version}/books",tags=["Books"]) 
app.include_router(auth_router,prefix=f"/api/{version}/auth",tags=["Authentication"])