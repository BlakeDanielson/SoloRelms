#!/usr/bin/env python3
"""
FEEDBACK COLLECTION API ENDPOINTS
FastAPI routes for SoloRealms MVP user feedback collection and analysis

Endpoints:
- POST /feedback/submit - Submit user feedback
- POST /feedback/survey/response - Submit survey response  
- GET /feedback/survey/template - Get survey template
- POST /feedback/session/track - Track user session
- GET /feedback/analytics/summary - Get feedback analytics
- GET /feedback/report - Generate comprehensive report
- GET /feedback/health - Health check

"""

from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import os
import sys

# Add the test_suites directory to the path so we can import our feedback system
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'test_suites'))

try:
    from feedback_collection_system import FeedbackCollectionSystem, FeedbackType
except ImportError:
    # Fallback if import fails
    print("Warning: Could not import feedback_collection_system")
    FeedbackCollectionSystem = None
    FeedbackType = None

from auth import get_current_user_id

router = APIRouter(prefix="/feedback", tags=["feedback"])

# Pydantic models for request/response validation
class FeedbackSubmission(BaseModel):
    """User feedback submission"""
    content: str = Field(..., min_length=1, max_length=2000, description="Feedback content")
    rating: int = Field(..., ge=1, le=5, description="Rating from 1-5")
    feedback_type: str = Field(default="general", description="Type of feedback")
    page_context: Optional[str] = Field(None, description="Page where feedback was given")
    session_id: Optional[str] = Field(None, description="User session ID")
    additional_data: Optional[Dict[str, Any]] = Field(default_factory=dict)

class SurveySubmission(BaseModel):
    """Survey response submission"""
    survey_id: str = Field(..., description="Survey identifier")
    responses: Dict[str, Any] = Field(..., description="Survey responses")
    completion_time_seconds: int = Field(..., ge=1, description="Time taken to complete survey")

class SessionTracking(BaseModel):
    """User session tracking data"""
    pages_visited: List[str] = Field(default_factory=list)
    actions_performed: List[Dict[str, Any]] = Field(default_factory=list)
    character_created: bool = Field(default=False)
    story_started: bool = Field(default=False)
    combat_engaged: bool = Field(default=False)
    errors_encountered: List[Dict[str, Any]] = Field(default_factory=list)
    performance_metrics: Dict[str, float] = Field(default_factory=dict)

class FeedbackResponse(BaseModel):
    """Response for feedback submission"""
    success: bool
    feedback_id: str
    message: str

class SurveyResponse(BaseModel):
    """Response for survey submission"""
    success: bool
    response_id: str
    message: str

class SessionResponse(BaseModel):
    """Response for session tracking"""
    success: bool
    session_id: str
    message: str

class AnalyticsSummary(BaseModel):
    """Analytics summary response"""
    period_days: int
    total_feedback_entries: int
    total_survey_responses: int
    average_rating: float
    sentiment_distribution: Dict[int, int]
    top_issues: List[Dict[str, Any]]
    top_highlights: List[Dict[str, Any]]

# Initialize feedback system (with error handling)
def get_feedback_system():
    """Get feedback system instance with error handling"""
    if FeedbackCollectionSystem is None:
        raise HTTPException(status_code=500, detail="Feedback system not available")
    
    try:
        return FeedbackCollectionSystem()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize feedback system: {str(e)}")

