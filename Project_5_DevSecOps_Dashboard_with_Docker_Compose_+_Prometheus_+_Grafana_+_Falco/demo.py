#!/usr/bin/env python3
"""
DevSecOps Dashboard Demo Script
Demonstrates the complete monitoring and security stack
"""

import requests
import time
import json
import subprocess
import sys
from datetime import datetime
import threading
import random

class DevSecOpsDemo:
    def __init__(self):
        self.base_url = "http://localhost:3000"
        self.grafana_url = "http://localhost:3001"
        self.prometheus_url = "http://localhost:9090"
        
    def print_banner(self):
        """Print demo banner"""
        print("=" * 80)
        print("🛡️  DevSecOps Dashboard Demo")
        print("   Security-Monitored Microservice Stack")
        print("   Prometheus + Grafana + Falco + FastAPI")
        print("=" * 80)
        print()
        
    def check_services(self):
        """Check if all services are running"""
        print("🔍 Checking service health...")
        
        services = {
            "Demo App": f"{self.base_url}/health",
            "Grafana": f"{self.grafana_url}/api/health",
            "Prometheus": f"{self.prometheus_url}/-/healthy"
        }
        
        all_healthy = True
        for service, url in services.items():
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"✅ {service}: Healthy")
                else:
                    print(f"❌ {service}: Unhealthy (Status: {response.status_code})")
                    all_healthy = False
            except Exception as e:
                print(f"❌ {service}: Unreachable ({e})")
                all_healthy = False
        
        if not all_healthy:
            print("\n⚠️  Some services are not healthy. Please check docker-compose logs.")
            return False
        
        print("✅ All services are healthy!")
        return True
    
    def generate_normal_traffic(self, duration=60):
        """Generate normal application traffic"""
        print(f"\n📊 Generating normal traffic for {duration} seconds...")
        
        endpoints = [
            "/",
            "/health",
            "/api/data",
            "/api/container-info",
            "/api/security-status"
        ]
        
        start_time = time.time()
        request_count = 0
        
        while time.time() - start_time < duration:
            endpoint = random.choice(endpoints)
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                request_count += 1
                if request_count % 10 == 0:
                    print(f"   Sent {request_count} requests...")
            except Exception as e:
                print(f"   Request failed: {e}")
            
            time.sleep(random.uniform(0.5, 2.0))
        
        print(f"✅ Generated {request_count} normal requests")
    
    def simulate_security_attacks(self):
        """Simulate various security attacks"""
        print("\n🚨 Simulating security attacks...")
        
        attacks = [
            {"type": "sql_injection", "description": "SQL Injection Attack"},
            {"type": "privilege_escalation", "description": "Privilege Escalation"},
            {"type": "file_access", "description": "Unauthorized File Access"},
            {"type": "network_scan", "description": "Network Scanning"}
        ]
        
        for attack in attacks:
            print(f"   🔴 Triggering: {attack['description']}")
            try:
                response = requests.post(
                    f"{self.base_url}/simulate/attack",
                    json={"type": attack["type"]},
                    timeout=5
                )
                if response.status_code == 200:
                    print(f"   ✅ Attack simulated successfully")
                else:
                    print(f"   ❌ Attack simulation failed: {response.status_code}")
            except Exception as e:
                print(f"   ❌ Attack simulation error: {e}")
            
            time.sleep(2)
    
    def create_user_activity(self):
        """Simulate user registration and login activity"""
        print("\n👥 Simulating user activity...")
        
        # Create users
        users = [
            {"username": "alice", "email": "alice@example.com", "password": "password123"},
            {"username": "bob", "email": "bob@example.com", "password": "secret456"},
            {"username": "charlie", "email": "charlie@example.com", "password": "pass789"}
        ]
        
        for user in users:
            # Create user
            try:
                response = requests.post(
                    f"{self.base_url}/api/users",
                    json={"username": user["username"], "email": user["email"]},
                    timeout=5
                )
                if response.status_code == 200:
                    print(f"   ✅ Created user: {user['username']}")
                
                # Login user
                response = requests.post(
                    f"{self.base_url}/api/login",
                    json={"username": user["username"], "password": user["password"]},
                    timeout=5
                )
                if response.status_code == 200:
                    print(f"   ✅ User logged in: {user['username']}")
                
            except Exception as e:
                print(f"   ❌ User activity error: {e}")
            
            time.sleep(1)
        
        # Simulate failed login attempts
        print("   🔴 Simulating failed login attempts...")
        for _ in range(3):
            try:
                requests.post(
                    f"{self.base_url}/api/login",
                    json={"username": "hacker", "password": "wrongpassword"},
                    timeout=5
                )
            except:
                pass
            time.sleep(0.5)
    
    def generate_load_test(self):
        """Generate high load to trigger alerts"""
        print("\n⚡ Generating high load to trigger alerts...")
        
        def make_requests():
            for _ in range(20):
                try:
                    requests.get(f"{self.base_url}/api/stress", timeout=10)
                except:
                    pass
        
        # Start multiple threads to generate load
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_requests)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        print("✅ Load test completed")
    
    def show_access_urls(self):
        """Show URLs for accessing the dashboard"""
        print("\n🌐 Access URLs:")
        print(f"   📱 Demo Application: {self.base_url}")
        print(f"   📊 Grafana Dashboard: {self.grafana_url} (admin/admin123)")
        print(f"   📈 Prometheus: {self.prometheus_url}")
        print(f"   🐳 cAdvisor: http://localhost:8080")
        print(f"   📊 Node Exporter: http://localhost:9100")
        print()
    
    def run_demo(self):
        """Run the complete demo"""
        self.print_banner()
        
        # Check services
        if not self.check_services():
            print("\n❌ Demo cannot proceed. Please start the services first:")
            print("   docker-compose up -d")
            return
        
        self.show_access_urls()
        
        print("🚀 Starting comprehensive demo...")
        print("   This demo will:")
        print("   1. Generate normal application traffic")
        print("   2. Simulate user registration and login")
        print("   3. Trigger security attacks")
        print("   4. Generate high load")
        print("   5. Show monitoring results")
        print()
        
        input("Press Enter to continue...")
        
        # Run demo scenarios
        self.create_user_activity()
        
        # Generate normal traffic in background
        traffic_thread = threading.Thread(
            target=self.generate_normal_traffic, 
            args=(120,)
        )
        traffic_thread.start()
        
        time.sleep(10)
        self.simulate_security_attacks()
        
        time.sleep(10)
        self.generate_load_test()
        
        # Wait for traffic generation to complete
        traffic_thread.join()
        
        print("\n🎉 Demo completed!")
        print("\n📊 Check the following for results:")
        print(f"   • Grafana Dashboard: {self.grafana_url}")
        print("   • Look for security alerts and metrics")
        print("   • Check Falco logs: docker-compose logs falco")
        print("   • View Prometheus alerts: {}/alerts".format(self.prometheus_url))
        print()
        print("🔍 To see Falco alerts in real-time:")
        print("   docker-compose logs -f falco")

if __name__ == "__main__":
    demo = DevSecOpsDemo()
    demo.run_demo()
