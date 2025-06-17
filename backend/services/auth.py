"""
Stub authentication service for development.
TODO: Implement proper authentication with Clerk
"""

from fastapi import HTTPException


async def get_current_user():
    """
    Stub function that returns a mock user for development.
    TODO: Implement proper Clerk authentication
    """
    # For now, return a mock user that matches our test character's user_id
    return {
        'user_id': 'user_2nGfzI9kCPNrk8rXjzfyNEAKYZ9',  # This matches the user_id of our test character
        'email': 'test@example.com',
        'name': 'Test User'
    }


def require_admin():
    """
    Stub function for admin authentication
    TODO: Implement proper admin role checking
    """
    return get_current_user()


def get_optional_user():
    """
    Optional authentication - returns user if authenticated, None otherwise
    TODO: Implement proper optional authentication
    """
    try:
        return get_current_user()
    except:
        return None 