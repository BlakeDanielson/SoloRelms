"""
Webhook endpoints for Clerk integration
Handles user creation, updates, and deletion events from Clerk
"""
from fastapi import APIRouter, Request, HTTPException, Depends, status, BackgroundTasks
from sqlalchemy.orm import Session
from database import get_db
from auth import create_or_update_user, verify_webhook_signature
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/webhooks",
    tags=["webhooks"]
)

@router.post("/clerk")
async def clerk_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Handle Clerk webhook events for user management
    Supports user.created, user.updated, and user.deleted events
    """
    try:
        # Get the raw body and signature
        body = await request.body()
        signature = request.headers.get("svix-signature", "")
        
        # Verify webhook signature (simplified for development)
        if not verify_webhook_signature(body, signature):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature"
            )
        
        # Parse the event data
        try:
            event_data = json.loads(body.decode())
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON payload"
            )
        
        event_type = event_data.get("type")
        user_data = event_data.get("data", {})
        
        logger.info(f"Received Clerk webhook event: {event_type}")
        
        # Handle different event types
        if event_type == "user.created":
            await handle_user_created(user_data, db)
        elif event_type == "user.updated":
            await handle_user_updated(user_data, db)
        elif event_type == "user.deleted":
            await handle_user_deleted(user_data, db)
        else:
            logger.warning(f"Unhandled Clerk webhook event type: {event_type}")
        
        return {"message": "Webhook processed successfully"}
        
    except Exception as e:
        logger.error(f"Error processing Clerk webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process webhook"
        )

async def handle_user_created(user_data: dict, db: Session):
    """Handle user creation event from Clerk"""
    try:
        user = create_or_update_user(db, user_data)
        logger.info(f"Created user: {user.id} ({user.email})")
        
        # You could trigger additional setup here, like:
        # - Send welcome email
        # - Create default character
        # - Set up user preferences
        
    except Exception as e:
        logger.error(f"Failed to create user: {e}")
        raise

async def handle_user_updated(user_data: dict, db: Session):
    """Handle user update event from Clerk"""
    try:
        user = create_or_update_user(db, user_data)
        logger.info(f"Updated user: {user.id} ({user.email})")
        
    except Exception as e:
        logger.error(f"Failed to update user: {e}")
        raise

async def handle_user_deleted(user_data: dict, db: Session):
    """Handle user deletion event from Clerk"""
    try:
        user_id = user_data.get("id")
        if not user_id:
            logger.warning("User deletion event missing user ID")
            return
        
        # Find and delete the user
        from models.user import User
        user = db.query(User).filter(User.id == user_id).first()
        
        if user:
            # This will cascade delete all related data (characters, story arcs, etc.)
            db.delete(user)
            db.commit()
            logger.info(f"Deleted user: {user_id}")
        else:
            logger.warning(f"User {user_id} not found for deletion")
    
    except Exception as e:
        logger.error(f"Failed to delete user: {e}")
        raise

@router.get("/test")
async def test_webhook():
    """Test endpoint to verify webhook setup"""
    return {"message": "Webhook endpoint is working"}

@router.post("/sync-user")
async def sync_user_manually(
    user_data: dict,
    db: Session = Depends(get_db)
):
    """
    Manual user sync endpoint for development/testing
    Allows manually creating/updating users without going through Clerk webhooks
    """
    try:
        user = create_or_update_user(db, user_data)
        return {
            "message": "User synced successfully",
            "user": user.to_dict()
        }
    except Exception as e:
        logger.error(f"Failed to sync user manually: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync user: {str(e)}"
        ) 