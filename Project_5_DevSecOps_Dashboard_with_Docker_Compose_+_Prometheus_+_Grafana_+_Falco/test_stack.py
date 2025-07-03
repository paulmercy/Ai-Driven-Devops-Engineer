#!/usr/bin/env python3
"""
DevSecOps Stack Test Suite
Comprehensive testing for the monitoring and security stack
"""

import requests
import time
import json
import subprocess
import sys
from datetime import datetime
import threading

class StackTester:
    def __init__(self):
        self.base_url = "http://localhost:3000"
        self.grafana_url = "http://localhost:3001"
        self.prometheus_url = "http://localhost:9090"
        self.cadvisor_url = "http://localhost:8080"
        self.node_exporter_url = "http://localhost:9100"
        
        self.test_results = []
        
    def log_test(self, test_name, success, message=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        timestamp = datetime.now().strftime("%H:%M:%S")
        result = {
            "timestamp": timestamp,
            "test": test_name,
            "success": success,
            "message": message
        }
        self.test_results.append(result)
        print(f"[{timestamp}] {status}: {test_name} {message}")
        
    def test_service_health(self):
        """Test all service health endpoints"""
        print("\n🔍 Testing Service Health...")
        
        services = {
            "Demo Application": f"{self.base_url}/health",
            "Grafana": f"{self.grafana_url}/api/health",
            "Prometheus": f"{self.prometheus_url}/-/healthy",
            "cAdvisor": f"{self.cadvisor_url}/healthz",
            "Node Exporter": f"{self.node_exporter_url}/metrics"
        }
        
        for service, url in services.items():
            try:
                response = requests.get(url, timeout=10)
                success = response.status_code == 200
                self.log_test(
                    f"{service} Health Check",
                    success,
                    f"(Status: {response.status_code})"
                )
            except Exception as e:
                self.log_test(f"{service} Health Check", False, f"(Error: {e})")
    
    def test_prometheus_targets(self):
        """Test Prometheus target discovery"""
        print("\n📊 Testing Prometheus Targets...")
        
        try:
            response = requests.get(f"{self.prometheus_url}/api/v1/targets", timeout=10)
            if response.status_code == 200:
                data = response.json()
                targets = data.get("data", {}).get("activeTargets", [])
                
                expected_jobs = ["demo-app", "prometheus", "node-exporter", "cadvisor"]
                found_jobs = set()
                
                for target in targets:
                    job = target.get("labels", {}).get("job", "")
                    if job:
                        found_jobs.add(job)
                        health = target.get("health", "unknown")
                        self.log_test(
                            f"Prometheus Target: {job}",
                            health == "up",
                            f"(Health: {health})"
                        )
                
                # Check if all expected jobs are found
                missing_jobs = set(expected_jobs) - found_jobs
                if missing_jobs:
                    self.log_test(
                        "Prometheus Target Discovery",
                        False,
                        f"(Missing jobs: {missing_jobs})"
                    )
                else:
                    self.log_test("Prometheus Target Discovery", True)
                    
            else:
                self.log_test("Prometheus Targets API", False, f"(Status: {response.status_code})")
                
        except Exception as e:
            self.log_test("Prometheus Targets API", False, f"(Error: {e})")
    
    def test_metrics_collection(self):
        """Test metrics collection from application"""
        print("\n📈 Testing Metrics Collection...")
        
        # Generate some requests first
        for _ in range(5):
            try:
                requests.get(f"{self.base_url}/api/data", timeout=5)
            except:
                pass
        
        time.sleep(5)  # Wait for metrics to be scraped
        
        # Test application metrics endpoint
        try:
            response = requests.get(f"{self.base_url}/metrics", timeout=10)
            success = response.status_code == 200
            self.log_test("Application Metrics Endpoint", success)
            
            if success:
                metrics_text = response.text
                expected_metrics = [
                    "http_requests_total",
                    "http_request_duration_seconds",
                    "cpu_usage_percent",
                    "memory_usage_bytes",
                    "suspicious_activity_total"
                ]
                
                for metric in expected_metrics:
                    found = metric in metrics_text
                    self.log_test(f"Metric: {metric}", found)
                    
        except Exception as e:
            self.log_test("Application Metrics Endpoint", False, f"(Error: {e})")
        
        # Test Prometheus query API
        try:
            query = "up"
            response = requests.get(
                f"{self.prometheus_url}/api/v1/query",
                params={"query": query},
                timeout=10
            )
            success = response.status_code == 200
            self.log_test("Prometheus Query API", success)
            
            if success:
                data = response.json()
                result = data.get("data", {}).get("result", [])
                self.log_test("Prometheus Query Results", len(result) > 0, f"({len(result)} results)")
                
        except Exception as e:
            self.log_test("Prometheus Query API", False, f"(Error: {e})")
    
    def test_grafana_datasources(self):
        """Test Grafana datasource configuration"""
        print("\n📊 Testing Grafana Configuration...")
        
        try:
            # Test Grafana API with basic auth
            auth = ("admin", "admin123")
            response = requests.get(
                f"{self.grafana_url}/api/datasources",
                auth=auth,
                timeout=10
            )
            
            success = response.status_code == 200
            self.log_test("Grafana Datasources API", success)
            
            if success:
                datasources = response.json()
                prometheus_found = any(
                    ds.get("type") == "prometheus" for ds in datasources
                )
                self.log_test("Prometheus Datasource", prometheus_found)
                
        except Exception as e:
            self.log_test("Grafana Datasources API", False, f"(Error: {e})")
    
    def test_security_simulation(self):
        """Test security attack simulation"""
        print("\n🚨 Testing Security Simulation...")
        
        attacks = [
            {"type": "sql_injection", "name": "SQL Injection"},
            {"type": "privilege_escalation", "name": "Privilege Escalation"},
            {"type": "file_access", "name": "File Access"},
            {"type": "network_scan", "name": "Network Scan"}
        ]
        
        for attack in attacks:
            try:
                response = requests.post(
                    f"{self.base_url}/simulate/attack",
                    json={"type": attack["type"]},
                    timeout=10
                )
                success = response.status_code == 200
                self.log_test(f"Attack Simulation: {attack['name']}", success)
                
            except Exception as e:
                self.log_test(f"Attack Simulation: {attack['name']}", False, f"(Error: {e})")
        
        # Wait and check if suspicious activity metrics increased
        time.sleep(5)
        try:
            response = requests.get(
                f"{self.prometheus_url}/api/v1/query",
                params={"query": "suspicious_activity_total"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("data", {}).get("result", [])
                has_suspicious_activity = any(
                    float(result.get("value", [0, "0"])[1]) > 0 
                    for result in results
                )
                self.log_test("Suspicious Activity Metrics", has_suspicious_activity)
            else:
                self.log_test("Suspicious Activity Metrics", False, "Query failed")
                
        except Exception as e:
            self.log_test("Suspicious Activity Metrics", False, f"(Error: {e})")
    
    def test_container_monitoring(self):
        """Test container monitoring with cAdvisor"""
        print("\n🐳 Testing Container Monitoring...")
        
        try:
            response = requests.get(f"{self.cadvisor_url}/api/v1.3/containers", timeout=10)
            success = response.status_code == 200
            self.log_test("cAdvisor API", success)
            
            if success:
                containers = response.json()
                container_count = len(containers)
                self.log_test("Container Discovery", container_count > 0, f"({container_count} containers)")
                
        except Exception as e:
            self.log_test("cAdvisor API", False, f"(Error: {e})")
    
    def test_falco_integration(self):
        """Test Falco security monitoring"""
        print("\n🛡️ Testing Falco Integration...")
        
        try:
            # Check if Falco container is running
            result = subprocess.run(
                ["docker", "ps", "--filter", "name=falco", "--format", "{{.Status}}"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and "Up" in result.stdout:
                self.log_test("Falco Container Status", True, "(Running)")
                
                # Check Falco logs for recent activity
                log_result = subprocess.run(
                    ["docker", "logs", "--tail", "10", "falco"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if log_result.returncode == 0:
                    has_logs = len(log_result.stdout.strip()) > 0
                    self.log_test("Falco Log Output", has_logs)
                else:
                    self.log_test("Falco Log Output", False, "Cannot read logs")
            else:
                self.log_test("Falco Container Status", False, "(Not running)")
                
        except Exception as e:
            self.log_test("Falco Integration", False, f"(Error: {e})")
    
    def test_alerting_rules(self):
        """Test Prometheus alerting rules"""
        print("\n🚨 Testing Alerting Rules...")
        
        try:
            response = requests.get(f"{self.prometheus_url}/api/v1/rules", timeout=10)
            success = response.status_code == 200
            self.log_test("Prometheus Rules API", success)
            
            if success:
                data = response.json()
                groups = data.get("data", {}).get("groups", [])
                rule_count = sum(len(group.get("rules", [])) for group in groups)
                self.log_test("Alert Rules Loaded", rule_count > 0, f"({rule_count} rules)")
                
                # Check for specific rule groups
                group_names = [group.get("name", "") for group in groups]
                expected_groups = ["application_alerts", "security_alerts", "infrastructure_alerts"]
                
                for group_name in expected_groups:
                    found = group_name in group_names
                    self.log_test(f"Rule Group: {group_name}", found)
                    
        except Exception as e:
            self.log_test("Prometheus Rules API", False, f"(Error: {e})")
    
    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "="*80)
        print("📋 TEST SUMMARY")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']} {result['message']}")
        
        print("\n🎯 Recommendations:")
        if failed_tests == 0:
            print("   ✅ All tests passed! Your DevSecOps stack is ready for production.")
        else:
            print("   🔧 Review failed tests and check service configurations.")
            print("   📋 Run 'docker-compose logs [service]' for detailed error information.")
            print("   🔄 Restart services if needed: 'docker-compose restart [service]'")
        
        return failed_tests == 0
    
    def run_all_tests(self):
        """Run all tests"""
        print("🧪 DevSecOps Stack Test Suite")
        print("="*50)
        
        self.test_service_health()
        self.test_prometheus_targets()
        self.test_metrics_collection()
        self.test_grafana_datasources()
        self.test_security_simulation()
        self.test_container_monitoring()
        self.test_falco_integration()
        self.test_alerting_rules()
        
        return self.generate_summary()

if __name__ == "__main__":
    tester = StackTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
