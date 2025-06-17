#!/usr/bin/env python3
"""
PRODUCTION CONNECTIONS TEST SUITE
Comprehensive validation of Neon Database and Clerk Authentication connections

Tests include:
- Neon Database Connection & Health
- Clerk Authentication Setup  
- Frontend Route Accessibility
- Environment Configuration
- Cross-System Integration
- Production Readiness Validation

Usage: python test_production_connections.py
"""

import requests
import json
import os
import time
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass
import subprocess
import psycopg2
from urllib.parse import urlparse

# Test Configuration
TEST_CONFIG = {
    "backend_url": "http://localhost:8000",
    "frontend_url": "http://localhost:3001",
    "test_timeout": 30
}

@dataclass
class TestResult:
    """Individual test result"""
    test_name: str
    success: bool
    duration_ms: int
    details: str
    data: Dict[str, Any] = None

class ProductionConnectionTester:
    """Comprehensive production connections tester"""
    
    def __init__(self):
        self.backend_url = TEST_CONFIG["backend_url"]
        self.frontend_url = TEST_CONFIG["frontend_url"]
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
    
    def test_neon_database_connection(self) -> Dict[str, Any]:
        """Test direct connection to Neon database"""
        # Get database URL from environment
        database_url = os.getenv("DATABASE_URL")
        
        if not database_url:
            raise Exception("DATABASE_URL not found in environment")
        
        if "neon.tech" not in database_url:
            raise Exception(f"Database URL does not appear to be Neon: {database_url[:50]}...")
        
        # Parse the URL
        parsed = urlparse(database_url)
        
        try:
            # Test direct PostgreSQL connection
            conn = psycopg2.connect(database_url)
            cursor = conn.cursor()
            
            # Test basic query
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            
            # Test table existence
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            # Close connection
            cursor.close()
            conn.close()
            
            return {
                "database_type": "Neon PostgreSQL",
                "host": parsed.hostname,
                "database": parsed.path.lstrip('/'),
                "version": version,
                "tables_count": len(tables),
                "tables": tables[:5],  # Show first 5 tables
                "ssl_mode": "require" if "sslmode=require" in database_url else "not specified"
            }
            
        except Exception as e:
            raise Exception(f"Direct database connection failed: {str(e)}")
    
    def test_backend_database_health(self) -> Dict[str, Any]:
        """Test backend database health endpoint"""
        response = requests.get(f"{self.backend_url}/health/database", timeout=10)
        
        if response.status_code != 200:
            raise Exception(f"Database health check failed with status {response.status_code}")
        
        data = response.json()
        
        if data.get("status") != "healthy":
            raise Exception(f"Database reports unhealthy status: {data.get('status')}")
        
        return {
            "status": data.get("status"),
            "connection": data.get("database"),
            "character_count": data.get("character_count", 0),
            "response_time_ms": response.elapsed.total_seconds() * 1000
        }
    
    def test_clerk_authentication_setup(self) -> Dict[str, Any]:
        """Test Clerk authentication configuration"""
        # Check environment variables
        clerk_publishable = os.getenv("NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY")
        clerk_secret = os.getenv("CLERK_SECRET_KEY")
        
        if not clerk_publishable:
            raise Exception("NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY not found in environment")
        
        if not clerk_secret:
            raise Exception("CLERK_SECRET_KEY not found in environment")
        
        if not clerk_publishable.startswith("pk_test_"):
            raise Exception("Clerk publishable key doesn't appear to be a test key")
        
        if not clerk_secret.startswith("sk_test_"):
            raise Exception("Clerk secret key doesn't appear to be a test key")
        
        # Test frontend Clerk integration
        response = requests.get(f"{self.frontend_url}/sign-in", timeout=10)
        
        if response.status_code != 200:
            raise Exception(f"Frontend sign-in page failed with status {response.status_code}")
        
        # Check for Clerk headers
        clerk_auth_status = response.headers.get("x-clerk-auth-status")
        clerk_auth_reason = response.headers.get("x-clerk-auth-reason")
        
        if not clerk_auth_status:
            raise Exception("Missing Clerk auth status header")
        
        return {
            "publishable_key": clerk_publishable[:20] + "...",
            "secret_key": clerk_secret[:20] + "...",
            "auth_status": clerk_auth_status,
            "auth_reason": clerk_auth_reason,
            "frontend_integration": "active",
            "environment": "test" if "test" in clerk_publishable else "production"
        }
    
    def test_frontend_routes_accessibility(self) -> Dict[str, Any]:
        """Test frontend route accessibility"""
        routes_to_test = [
            ("/", "Home"),
            ("/sign-in", "Sign In"),
            ("/sign-up", "Sign Up"),
            ("/dashboard", "Dashboard"),
            ("/character/create", "Character Creation")
        ]
        
        route_results = {
            "total_routes": len(routes_to_test),
            "accessible_routes": 0,
            "auth_protected_routes": 0,
            "missing_routes": 0,
            "route_details": {}
        }
        
        for route, name in routes_to_test:
            try:
                response = requests.get(f"{self.frontend_url}{route}", timeout=5)
                
                route_info = {
                    "status_code": response.status_code,
                    "response_time_ms": int(response.elapsed.total_seconds() * 1000),
                    "auth_status": response.headers.get("x-clerk-auth-status", "none"),
                    "content_length": len(response.content)
                }
                
                if response.status_code == 200:
                    route_results["accessible_routes"] += 1
                    route_info["status"] = "accessible"
                elif response.status_code == 404:
                    route_results["missing_routes"] += 1
                    route_info["status"] = "missing"
                elif response.status_code in [401, 403]:
                    route_results["auth_protected_routes"] += 1
                    route_info["status"] = "auth_protected"
                else:
                    route_info["status"] = f"unexpected_{response.status_code}"
                
                route_results["route_details"][route] = route_info
                
            except Exception as e:
                route_results["route_details"][route] = {
                    "status": "error",
                    "error": str(e)
                }
        
        # Analyze results
        if route_results["missing_routes"] > 0:
            missing_routes = [route for route, details in route_results["route_details"].items() 
                            if details.get("status") == "missing"]
            raise Exception(f"Found {route_results['missing_routes']} missing routes: {missing_routes}")
        
        return route_results
    
    def test_environment_configuration(self) -> Dict[str, Any]:
        """Test environment configuration completeness"""
        required_vars = [
            "DATABASE_URL",
            "NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY", 
            "CLERK_SECRET_KEY"
        ]
        
        optional_vars = [
            "ANTHROPIC_API_KEY",
            "OPENAI_API_KEY",
            "REDIS_URL",
            "ENVIRONMENT",
            "DEBUG"
        ]
        
        env_status = {
            "required_vars": {},
            "optional_vars": {},
            "missing_required": [],
            "total_configured": 0
        }
        
        # Check required variables
        for var in required_vars:
            value = os.getenv(var)
            if value:
                env_status["required_vars"][var] = {
                    "configured": True,
                    "length": len(value),
                    "preview": value[:20] + "..." if len(value) > 20 else value
                }
                env_status["total_configured"] += 1
            else:
                env_status["required_vars"][var] = {"configured": False}
                env_status["missing_required"].append(var)
        
        # Check optional variables
        for var in optional_vars:
            value = os.getenv(var)
            if value:
                env_status["optional_vars"][var] = {
                    "configured": True,
                    "length": len(value),
                    "preview": value[:20] + "..." if len(value) > 20 else value
                }
                env_status["total_configured"] += 1
            else:
                env_status["optional_vars"][var] = {"configured": False}
        
        if env_status["missing_required"]:
            raise Exception(f"Missing required environment variables: {env_status['missing_required']}")
        
        return env_status
    
    def test_cross_system_integration(self) -> Dict[str, Any]:
        """Test integration between all systems"""
        integration_results = {
            "backend_frontend_communication": False,
            "database_backend_integration": False,
            "auth_system_integration": False,
            "api_endpoints_functional": False,
            "overall_integration": False
        }
        
        # Test backend-frontend communication
        try:
            backend_response = requests.get(f"{self.backend_url}/health", timeout=5)
            frontend_response = requests.get(f"{self.frontend_url}/", timeout=5)
            
            if backend_response.status_code == 200 and frontend_response.status_code == 200:
                integration_results["backend_frontend_communication"] = True
        except:
            pass
        
        # Test database-backend integration
        try:
            db_response = requests.get(f"{self.backend_url}/health/database", timeout=5)
            if db_response.status_code == 200 and db_response.json().get("status") == "healthy":
                integration_results["database_backend_integration"] = True
        except:
            pass
        
        # Test auth system integration
        try:
            auth_response = requests.get(f"{self.frontend_url}/sign-in", timeout=5)
            if (auth_response.status_code == 200 and 
                auth_response.headers.get("x-clerk-auth-status")):
                integration_results["auth_system_integration"] = True
        except:
            pass
        
        # Test API endpoints functionality
        try:
            api_tests = [
                f"{self.backend_url}/api/characters/options",
                f"{self.backend_url}/api/dice/simple",
                f"{self.backend_url}/api/redis/health"
            ]
            
            all_working = True
            for endpoint in api_tests:
                try:
                    response = requests.post(endpoint, json={}, timeout=5)
                    if response.status_code not in [200, 422]:  # 422 is validation error, which is ok
                        all_working = False
                        break
                except:
                    all_working = False
                    break
            
            integration_results["api_endpoints_functional"] = all_working
        except:
            pass
        
        # Overall integration score
        successful_integrations = sum(integration_results.values())
        integration_results["overall_integration"] = successful_integrations >= 3
        integration_results["integration_score"] = f"{successful_integrations}/4"
        
        if not integration_results["overall_integration"]:
            failed_systems = [k for k, v in integration_results.items() if not v and k != "overall_integration"]
            raise Exception(f"Integration failures detected in: {failed_systems}")
        
        return integration_results
    
    def test_production_readiness(self) -> Dict[str, Any]:
        """Test overall production readiness"""
        readiness_checks = {
            "database_connection": False,
            "authentication_system": False,
            "frontend_accessibility": False,
            "api_functionality": False,
            "environment_setup": False,
            "performance_acceptable": False
        }
        
        # Database connection check
        try:
            db_response = requests.get(f"{self.backend_url}/health/database", timeout=5)
            readiness_checks["database_connection"] = (
                db_response.status_code == 200 and 
                db_response.json().get("status") == "healthy"
            )
        except:
            pass
        
        # Authentication system check
        try:
            auth_response = requests.get(f"{self.frontend_url}/sign-in", timeout=5)
            readiness_checks["authentication_system"] = (
                auth_response.status_code == 200 and
                "x-clerk-auth-status" in auth_response.headers
            )
        except:
            pass
        
        # Frontend accessibility check
        try:
            frontend_response = requests.get(f"{self.frontend_url}/", timeout=5)
            readiness_checks["frontend_accessibility"] = frontend_response.status_code == 200
        except:
            pass
        
        # API functionality check
        try:
            api_response = requests.get(f"{self.backend_url}/api/characters/options", timeout=5)
            readiness_checks["api_functionality"] = api_response.status_code == 200
        except:
            pass
        
        # Environment setup check
        required_env = ["DATABASE_URL", "NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY", "CLERK_SECRET_KEY"]
        readiness_checks["environment_setup"] = all(os.getenv(var) for var in required_env)
        
        # Performance check
        try:
            start_time = time.time()
            requests.get(f"{self.backend_url}/health", timeout=5)
            response_time = (time.time() - start_time) * 1000
            readiness_checks["performance_acceptable"] = response_time < 1000  # Under 1 second
        except:
            pass
        
        # Calculate readiness score
        passed_checks = sum(readiness_checks.values())
        total_checks = len(readiness_checks)
        readiness_score = (passed_checks / total_checks) * 100
        
        readiness_results = {
            "readiness_score": readiness_score,
            "passed_checks": passed_checks,
            "total_checks": total_checks,
            "checks": readiness_checks,
            "production_ready": readiness_score >= 80
        }
        
        if not readiness_results["production_ready"]:
            failed_checks = [k for k, v in readiness_checks.items() if not v]
            raise Exception(f"Production readiness below 80%. Failed checks: {failed_checks}")
        
        return readiness_results
    
    def run_comprehensive_test_suite(self):
        """Run all production connection tests"""
        print("🎯 STARTING COMPREHENSIVE PRODUCTION CONNECTIONS TESTS")
        print("=" * 80)
        
        # Define test cases
        test_cases = [
            ("Neon Database Connection", self.test_neon_database_connection),
            ("Backend Database Health", self.test_backend_database_health),
            ("Clerk Authentication Setup", self.test_clerk_authentication_setup),
            ("Frontend Routes Accessibility", self.test_frontend_routes_accessibility),
            ("Environment Configuration", self.test_environment_configuration),
            ("Cross-System Integration", self.test_cross_system_integration),
            ("Production Readiness", self.test_production_readiness)
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
        print("🎯 PRODUCTION CONNECTIONS TEST RESULTS")
        print("=" * 80)
        
        print(f"📊 **SUMMARY SCORE: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)**")
        print(f"⏱️ **Total Duration: {total_duration:.1f} seconds**")
        print(f"🚀 **Average Response Time: {avg_response_time:.0f}ms**")
        
        if success_rate == 100:
            print("🌟 **Status: EXCELLENT! All production connections verified!**")
        elif success_rate >= 80:
            print("✅ **Status: GOOD! Most connections working correctly**")
        elif success_rate >= 60:
            print("⚠️ **Status: NEEDS ATTENTION! Some connection issues detected**")
        else:
            print("🔥 **Status: CRITICAL! Major connection issues**")
        
        print("\n📋 **DETAILED RESULTS:**")
        for result in self.results:
            status_icon = "✅" if result.success else "❌"
            print(f"   {status_icon} {result.test_name}: {result.details} ({result.duration_ms}ms)")
            
            # Show key data points for successful tests
            if result.success and result.data:
                if result.test_name == "Neon Database Connection":
                    print(f"      - Database: {result.data.get('database_type')}")
                    print(f"      - Host: {result.data.get('host')}")
                    print(f"      - Tables: {result.data.get('tables_count')}")
                    
                elif result.test_name == "Clerk Authentication Setup":
                    print(f"      - Environment: {result.data.get('environment')}")
                    print(f"      - Auth Status: {result.data.get('auth_status')}")
                    print(f"      - Integration: {result.data.get('frontend_integration')}")
                    
                elif result.test_name == "Frontend Routes Accessibility":
                    print(f"      - Accessible Routes: {result.data.get('accessible_routes')}")
                    print(f"      - Auth Protected: {result.data.get('auth_protected_routes')}")
                    print(f"      - Missing Routes: {result.data.get('missing_routes')}")
                    
                elif result.test_name == "Production Readiness":
                    print(f"      - Readiness Score: {result.data.get('readiness_score'):.1f}%")
                    print(f"      - Passed Checks: {result.data.get('passed_checks')}/{result.data.get('total_checks')}")
        
        print("\n💡 **CONNECTION STATUS:**")
        neon_connected = any(r.success and r.test_name == "Neon Database Connection" for r in self.results)
        clerk_connected = any(r.success and r.test_name == "Clerk Authentication Setup" for r in self.results)
        
        print(f"   {'✅' if neon_connected else '❌'} Neon Database - {'Connected' if neon_connected else 'Disconnected'}")
        print(f"   {'✅' if clerk_connected else '❌'} Clerk Authentication - {'Connected' if clerk_connected else 'Disconnected'}")
        
        print("\n" + "=" * 80)
        if success_rate == 100:
            print("🎉 ALL PRODUCTION CONNECTIONS VERIFIED!")
            print("✅ Neon database and Clerk authentication fully operational")
            print("🚀 System ready for production deployment")
        else:
            print("⚠️ Some connection issues detected - review failed tests above")
        
        print("=" * 80)
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": success_rate,
            "total_duration": total_duration,
            "average_response_time": avg_response_time,
            "neon_connected": neon_connected,
            "clerk_connected": clerk_connected,
            "results": self.results
        }

def main():
    """Run the comprehensive production connections test suite"""
    tester = ProductionConnectionTester()
    results = tester.run_comprehensive_test_suite()
    
    # Return results for potential automation/CI integration
    return results

if __name__ == "__main__":
    main() 