@router.get("/health")
async def feedback_health():
    """Health check for feedback system"""
    try:
        system = get_feedback_system()
        return {
            "status": "healthy",
            "service": "feedback_collection",
            "database": "mvp_feedback.db",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Feedback system unhealthy: {str(e)}")

@router.post("/submit", response_model=FeedbackResponse)
async def submit_feedback(
    feedback: FeedbackSubmission,
    current_user_id: str = Depends(get_current_user_id)
):
    """Submit user feedback"""
    try:
        system = get_feedback_system()
        
        # Prepare feedback data
        feedback_data = {
            "content": feedback.content,
            "rating": feedback.rating,
            "type": feedback.feedback_type,
            "page_context": feedback.page_context or "",
            "session_id": feedback.session_id or "",
            "user_agent": "API-Submission",  # Could be enhanced to get from request headers
            "additional_data": feedback.additional_data
        }
        
        # Submit feedback
        feedback_id = system.collect_feedback(current_user_id, feedback_data)
        
        return FeedbackResponse(
            success=True,
            feedback_id=feedback_id,
            message="Feedback submitted successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit feedback: {str(e)}")

@router.post("/survey/response", response_model=SurveyResponse)
async def submit_survey_response(
    survey: SurveySubmission,
    current_user_id: str = Depends(get_current_user_id)
):
    """Submit survey response"""
    try:
        system = get_feedback_system()
        
        # Submit survey response
        response_id = system.submit_survey_response(
            current_user_id,
            survey.survey_id,
            survey.responses,
            survey.completion_time_seconds
        )
        
        return SurveyResponse(
            success=True,
            response_id=response_id,
            message="Survey response submitted successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit survey response: {str(e)}")

@router.get("/survey/template")
async def get_survey_template():
    """Get the MVP survey template"""
    try:
        system = get_feedback_system()
        survey = system.generate_mvp_survey()
        
        return {
            "success": True,
            "survey": survey,
            "message": "Survey template retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get survey template: {str(e)}")

@router.post("/session/track", response_model=SessionResponse)
async def track_user_session(
    session: SessionTracking,
    current_user_id: str = Depends(get_current_user_id)
):
    """Track user session data"""
    try:
        system = get_feedback_system()
        
        # Prepare session data
        session_data = {
            "pages_visited": session.pages_visited,
            "actions_performed": session.actions_performed,
            "character_created": session.character_created,
            "story_started": session.story_started,
            "combat_engaged": session.combat_engaged,
            "errors_encountered": session.errors_encountered,
            "performance_metrics": session.performance_metrics
        }
        
        # Track session
        session_id = system.track_user_session(current_user_id, session_data)
        
        return SessionResponse(
            success=True,
            session_id=session_id,
            message="User session tracked successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to track session: {str(e)}")

@router.get("/analytics/summary", response_model=AnalyticsSummary)
async def get_analytics_summary(
    days_back: int = Query(default=7, ge=1, le=365, description="Number of days to analyze"),
    current_user_id: str = Depends(get_current_user_id)  # Admin check could be added here
):
    """Get feedback analytics summary"""
    try:
        system = get_feedback_system()
        analysis = system.analyze_feedback_trends(days_back)
        
        return AnalyticsSummary(
            period_days=analysis["period_days"],
            total_feedback_entries=analysis["total_feedback_entries"],
            total_survey_responses=analysis["total_survey_responses"],
            average_rating=analysis["average_rating"],
            sentiment_distribution=analysis["sentiment_distribution"],
            top_issues=analysis["common_issues"][:5],
            top_highlights=analysis["positive_highlights"][:5]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")

@router.get("/report")
async def generate_feedback_report(
    days_back: int = Query(default=7, ge=1, le=365, description="Number of days to analyze"),
    save_file: bool = Query(default=False, description="Save report to file"),
    current_user_id: str = Depends(get_current_user_id)  # Admin check could be added here
):
    """Generate comprehensive feedback report"""
    try:
        system = get_feedback_system()
        report = system.generate_feedback_report(days_back)
        
        response_data = {
            "success": True,
            "report": report,
            "message": "Feedback report generated successfully"
        }
        
        # Optionally save to file
        if save_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"mvp_feedback_report_{timestamp}.json"
            
            try:
                with open(filename, 'w') as f:
                    json.dump(report, f, indent=2, default=str)
                
                response_data["file_saved"] = filename
                response_data["message"] += f" and saved to {filename}"
                
            except Exception as e:
                response_data["file_error"] = f"Could not save file: {str(e)}"
        
        return response_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")

# Background task endpoints for performance
@router.post("/submit/async")
async def submit_feedback_async(
    feedback: FeedbackSubmission,
    background_tasks: BackgroundTasks,
    current_user_id: str = Depends(get_current_user_id)
):
    """Submit feedback asynchronously for better performance"""
    
    def process_feedback():
        """Background task to process feedback"""
        try:
            system = get_feedback_system()
            feedback_data = {
                "content": feedback.content,
                "rating": feedback.rating,
                "type": feedback.feedback_type,
                "page_context": feedback.page_context or "",
                "session_id": feedback.session_id or "",
                "user_agent": "API-Async-Submission",
                "additional_data": feedback.additional_data
            }
            system.collect_feedback(current_user_id, feedback_data)
        except Exception as e:
            print(f"Background feedback processing failed: {str(e)}")
    
    # Add background task
    background_tasks.add_task(process_feedback)
    
    return {
        "success": True,
        "message": "Feedback submitted for async processing",
        "status": "processing"
    }

@router.get("/stats/quick")
async def get_quick_stats():
    """Get quick feedback statistics (no auth required)"""
    try:
        system = get_feedback_system()
        analysis = system.analyze_feedback_trends(1)  # Last day only
        
        return {
            "feedback_entries_today": analysis["total_feedback_entries"],
            "survey_responses_today": analysis["total_survey_responses"],
            "average_rating": analysis["average_rating"],
            "status": "healthy"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "status": "error"
        }

# Public endpoint for survey template (no auth)
@router.get("/survey/public")
async def get_public_survey():
    """Get survey template without authentication"""
    try:
        system = get_feedback_system()
        survey = system.generate_mvp_survey()
        
        # Remove any sensitive information
        public_survey = {
            "survey_id": survey["survey_id"],
            "title": survey["title"],
            "description": survey["description"],
            "estimated_time_minutes": survey["estimated_time_minutes"],
            "sections": survey["sections"]
        }
        
        return {
            "success": True,
            "survey": public_survey
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get public survey: {str(e)}")

# Development/testing endpoints
@router.post("/test/generate-sample-data")
async def generate_sample_data(
    num_users: int = Query(default=5, ge=1, le=20, description="Number of sample users"),
    current_user_id: str = Depends(get_current_user_id)
):
    """Generate sample feedback data for testing (development only)"""
    try:
        system = get_feedback_system()
        
        # Generate sample data similar to the main demo
        demo_users = [f"test_user_{i}" for i in range(num_users)]
        generated_data = {
            "users_created": num_users,
            "feedback_entries": [],
            "survey_responses": [],
            "sessions": []
        }
        
        for i, user_id in enumerate(demo_users):
            # Track session
            session_data = {
                "pages_visited": ["/", "/character/create", "/dashboard", "/game"],
                "actions_performed": [
                    {"action": "character_created", "timestamp": datetime.now().isoformat()},
                    {"action": "story_started", "timestamp": datetime.now().isoformat()}
                ],
                "character_created": True,
                "story_started": True,
                "combat_engaged": i % 2 == 0,
                "errors_encountered": [] if i % 3 != 0 else [{"error": "slow loading", "page": "/game"}],
                "performance_metrics": {
                    "avg_load_time": 500 + (i * 100),
                    "api_response_time": 200 + (i * 50)
                }
            }
            
            session_id = system.track_user_session(user_id, session_data)
            generated_data["sessions"].append(session_id)
            
            # Submit feedback
            feedback_content = [
                "Love the character creation! Very intuitive and fun.",
                "The story generation is amazing but loading is a bit slow.",
                "Combat system needs work, feels clunky at times.",
                "Great concept but encountered some bugs during play.",
                "Absolutely fantastic! Can't wait for more features."
            ]
            
            feedback_data = {
                "session_id": session_id,
                "type": "general",
                "content": feedback_content[i % len(feedback_content)],
                "rating": [5, 3, 2, 3, 5][i % 5],
                "page_context": "/game",
                "user_agent": "Test-Data-Generator"
            }
            
            feedback_id = system.collect_feedback(user_id, feedback_data)
            generated_data["feedback_entries"].append(feedback_id)
            
            # Submit survey response
            survey_responses = {
                "overall_rating": [5, 3, 2, 4, 5][i % 5],
                "recommendation": [9, 6, 4, 7, 10][i % 5],
                "character_creation_ease": [5, 4, 3, 4, 5][i % 5],
                "story_quality": [5, 4, 2, 3, 5][i % 5],
                "ui_design": [4, 3, 2, 4, 5][i % 5],
                "loading_speed": [3, 2, 1, 3, 4][i % 5],
                "most_wanted_feature": ["Multiplayer campaigns", "More character classes/races", "Mobile app", "Voice narration", "Custom dice sets"][i % 5]
            }
            
            response_id = system.submit_survey_response(user_id, "mvp_feedback_v1", survey_responses, 180 + (i * 30))
            generated_data["survey_responses"].append(response_id)
        
        return {
            "success": True,
            "message": f"Generated sample data for {num_users} users",
            "data": generated_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate sample data: {str(e)}") 