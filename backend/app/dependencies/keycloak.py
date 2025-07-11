from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from typing import Optional, Dict, Any
import requests
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()

# Keycloak configuration
ALTERNATE_KEYCLOAK_SERVER_URL = os.getenv(
    "ALTERNATE_KEYCLOAK_SERVER_URL", "http://keycloak:8080"
)
KEYCLOAK_SERVER_URL = os.getenv("KEYCLOAK_SERVER_URL", "http://keycloak:8080")
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM", "testrealm")
KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID", "test-client")
KEYCLOAK_CLIENT_SECRET = os.getenv("KEYCLOAK_CLIENT_SECRET", "your-client-secret")

# Keycloak URLs
KEYCLOAK_PUBLIC_KEY_URL = (
    f"{KEYCLOAK_SERVER_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/certs"
)
KEYCLOAK_TOKEN_URL = (
    f"{KEYCLOAK_SERVER_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token"
)
KEYCLOAK_USERINFO_URL = (
    f"{KEYCLOAK_SERVER_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/userinfo"
)

class KeycloakAuth:
    def __init__(self):
        self.public_keys = None
        self.refresh_public_keys()

    def refresh_public_keys(self):
        """Fetch public keys from Keycloak"""
        try:
            logger.info("Fetching public keys from Keycloak...")
            logger.info(f"Keycloak Public Key URL: {KEYCLOAK_PUBLIC_KEY_URL}")
            response = requests.get(KEYCLOAK_PUBLIC_KEY_URL, timeout=10)
            response.raise_for_status()
            self.public_keys = response.json()
            logger.info(f"Public keys refreshed successfully")
        except requests.RequestException as e:
            logger.error(
                f"Failed to fetch public keys from {KEYCLOAK_PUBLIC_KEY_URL}: {e}"
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication service unavailable",
            )

    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token with Keycloak public key"""
        try:
            unverified_payload = jwt.get_unverified_claims(token)
            unverified_header = jwt.get_unverified_header(token)

            logger.info(f"Token issuer: {unverified_payload.get('iss')}")
            logger.info(f"Expected issuer: {KEYCLOAK_SERVER_URL}/realms/{KEYCLOAK_REALM}")
            logger.info(f"Token audience: {unverified_payload.get('aud')}")
            logger.info(f"Expected audience: {KEYCLOAK_CLIENT_ID}")

            key_id = unverified_header.get("kid")
            if not key_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: missing key ID",
                )

            # Find the public key
            public_key = None
            for key in self.public_keys.get("keys", []):
                if key.get("kid") == key_id:
                    public_key = key
                    break

            if not public_key:
                # Try refreshing keys
                logger.info("Key not found, refreshing public keys...")
                self.refresh_public_keys()
                for key in self.public_keys.get("keys", []):
                    if key.get("kid") == key_id:
                        public_key = key
                        break

            if not public_key:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: key not found",
                )

            # Convert JWK to PEM format for verification
            try:
                from jose.utils import base64url_decode
                from cryptography.hazmat.primitives import serialization
                from cryptography.hazmat.primitives.asymmetric import rsa

                # Extract RSA components
                n = base64url_decode(public_key["n"].encode("utf-8"))
                e = base64url_decode(public_key["e"].encode("utf-8"))

                # Convert to integers
                n_int = int.from_bytes(n, "big")
                e_int = int.from_bytes(e, "big")

                # Create RSA public key
                rsa_key = rsa.RSAPublicNumbers(e_int, n_int).public_key()

                # Convert to PEM format
                pem_key = rsa_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo,
                )

                logger.info("Successfully converted JWK to PEM")

            except Exception as e:
                logger.error(f"Failed to convert JWK to PEM: {e}")
                pem_key = public_key

            # Get the actual issuer from the token to compare
            token_issuer = unverified_payload.get("iss")
            expected_issuer = f"{KEYCLOAK_SERVER_URL}/realms/{KEYCLOAK_REALM}"
            alternate_issuer = f"{ALTERNATE_KEYCLOAK_SERVER_URL}/realms/{KEYCLOAK_REALM}"

            # Use the token's issuer if it differs
            if token_issuer != expected_issuer:
                if token_issuer != alternate_issuer:
                    logger.warning(
                        f"Issuer mismatch. Token: {token_issuer}, Expected: {expected_issuer}"
                    )
                    logger.info("Using token issuer for verification")
                    issuer_to_use = token_issuer
                else:
                    issuer_to_use = alternate_issuer
            else:
                issuer_to_use = expected_issuer

            # Verify token
            payload = jwt.decode(
                token,
                pem_key,
                algorithms=["RS256"],
                audience=KEYCLOAK_CLIENT_ID,
                issuer=issuer_to_use,
                options={
                    "verify_signature": True,
                    "verify_aud": False,
                    "verify_exp": True,
                    "verify_iss": True,
                },
            )

            logger.info(f"Token verified successfully for user: {payload.get('preferred_username')}")
            return payload

        except JWTError as e:
            logger.error(f"JWT verification failed: {e}")
            logger.error(f"Token header: {jwt.get_unverified_header(token)}")
            logger.error(f"Token payload: {jwt.get_unverified_claims(token)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}",
            )

# Initialize Keycloak auth
try:
    keycloak_auth = KeycloakAuth()
except HTTPException as e:
    logger.error(f"Failed to initialize KeycloakAuth: {e.detail}")

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Dependency to get current user from token"""
    token = credentials.credentials
    payload = keycloak_auth.verify_token(token)
    return payload

def require_role(required_role: str):
    """Decorator to require specific role"""
    logger.info(f"Requiring role: {required_role}")

    def role_checker(current_user: Dict[str, Any] = Depends(get_current_user)):
        user_roles = current_user.get("realm_access", {}).get("roles", [])
        if required_role not in user_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{required_role}' required",
            )
        return current_user

    return role_checker