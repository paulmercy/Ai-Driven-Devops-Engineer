#!/usr/bin/env python3
"""
Comprehensive Grafana Dashboard Diagnostic Tool
Tests all aspects of the Grafana dashboard configuration
"""

import requests
import json
import time
import sys
from datetime import datetime

class GrafanaDashboardTester:
    def __init__(self):
        self.grafana_url = "http://localhost:3000"
        self.prometheus_url = "http://localhost:9090"
        self.demo_app_url = "http://localhost:8000"
        self.grafana_auth = ("admin", "admin")
        self.results = []
        
    def log_result(self, test_name, status, message, details=None):
        """Log test result"""
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {test_name}: {message}")
        if details:
            print(f"   Details: {details}")
    
    def test_service_connectivity(self):
        """Test connectivity to all services"""
        print("\n🔍 Testing Service Connectivity...")
        
        # Test Grafana
        try:
            response = requests.get(f"{self.grafana_url}/api/health", timeout=10)
            if response.status_code == 200:
                self.log_result("Grafana Connectivity", "PASS", "Grafana is accessible")
            else:
                self.log_result("Grafana Connectivity", "FAIL", f"HTTP {response.status_code}")
        except Exception as e:
            self.log_result("Grafana Connectivity", "FAIL", f"Connection failed: {e}")
        
        # Test Prometheus
        try:
            response = requests.get(f"{self.prometheus_url}/api/v1/query?query=up", timeout=10)
            if response.status_code == 200:
                self.log_result("Prometheus Connectivity", "PASS", "Prometheus is accessible")
            else:
                self.log_result("Prometheus Connectivity", "FAIL", f"HTTP {response.status_code}")
        except Exception as e:
            self.log_result("Prometheus Connectivity", "FAIL", f"Connection failed: {e}")
        
        # Test Demo App
        try:
            response = requests.get(f"{self.demo_app_url}/health", timeout=10)
            if response.status_code == 200:
                self.log_result("Demo App Connectivity", "PASS", "Demo app is accessible")
            else:
                self.log_result("Demo App Connectivity", "FAIL", f"HTTP {response.status_code}")
        except Exception as e:
            self.log_result("Demo App Connectivity", "FAIL", f"Connection failed: {e}")
    
    def test_grafana_datasource(self):
        """Test Grafana datasource configuration"""
        print("\n🔗 Testing Grafana Datasource...")
        
        try:
            response = requests.get(
                f"{self.grafana_url}/api/datasources",
                auth=self.grafana_auth,
                timeout=10
            )
            
            if response.status_code == 200:
                datasources = response.json()
                prometheus_ds = None
                
                for ds in datasources:
                    if ds.get("type") == "prometheus":
                        prometheus_ds = ds
                        break
                
                if prometheus_ds:
                    self.log_result("Datasource Config", "PASS", "Prometheus datasource found")
                    
                    # Test datasource connectivity
                    ds_id = prometheus_ds.get("id")
                    test_response = requests.get(
                        f"{self.grafana_url}/api/datasources/{ds_id}/health",
                        auth=self.grafana_auth,
                        timeout=10
                    )
                    
                    if test_response.status_code == 200:
                        self.log_result("Datasource Health", "PASS", "Prometheus datasource is healthy")
                    else:
                        self.log_result("Datasource Health", "FAIL", f"Health check failed: {test_response.status_code}")
                else:
                    self.log_result("Datasource Config", "FAIL", "No Prometheus datasource found")
            else:
                self.log_result("Datasource Config", "FAIL", f"Failed to get datasources: {response.status_code}")
                
        except Exception as e:
            self.log_result("Datasource Config", "FAIL", f"Error: {e}")
    
    def test_prometheus_metrics(self):
        """Test if Prometheus is collecting metrics from demo app"""
        print("\n📊 Testing Prometheus Metrics...")
        
        # Test basic Prometheus metrics
        metrics_to_test = [
            "up",
            "http_requests_total",
            "suspicious_activity_total",
            "cpu_usage_percent"
        ]
        
        for metric in metrics_to_test:
            try:
                response = requests.get(
                    f"{self.prometheus_url}/api/v1/query",
                    params={"query": metric},
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "success" and data.get("data", {}).get("result"):
                        self.log_result(f"Metric: {metric}", "PASS", "Metric available with data")
                    else:
                        self.log_result(f"Metric: {metric}", "WARN", "Metric exists but no data")
                else:
                    self.log_result(f"Metric: {metric}", "FAIL", f"Query failed: {response.status_code}")
                    
            except Exception as e:
                self.log_result(f"Metric: {metric}", "FAIL", f"Error: {e}")
    
    def test_demo_app_metrics(self):
        """Test demo app metrics endpoint"""
        print("\n🎯 Testing Demo App Metrics...")
        
        try:
            response = requests.get(f"{self.demo_app_url}/metrics", timeout=10)
            if response.status_code == 200:
                metrics_text = response.text
                
                # Check for key metrics
                key_metrics = [
                    "http_requests_total",
                    "http_request_duration_seconds",
                    "suspicious_activity_total",
                    "cpu_usage_percent"
                ]
                
                found_metrics = []
                for metric in key_metrics:
                    if metric in metrics_text:
                        found_metrics.append(metric)
                
                if found_metrics:
                    self.log_result("Demo App Metrics", "PASS", f"Found {len(found_metrics)}/{len(key_metrics)} key metrics")
                else:
                    self.log_result("Demo App Metrics", "FAIL", "No key metrics found in response")
                    
            else:
                self.log_result("Demo App Metrics", "FAIL", f"Metrics endpoint returned {response.status_code}")
                
        except Exception as e:
            self.log_result("Demo App Metrics", "FAIL", f"Error: {e}")
    
    def test_dashboard_json(self):
        """Test dashboard JSON validity"""
        print("\n📋 Testing Dashboard JSON...")
        
        try:
            with open("grafana/dashboards/devsecops-dashboard.json", "r") as f:
                dashboard_json = json.load(f)
            
            # Basic structure checks
            required_fields = ["id", "title", "panels", "time"]
            missing_fields = [field for field in required_fields if field not in dashboard_json]
            
            if not missing_fields:
                self.log_result("Dashboard JSON Structure", "PASS", "All required fields present")
                
                # Check panels
                panels = dashboard_json.get("panels", [])
                if panels:
                    self.log_result("Dashboard Panels", "PASS", f"Found {len(panels)} panels")
                    
                    # Check each panel for datasource
                    panels_with_datasource = 0
                    for panel in panels:
                        if panel.get("datasource", {}).get("type") == "prometheus":
                            panels_with_datasource += 1
                    
                    self.log_result("Panel Datasources", "PASS", f"{panels_with_datasource}/{len(panels)} panels have Prometheus datasource")
                else:
                    self.log_result("Dashboard Panels", "FAIL", "No panels found")
            else:
                self.log_result("Dashboard JSON Structure", "FAIL", f"Missing fields: {missing_fields}")
                
        except FileNotFoundError:
            self.log_result("Dashboard JSON", "FAIL", "Dashboard JSON file not found")
        except json.JSONDecodeError as e:
            self.log_result("Dashboard JSON", "FAIL", f"Invalid JSON: {e}")
        except Exception as e:
            self.log_result("Dashboard JSON", "FAIL", f"Error: {e}")
    
    def generate_test_data(self):
        """Generate test data by calling demo app endpoints"""
        print("\n🚀 Generating Test Data...")
        
        try:
            # Generate some HTTP requests
            for i in range(5):
                requests.get(f"{self.demo_app_url}/health", timeout=5)
                requests.get(f"{self.demo_app_url}/api/security-status", timeout=5)
            
            # Simulate some attacks
            attack_types = ["sql_injection", "xss_attack", "brute_force"]
            for attack in attack_types:
                requests.post(
                    f"{self.demo_app_url}/api/simulate/attack",
                    json={"type": attack, "description": f"Test {attack}"},
                    timeout=5
                )
            
            self.log_result("Test Data Generation", "PASS", "Generated HTTP requests and security events")
            
        except Exception as e:
            self.log_result("Test Data Generation", "FAIL", f"Error: {e}")
    
    def run_all_tests(self):
        """Run all diagnostic tests"""
        print("🛡️  Grafana Dashboard Diagnostic Tool")
        print("=" * 50)
        
        self.test_service_connectivity()
        self.test_grafana_datasource()
        self.test_prometheus_metrics()
        self.test_demo_app_metrics()
        self.test_dashboard_json()
        self.generate_test_data()
        
        # Summary
        print("\n📊 Test Summary")
        print("=" * 30)
        
        passed = len([r for r in self.results if r["status"] == "PASS"])
        failed = len([r for r in self.results if r["status"] == "FAIL"])
        warnings = len([r for r in self.results if r["status"] == "WARN"])
        
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️  Warnings: {warnings}")
        print(f"📋 Total: {len(self.results)}")
        
        if failed == 0:
            print("\n🎉 All critical tests passed! Dashboard should be working.")
            return 0
        else:
            print(f"\n⚠️  {failed} tests failed. Check the issues above.")
            return 1

if __name__ == "__main__":
    tester = GrafanaDashboardTester()
    sys.exit(tester.run_all_tests())
