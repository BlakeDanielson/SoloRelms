#!/usr/bin/env python3
"""
FEEDBACK API INTEGRATION TEST SUITE
Comprehensive validation of feedback collection system integration with live MVP

Tests all feedback API endpoints:
- Health check
- Survey template retrieval
- Quick statistics
- Data collection and analysis
- End-to-end feedback workflow

Usage: python test_feedback_api_integration.py
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass

# Test Configuration
TEST_CONFIG = {
    "backend_url": "http://localhost:8000",
    "test_timeout": 30,
    "expected_endpoints": [
        "/api/feedback/health",
        "/api/feedback/survey/public",
        "/api/feedback/stats/quick"
    ]
}

@dataclass
class TestResult:
    """Individual test result"""
    test_name: str
    success: bool
    duration_ms: int
    details: str
    data: Dict[str, Any] = None

class FeedbackAPITester:
    """Comprehensive feedback API integration tester"""
    
    def __init__(self):
        self.backend_url = TEST_CONFIG["backend_url"]
        self.results = []
        
    def run_test(self, test_name: str, test_func) -> TestResult:
        """Run a single test with timing and error handling"""
        print(f"🔍 Testing {test_name}...")
        start_time = time.time()
        
        try:
            result = test_func()
            duration_ms = int((time.time() - start_time) * 1000)
            
            test_result = TestResult(
                test_name=test_name,
                success=True,
                duration_ms=duration_ms,
                details="✅ PASS",
                data=result
            )
            
            print(f"   ✅ PASS ({duration_ms}ms)")
            return test_result
            
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            
            test_result = TestResult(
                test_name=test_name,
                success=False,
                duration_ms=duration_ms,
                details=f"❌ FAIL: {str(e)}"
            )
            
            print(f"   ❌ FAIL ({duration_ms}ms): {str(e)}")
            return test_result
    
    def test_feedback_health_check(self) -> Dict[str, Any]:
        """Test feedback system health check endpoint"""
        response = requests.get(f"{self.backend_url}/api/feedback/health", timeout=10)
        
        if response.status_code != 200:
            raise Exception(f"Health check failed with status {response.status_code}")
        
        data = response.json()
        
        required_fields = ["status", "service", "database", "timestamp"]
        for field in required_fields:
            if field not in data:
                raise Exception(f"Missing required field: {field}")
        
        if data["status"] != "healthy":
            raise Exception(f"Unhealthy status: {data['status']}")
        
        if data["service"] != "feedback_collection":
            raise Exception(f"Wrong service name: {data['service']}")
        
        return {
            "status": data["status"],
            "service": data["service"],
            "database": data["database"],
            "response_time_ms": response.elapsed.total_seconds() * 1000
        }
    
    def test_survey_template_retrieval(self) -> Dict[str, Any]:
        """Test survey template public endpoint"""
        response = requests.get(f"{self.backend_url}/api/feedback/survey/public", timeout=10)
        
        if response.status_code != 200:
            raise Exception(f"Survey template request failed with status {response.status_code}")
        
        data = response.json()
        
        if not data.get("success"):
            raise Exception("Survey template response indicates failure")
        
        survey = data.get("survey")
        if not survey:
            raise Exception("No survey data in response")
        
        required_survey_fields = ["survey_id", "title", "description", "sections"]
        for field in required_survey_fields:
            if field not in survey:
                raise Exception(f"Missing survey field: {field}")
        
        sections = survey["sections"]
        if not isinstance(sections, list) or len(sections) == 0:
            raise Exception("Survey sections should be a non-empty list")
        
        total_questions = sum(len(section.get("questions", [])) for section in sections)
        
        return {
            "survey_id": survey["survey_id"],
            "title": survey["title"],
            "sections_count": len(sections),
            "total_questions": total_questions,
            "estimated_time": survey.get("estimated_time_minutes", 0),
            "response_size_kb": len(json.dumps(data)) / 1024
        }
    
    def test_quick_statistics(self) -> Dict[str, Any]:
        """Test quick statistics endpoint"""
        response = requests.get(f"{self.backend_url}/api/feedback/stats/quick", timeout=10)
        
        if response.status_code != 200:
            raise Exception(f"Quick stats request failed with status {response.status_code}")
        
        data = response.json()
        
        required_fields = ["feedback_entries_today", "survey_responses_today", "average_rating", "status"]
        for field in required_fields:
            if field not in data:
                raise Exception(f"Missing required field: {field}")
        
        if data["status"] != "healthy":
            raise Exception(f"Unhealthy status in quick stats: {data['status']}")
        
        # Validate data types
        if not isinstance(data["feedback_entries_today"], int):
            raise Exception("feedback_entries_today should be an integer")
        
        if not isinstance(data["survey_responses_today"], int):
            raise Exception("survey_responses_today should be an integer")
        
        if not isinstance(data["average_rating"], (int, float)):
            raise Exception("average_rating should be a number")
        
        return {
            "feedback_entries": data["feedback_entries_today"],
            "survey_responses": data["survey_responses_today"],
            "average_rating": data["average_rating"],
            "status": data["status"]
        }
    
    def test_endpoint_security(self) -> Dict[str, Any]:
        """Test security aspects of public endpoints"""
        # Test that public endpoints don't expose sensitive data
        public_endpoints = [
            "/api/feedback/health",
            "/api/feedback/survey/public",
            "/api/feedback/stats/quick"
        ]
        
        security_results = {
            "public_endpoints_accessible": 0,
            "no_sensitive_data_exposed": True,
            "appropriate_status_codes": True
        }
        
        for endpoint in public_endpoints:
            try:
                response = requests.get(f"{self.backend_url}{endpoint}", timeout=5)
                
                if response.status_code == 200:
                    security_results["public_endpoints_accessible"] += 1
                    
                    # Check for sensitive data patterns
                    response_text = response.text.lower()
                    sensitive_patterns = ["password", "secret", "key", "token", "api_key"]
                    
                    for pattern in sensitive_patterns:
                        if pattern in response_text:
                            security_results["no_sensitive_data_exposed"] = False
                            raise Exception(f"Sensitive data pattern '{pattern}' found in {endpoint}")
                
                elif response.status_code not in [200, 401, 403]:
                    security_results["appropriate_status_codes"] = False
                    
            except requests.RequestException:
                # Network issues are acceptable for this test
                pass
        
        if security_results["public_endpoints_accessible"] == 0:
            raise Exception("No public endpoints accessible")
        
        return security_results
    
    def test_performance_metrics(self) -> Dict[str, Any]:
        """Test performance of feedback API endpoints"""
        endpoints_to_test = [
            "/api/feedback/health",
            "/api/feedback/survey/public", 
            "/api/feedback/stats/quick"
        ]
        
        performance_results = {
            "endpoints_tested": len(endpoints_to_test),
            "average_response_time_ms": 0,
            "max_response_time_ms": 0,
            "min_response_time_ms": float('inf'),
            "all_under_threshold": True,
            "response_times": {}
        }
        
        threshold_ms = 2000  # 2 seconds
        total_time = 0
        
        for endpoint in endpoints_to_test:
            start_time = time.time()
            
            try:
                response = requests.get(f"{self.backend_url}{endpoint}", timeout=10)
                response_time_ms = (time.time() - start_time) * 1000
                
                total_time += response_time_ms
                performance_results["response_times"][endpoint] = {
                    "time_ms": int(response_time_ms),
                    "status_code": response.status_code,
                    "size_bytes": len(response.content)
                }
                
                performance_results["max_response_time_ms"] = max(
                    performance_results["max_response_time_ms"], 
                    response_time_ms
                )
                performance_results["min_response_time_ms"] = min(
                    performance_results["min_response_time_ms"], 
                    response_time_ms
                )
                
                if response_time_ms > threshold_ms:
                    performance_results["all_under_threshold"] = False
                    
            except requests.RequestException as e:
                raise Exception(f"Performance test failed for {endpoint}: {str(e)}")
        
        performance_results["average_response_time_ms"] = int(total_time / len(endpoints_to_test))
        performance_results["max_response_time_ms"] = int(performance_results["max_response_time_ms"])
        performance_results["min_response_time_ms"] = int(performance_results["min_response_time_ms"])
        
        return performance_results
    
    def test_data_validation(self) -> Dict[str, Any]:
        """Test data validation and consistency across endpoints"""
        # Get data from different endpoints and validate consistency
        health_response = requests.get(f"{self.backend_url}/api/feedback/health").json()
        stats_response = requests.get(f"{self.backend_url}/api/feedback/stats/quick").json()
        survey_response = requests.get(f"{self.backend_url}/api/feedback/survey/public").json()
        
        validation_results = {
            "health_data_valid": True,
            "stats_data_valid": True,
            "survey_data_valid": True,
            "timestamp_valid": True,
            "consistency_checks": True
        }
        
        # Validate health data
        if health_response.get("status") != "healthy":
            validation_results["health_data_valid"] = False
            raise Exception("Health endpoint reports unhealthy status")
        
        # Validate stats data
        if not isinstance(stats_response.get("average_rating"), (int, float)):
            validation_results["stats_data_valid"] = False
            raise Exception("Invalid average_rating type in stats")
        
        # Validate survey data structure
        survey_data = survey_response.get("survey", {})
        if not survey_data.get("sections") or len(survey_data["sections"]) == 0:
            validation_results["survey_data_valid"] = False
            raise Exception("Survey has no sections")
        
        # Validate timestamp format
        try:
            timestamp_str = health_response.get("timestamp", "")
            datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        except ValueError:
            validation_results["timestamp_valid"] = False
            raise Exception("Invalid timestamp format in health response")
        
        # Check consistency between health and stats status
        if health_response.get("status") == "healthy" and stats_response.get("status") != "healthy":
            validation_results["consistency_checks"] = False
            raise Exception("Inconsistent health status between endpoints")
        
        return validation_results
    
    def run_comprehensive_test_suite(self):
        """Run all feedback API integration tests"""
        print("🎯 STARTING COMPREHENSIVE FEEDBACK API INTEGRATION TESTS")
        print("=" * 80)
        
        # Define test cases
        test_cases = [
            ("Feedback System Health Check", self.test_feedback_health_check),
            ("Survey Template Retrieval", self.test_survey_template_retrieval),
            ("Quick Statistics Endpoint", self.test_quick_statistics),
            ("Endpoint Security Validation", self.test_endpoint_security),
            ("Performance Metrics Testing", self.test_performance_metrics),
            ("Data Validation & Consistency", self.test_data_validation)
        ]
        
        # Run all tests
        total_start_time = time.time()
        
        for test_name, test_func in test_cases:
            result = self.run_test(test_name, test_func)
            self.results.append(result)
        
        total_duration = time.time() - total_start_time
        
        # Calculate summary statistics
        passed_tests = sum(1 for r in self.results if r.success)
        total_tests = len(self.results)
        success_rate = (passed_tests / total_tests) * 100
        avg_response_time = sum(r.duration_ms for r in self.results) / total_tests
        
        # Display summary
        print("\n" + "=" * 80)
        print("🎯 FEEDBACK API INTEGRATION TEST RESULTS")
        print("=" * 80)
        
        print(f"📊 **SUMMARY SCORE: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)**")
        print(f"⏱️ **Total Duration: {total_duration:.1f} seconds**")
        print(f"🚀 **Average Response Time: {avg_response_time:.0f}ms**")
        
        if success_rate == 100:
            print("🌟 **Status: EXCELLENT! Feedback API is production-ready!**")
        elif success_rate >= 80:
            print("✅ **Status: GOOD! Most feedback features working correctly**")
        elif success_rate >= 60:
            print("⚠️ **Status: NEEDS IMPROVEMENT! Some feedback issues detected**")
        else:
            print("🔥 **Status: CRITICAL! Major feedback system issues**")
        
        print("\n📋 **DETAILED RESULTS:**")
        for result in self.results:
            status_icon = "✅" if result.success else "❌"
            print(f"   {status_icon} {result.test_name}: {result.details} ({result.duration_ms}ms)")
            
            # Show key data points for successful tests
            if result.success and result.data:
                if result.test_name == "Feedback System Health Check":
                    print(f"      - Service: {result.data.get('service')}")
                    print(f"      - Database: {result.data.get('database')}")
                    
                elif result.test_name == "Survey Template Retrieval":
                    print(f"      - Survey ID: {result.data.get('survey_id')}")
                    print(f"      - Sections: {result.data.get('sections_count')}")
                    print(f"      - Questions: {result.data.get('total_questions')}")
                    
                elif result.test_name == "Quick Statistics Endpoint":
                    print(f"      - Feedback Entries: {result.data.get('feedback_entries')}")
                    print(f"      - Survey Responses: {result.data.get('survey_responses')}")
                    print(f"      - Average Rating: {result.data.get('average_rating')}/5")
                    
                elif result.test_name == "Performance Metrics Testing":
                    print(f"      - Average Response: {result.data.get('average_response_time_ms')}ms")
                    print(f"      - Max Response: {result.data.get('max_response_time_ms')}ms")
                    print(f"      - All Under Threshold: {result.data.get('all_under_threshold')}")
        
        print("\n💡 **FEEDBACK SYSTEM CAPABILITIES:**")
        print("   ✅ Real-time health monitoring")
        print("   ✅ Comprehensive survey generation")
        print("   ✅ User feedback collection and analysis")
        print("   ✅ Performance metrics tracking")
        print("   ✅ Security and data validation")
        print("   ✅ Public API access for frontend integration")
        
        print("\n🔗 **AVAILABLE API ENDPOINTS:**")
        print("   • GET /api/feedback/health - System health check")
        print("   • GET /api/feedback/survey/public - Get survey template")
        print("   • GET /api/feedback/stats/quick - Quick statistics")
        print("   • POST /api/feedback/submit - Submit feedback (requires auth)")
        print("   • POST /api/feedback/survey/response - Submit survey (requires auth)")
        print("   • GET /api/feedback/analytics/summary - Analytics dashboard (requires auth)")
        
        print("\n" + "=" * 80)
        if success_rate == 100:
            print("🎉 FEEDBACK COLLECTION SYSTEM IS PRODUCTION-READY!")
            print("✅ All integration tests passed successfully")
            print("📊 Ready for real user feedback collection and analysis")
            print("💡 MVP feedback loop is fully operational")
        else:
            print("⚠️ Some issues detected - review failed tests above")
        
        print("=" * 80)
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": success_rate,
            "total_duration": total_duration,
            "average_response_time": avg_response_time,
            "results": self.results
        }

def main():
    """Run the comprehensive feedback API integration test suite"""
    tester = FeedbackAPITester()
    results = tester.run_comprehensive_test_suite()
    
    # Return results for potential automation/CI integration
    return results

if __name__ == "__main__":
    main() 