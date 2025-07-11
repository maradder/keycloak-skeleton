from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from app.dependencies.keycloak import require_role, keycloak_auth

router = APIRouter()

@router.get("/admin-only")
async def admin_only_endpoint(
    current_user: Dict[str, Any] = Depends(require_role("admin")),
):
    """Admin-only endpoint"""
    return {
        "message": "This endpoint is only accessible to admins",
        "user": current_user.get("preferred_username"),
        "admin_data": {
            "sensitive_info": "This is admin-only data",
            # This is a hardcoded number for initial testing. If we want to use this endpoint
            # to return dynamic data, we would need to fetch the info from Keycloak.
            "system_stats": {"users": 150, "active_sessions": 45},
        },
    }

@router.post("/refresh-keys")
async def refresh_keys(current_user: Dict[str, Any] = Depends(require_role("admin"))):
    """Manually refresh Keycloak public keys (admin only)"""
    try:
        keycloak_auth.refresh_public_keys()
        return {"message": "Public keys refreshed successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refresh public keys",
        )
