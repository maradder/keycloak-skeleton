import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, admin, health
from dotenv import load_dotenv

load_dotenv()

# Load environment variables
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")  
FASTAPI_HOST = os.getenv("FASTAPI_HOST", "0.0.0.0")
FASTAPI_PORT = int(os.getenv("FASTAPI_PORT", 8000))
FASTAPI_RELOAD = os.getenv("FASTAPI_RELOAD", "true").lower() in ("true")

app = FastAPI(
    title="FastAPI with Keycloak",
    description="API with Keycloak authentication",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Print the requested URL to the console for each request
@app.middleware("http")
async def log_request(request, call_next):
    print(f"Request URL: {request.url}")
    response = await call_next(request)
    return response

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(health.router, tags=["health"])


@app.get("/")
async def root():
    return {"message": "FastAPI with Keycloak Authentication"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=FASTAPI_HOST, port=FASTAPI_PORT, reload=FASTAPI_RELOAD)

