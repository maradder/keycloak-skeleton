from fastapi import APIRouter, HTTPException, status
from app.dependencies.keycloak import KEYCLOAK_PUBLIC_KEY_URL
import requests
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check endpoint with Keycloak connectivity test"""
    keycloak_status = "unknown"
    overall_status = "healthy"
    
    try:
        # Test Keycloak connectivity
        response = requests.get(KEYCLOAK_PUBLIC_KEY_URL, timeout=5)
        if response.status_code == 200:
            keycloak_status = "connected"
        else:
            keycloak_status = f"http_error_{response.status_code}"
            logger.warning(f"Keycloak health check failed with status {response.status_code}")
            
    except requests.exceptions.Timeout:
        keycloak_status = "timeout"
        logger.error("Keycloak health check timed out")
        overall_status = "degraded"
        
    except requests.exceptions.ConnectionError:
        keycloak_status = "connection_refused"
        logger.error("Unable to connect to Keycloak")
        overall_status = "degraded"
        
    except Exception as e:
        keycloak_status = "error"
        logger.error(f"Keycloak health check failed: {e}")
        overall_status = "degraded"

    response_data = {
        "status": overall_status,
        "services": {
            "keycloak": {
                "status": keycloak_status,
                "url": KEYCLOAK_PUBLIC_KEY_URL
            }
        }
    }
    
    # Return 503 if any critical service is down
    if overall_status == "degraded":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=response_data
        )
    
    return response_data