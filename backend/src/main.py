# src/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routers import router

app = FastAPI(
    title="Pi Calculation Service",
    description="A real-time Pi digit calculation service with streaming updates",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# --- CORS Configuration ---
# If your React app is running locally, it's typically http://localhost:3000
origins = [
    "http://localhost:3000",  # React development server
    "http://127.0.0.1:3000",
]

# 3. Add the CORSMiddleware to the application
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,             # List of origins permitted to make requests
    allow_credentials=True,            # Allow cookies to be sent (if needed)
    allow_methods=["*"],               # Allow all standard methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],               # Allow all request headers
)
# --- End CORS Configuration ---

app.include_router(router)