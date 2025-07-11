from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPAuthorizationCredentials
from jose import jwt
import logging
import requests
from typing import Dict, Any
from app.dependencies.keycloak import get_current_user, security, KEYCLOAK_SERVER_URL, KEYCLOAK_REALM, KEYCLOAK_CLIENT_ID, KEYCLOAK_CLIENT_SECRET
import os

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/protected-endpoint")
async def protected_endpoint(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Protected endpoint that requires authentication"""
    return {
        "message": "This is a protected endpoint",
        "user": {
            "id": current_user.get("sub"),
            "username": current_user.get("preferred_username"),
            "email": current_user.get("email"),
            "roles": current_user.get("realm_access", {}).get("roles", []),
        },
        "timestamp": current_user.get("iat"),
        "data": {
            "example": "This is some protected data",
            "items": ["item1", "item2", "item3"],
        },
    }

@router.get("/user-info")
async def get_user_info(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get detailed user information"""
    return {
        "sub": current_user.get("sub"),
        "preferred_username": current_user.get("preferred_username"),
        "email": current_user.get("email"),
        "name": current_user.get("name"),
        "given_name": current_user.get("given_name"),
        "family_name": current_user.get("family_name"),
        "roles": current_user.get("realm_access", {}).get("roles", []),
        "groups": current_user.get("groups", []),
        "email_verified": current_user.get("email_verified"),
        "token_issued_at": current_user.get("iat"),
        "token_expires_at": current_user.get("exp"),
    }

@router.get("/debug-token")
async def debug_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Debug endpoint to inspect token without verification"""
    
    token = credentials.credentials
    try:
        header = jwt.get_unverified_header(token)
        payload = jwt.get_unverified_claims(token)
        return {
            "header": header,
            "payload": payload,
            "expected_issuer": f"{KEYCLOAK_SERVER_URL}/realms/{KEYCLOAK_REALM}",
            "expected_audience": KEYCLOAK_CLIENT_ID,
        }
    except Exception as e:
        return {"error": str(e)}

@router.post("/logout")
async def logout_user_with_redirect(
    request: Request, 
    current_user: Dict[str, Any] = Depends(get_current_user),
    redirect_url: str = None
):
    """Logout with redirect to frontend dashboard"""
    
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No valid token provided",
            )

        token = auth_header.split(" ")[1]

        # Revoke token on Keycloak
        revoke_url = f"{KEYCLOAK_SERVER_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/revoke"
        revoke_data = {
            "client_id": KEYCLOAK_CLIENT_ID,
            "token": token,
            "token_type_hint": "access_token"
        }

        revoke_response = None
        try:
            revoke_response = requests.post(
                revoke_url,
                data=revoke_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10,
            )
            logger.info(f"Token revocation response: {revoke_response.status_code}")
            
        except requests.RequestException as e:
            logger.warning(f"Failed to call Keycloak revoke endpoint: {e}")

        # Get frontend URL from environment or use default
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
        
        # Use provided redirect_url or default to dashboard
        if not redirect_url:
            redirect_url = f"{frontend_url}/dashboard"
        
        logger.info(f"User {current_user.get('preferred_username')} logged out, redirecting to {redirect_url}")
        
        # Return success response with redirect information
        # Note: FastAPI doesn't automatically redirect for POST requests from fetch()
        # The frontend will need to handle the redirect
        return {
            "message": "Logged out successfully",
            "user": current_user.get("preferred_username"),
            "revoke_status": revoke_response.status_code if revoke_response else "not_attempted",
            "redirect_url": redirect_url,
            "success": True
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Logout failed"
        )

@router.get("/logout")
async def logout_user_get_redirect(
    request: Request, 
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """GET version of logout that actually redirects"""
    
    try:
        # Get token from query parameter if provided, otherwise from header
        token = request.query_params.get("token")
        if not token:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

        if token:
            # Revoke token on Keycloak
            revoke_url = f"{KEYCLOAK_SERVER_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/revoke"
            revoke_data = {
                "client_id": KEYCLOAK_CLIENT_ID,
                "token": token,
                "token_type_hint": "access_token"
            }

            try:
                requests.post(
                    revoke_url,
                    data=revoke_data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    timeout=10,
                )
            except requests.RequestException as e:
                logger.warning(f"Failed to revoke token: {e}")

        # Get frontend URL and redirect
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
        redirect_url = f"{frontend_url}/dashboard"
        
        logger.info(f"User {current_user.get('preferred_username')} logged out via GET, redirecting to {redirect_url}")
        
        return RedirectResponse(url=redirect_url, status_code=302)

    except Exception as e:
        logger.error(f"Logout error: {e}")
        # Even if there's an error, redirect to frontend
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
        return RedirectResponse(url=f"{frontend_url}/dashboard", status_code=302)

@router.post("/logout-simple")
async def logout_simple(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Simple logout endpoint that just acknowledges the logout"""
    logger.info(f"User {current_user.get('preferred_username')} logged out")
    return {
        "message": "Logged out successfully",
        "user": current_user.get("preferred_username"),
    }