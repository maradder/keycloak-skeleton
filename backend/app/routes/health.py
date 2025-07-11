from fastapi import APIRouter
from app.dependencies.keycloak import KEYCLOAK_PUBLIC_KEY_URL
import requests

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check endpoint with Keycloak connectivity test"""
    try:
        # Test Keycloak connectivity
        response = requests.get(KEYCLOAK_PUBLIC_KEY_URL, timeout=5)
        keycloak_status = "connected" if response.status_code == 200 else "disconnected"
    except Exception as e:
        keycloak_status = f"error: {str(e)}"

    return {
        "status": "healthy",
        "keycloak_status": keycloak_status,
        "keycloak_url": KEYCLOAK_PUBLIC_KEY_URL,
    }