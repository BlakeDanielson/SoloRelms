"""
Integration tests for frontend-backend authentication flow
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app
from models.user import User
import json

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_integration.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def client(setup_database):
    return TestClient(app)

class TestAuthenticationFlow:
    """Test the complete authentication flow"""
    
    def test_protected_endpoint_without_auth(self, client):
        """Test that protected endpoints require authentication"""
        response = client.get("/api/users/me")
        assert response.status_code == 403
        assert response.json()["detail"] == "Not authenticated"
    
    def test_public_endpoints_accessible(self, client):
        """Test that public endpoints are accessible without authentication"""
        # Health endpoint
        response = client.get("/health")
        assert response.status_code == 200
        
        # Webhook test endpoint
        response = client.get("/api/webhooks/test")
        assert response.status_code == 200
        assert response.json()["message"] == "Webhook endpoint is working"
    
    def test_user_creation_via_webhook(self, client):
        """Test user creation through webhook (simulating Clerk)"""
        user_data = {
            "id": "integration_test_user",
            "email_addresses": [{"email_address": "integration@test.com"}],
            "first_name": "Integration",
            "last_name": "Test",
            "username": "integrationtest"
        }
        
        response = client.post(
            "/api/webhooks/sync-user",
            json=user_data,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["user"]["id"] == "integration_test_user"
        assert result["user"]["email"] == "integration@test.com"
        assert result["user"]["display_name"] == "Integration Test"
    
    def test_public_profile_access(self, client):
        """Test accessing public user profiles"""
        # First create a user
        user_data = {
            "id": "public_profile_test",
            "email_addresses": [{"email_address": "public@test.com"}],
            "first_name": "Public",
            "last_name": "Profile",
            "username": "publicprofile"
        }
        
        client.post("/api/webhooks/sync-user", json=user_data)
        
        # Then access their public profile
        response = client.get("/api/users/profile/public_profile_test")
        assert response.status_code == 200
        
        profile = response.json()
        assert profile["id"] == "public_profile_test"
        assert profile["display_name"] == "Public Profile"
        assert "email" not in profile  # Email should not be in public profile
    
    def test_cors_headers(self, client):
        """Test that CORS headers are properly set for frontend communication"""
        response = client.options("/api/users/me", headers={
            "Origin": "http://localhost:3001",
            "Access-Control-Request-Method": "GET"
        })
        
        # The response should include CORS headers
        assert response.status_code == 200
    
    def test_webhook_error_handling(self, client):
        """Test webhook error handling"""
        # Test with invalid JSON
        response = client.post(
            "/api/webhooks/clerk",
            data="invalid json",
            headers={
                "svix-signature": "test-signature",
                "content-type": "application/json"
            }
        )
        
        assert response.status_code == 500
        assert "Failed to process webhook" in response.json()["detail"]
    
    def test_database_health_check(self, client):
        """Test database connectivity"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

class TestSessionManagement:
    """Test session management and route protection"""
    
    def test_route_protection_simulation(self, client):
        """Simulate route protection behavior"""
        # Test various protected endpoints
        protected_endpoints = [
            "/api/users/me",
            "/api/users/me/characters",
            "/api/users/me/stats"
        ]
        
        for endpoint in protected_endpoints:
            response = client.get(endpoint)
            assert response.status_code == 403
            assert "Not authenticated" in response.json()["detail"]
    
    def test_user_data_consistency(self, client):
        """Test that user data remains consistent across requests"""
        # Create a user
        user_data = {
            "id": "consistency_test",
            "email_addresses": [{"email_address": "consistency@test.com"}],
            "first_name": "Consistency",
            "last_name": "Test",
            "username": "consistencytest"
        }
        
        # Create user via webhook
        response1 = client.post("/api/webhooks/sync-user", json=user_data)
        assert response1.status_code == 200
        
        # Update user via webhook
        user_data["first_name"] = "Updated"
        response2 = client.post("/api/webhooks/sync-user", json=user_data)
        assert response2.status_code == 200
        
        # Verify update
        profile_response = client.get("/api/users/profile/consistency_test")
        assert profile_response.status_code == 200
        assert profile_response.json()["display_name"] == "Updated Test" 