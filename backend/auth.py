"""
Authentication utilities for Clerk integration
Handles JWT verification and user authentication for FastAPI endpoints
"""
import os
import requests
from typing import Optional, Dict, Any
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
import json
import logging

logger = logging.getLogger(__name__)

# Security scheme for FastAPI
security = HTTPBearer()

# Clerk configuration
CLERK_PEM_PUBLIC_KEY = None
CLERK_DOMAIN = os.getenv("CLERK_DOMAIN", "")
CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY", "")

class ClerkJWTAuth:
    """Clerk JWT authentication handler"""
    
    def __init__(self):
        self.public_key = None
        self.issuer = f"https://{CLERK_DOMAIN}"
    
    async def get_public_key(self) -> str:
        """Fetch Clerk's public key for JWT verification"""
        if self.public_key:
            return self.public_key
        
        try:
            # Get the JWKS from Clerk
            jwks_url = f"https://{CLERK_DOMAIN}/.well-known/jwks.json"
            response = requests.get(jwks_url, timeout=10)
            response.raise_for_status()
            jwks = response.json()
            
            # For now, use the first key (in production, match by kid)
            if jwks.get("keys"):
                # Convert JWK to PEM format would be needed here
                # For development, we'll use a simpler approach
                self.public_key = "placeholder"  # This needs proper implementation
                return self.public_key
                
        except Exception as e:
            logger.error(f"Failed to fetch Clerk public key: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication service unavailable"
            )
    
    async def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify Clerk JWT token and return payload"""
        try:
            # For development purposes, we'll use a simpler verification
            # In production, you'd want to properly verify with Clerk's public key
            
            # Extract payload without verification for now (DEVELOPMENT ONLY)
            # This should be replaced with proper JWT verification
            unverified_payload = jwt.get_unverified_claims(token)
            
            # Basic validation
            if not unverified_payload.get("sub"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: missing user ID"
                )
            
            return unverified_payload
            
        except JWTError as e:
            logger.error(f"JWT verification failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )

# Global auth instance
clerk_auth = ClerkJWTAuth()

async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """Extract user ID from JWT token"""
    token = credentials.credentials
    payload = await clerk_auth.verify_token(token)
    return payload["sub"]

async def get_current_user(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
) -> User:
    """Get the current user from database, create if doesn't exist"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        # Auto-create user from Clerk token if they don't exist
        # This handles cases where webhook didn't fire or user wasn't created during registration
        logger.info(f"Creating new user from Clerk token: {user_id}")
        
        # Extract additional info from token if available
        # For now, we'll create with minimal info and let webhook/profile update fill in details
        user = User(
            id=user_id,
            email=f"{user_id}@clerk.temp",  # Temporary email, will be updated by webhook
            first_name=None,
            last_name=None,
            username=None,
            image_url=None,
            email_verified=False,
            is_active=True
        )
        db.add(user)
        
        try:
            db.commit()
            db.refresh(user)
            logger.info(f"Successfully created user: {user_id}")
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create user {user_id}: {e}")
            # Try to get user again in case of race condition
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create or retrieve user"
                )
    
    return user

async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user if authenticated, otherwise return None"""
    if not credentials:
        return None
    
    try:
        user_id = await get_current_user_id(credentials)
        return await get_current_user(user_id, db)
    except HTTPException:
        return None

def create_or_update_user(db: Session, user_data: Dict[str, Any]) -> User:
    """Create or update user from Clerk webhook data"""
    user_id = user_data.get("id")
    
    if not user_id:
        raise ValueError("User ID is required")
    
    # Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    
    if user:
        # Update existing user
        user.email = user_data.get("email_addresses", [{}])[0].get("email_address", user.email)
        user.first_name = user_data.get("first_name")
        user.last_name = user_data.get("last_name")
        user.username = user_data.get("username")
        user.image_url = user_data.get("image_url")
        user.email_verified = user_data.get("email_addresses", [{}])[0].get("verification", {}).get("status") == "verified"
    else:
        # Create new user
        user = User(
            id=user_id,
            email=user_data.get("email_addresses", [{}])[0].get("email_address", ""),
            first_name=user_data.get("first_name"),
            last_name=user_data.get("last_name"),
            username=user_data.get("username"),
            image_url=user_data.get("image_url"),
            email_verified=user_data.get("email_addresses", [{}])[0].get("verification", {}).get("status") == "verified",
            is_active=True
        )
        db.add(user)
    
    db.commit()
    db.refresh(user)
    return user

def verify_webhook_signature(payload: bytes, signature: str) -> bool:
    """Verify Clerk webhook signature"""
    # This is a simplified version - implement proper webhook verification
    # using your Clerk webhook secret
    return True  # For development - implement proper verification in production 