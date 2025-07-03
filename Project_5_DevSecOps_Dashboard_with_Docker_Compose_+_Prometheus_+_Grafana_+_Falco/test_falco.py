#!/usr/bin/env python3
"""
Falco Testing Script
Tests if Falco is properly detecting security events
"""

import subprocess
import time
import json
import sys
from datetime import datetime

class FalcoTester:
    def __init__(self):
        self.test_results = []
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def run_command_in_container(self, command, container="app"):
        """Run a command in the specified container"""
        try:
            cmd = ["docker-compose", "exec", "-T", container, "bash", "-c", command]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except Exception as e:
            self.log(f"Command failed: {e}", "ERROR")
            return False
    
    def check_falco_running(self):
        """Check if Falco container is running"""
        self.log("Checking if Falco is running...")
        try:
            result = subprocess.run(
                ["docker-compose", "ps", "-q", "falco"], 
                capture_output=True, text=True
            )
            if result.stdout.strip():
                self.log("✅ Falco container is running")
                return True
            else:
                self.log("❌ Falco container is not running", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Error checking Falco status: {e}", "ERROR")
            return False
    
    def get_falco_logs(self, lines=50):
        """Get recent Falco logs"""
        try:
            result = subprocess.run(
                ["docker-compose", "logs", "--tail", str(lines), "falco"],
                capture_output=True, text=True
            )
            return result.stdout
        except Exception as e:
            self.log(f"Error getting Falco logs: {e}", "ERROR")
            return ""
    
    def test_system_info_gathering(self):
        """Test System Information Gathering rule"""
        self.log("Testing System Information Gathering detection...")
        
        commands = ["whoami", "id", "uname -a", "ps aux | head -5"]
        
        for cmd in commands:
            self.log(f"Running: {cmd}")
            self.run_command_in_container(cmd)
            time.sleep(1)
        
        return True
    
    def test_sensitive_file_access(self):
        """Test Sensitive File Access rule"""
        self.log("Testing Sensitive File Access detection...")
        
        commands = [
            "cat /etc/passwd | head -3",
            "ls -la /etc/ssh/ || echo 'No SSH dir'",
            "cat /etc/hostname"
        ]
        
        for cmd in commands:
            self.log(f"Running: {cmd}")
            self.run_command_in_container(cmd)
            time.sleep(1)
        
        return True
    
    def test_network_activity(self):
        """Test Suspicious Network Activity rule"""
        self.log("Testing Suspicious Network Activity detection...")
        
        commands = [
            "curl -I --connect-timeout 5 google.com || echo 'Curl failed'",
            "wget --spider --timeout=5 https://example.com || echo 'Wget failed'",
            "nc -z google.com 80 || echo 'NC failed'"
        ]
        
        for cmd in commands:
            self.log(f"Running: {cmd}")
            self.run_command_in_container(cmd)
            time.sleep(1)
        
        return True
    
    def test_package_management(self):
        """Test Package Management rule"""
        self.log("Testing Package Management detection...")
        
        commands = [
            "apt list --installed | head -3 || echo 'APT not available'",
            "pip list || echo 'PIP not available'",
            "which npm && npm list -g --depth=0 || echo 'NPM not available'"
        ]
        
        for cmd in commands:
            self.log(f"Running: {cmd}")
            self.run_command_in_container(cmd)
            time.sleep(1)
        
        return True
    
    def test_container_escape_attempt(self):
        """Test Container Escape Attempt rule"""
        self.log("Testing Container Escape Attempt detection...")
        
        commands = [
            "ls -la /proc/1/root 2>/dev/null || echo 'Access denied'",
            "ls -la /host 2>/dev/null || echo 'Access denied'",
            "ls -la /var/run/docker.sock 2>/dev/null || echo 'Access denied'"
        ]
        
        for cmd in commands:
            self.log(f"Running: {cmd}")
            self.run_command_in_container(cmd)
            time.sleep(1)
        
        return True
    
    def analyze_falco_output(self):
        """Analyze Falco logs for alerts"""
        self.log("Analyzing Falco output for alerts...")
        
        logs = self.get_falco_logs(100)
        
        # Count different types of alerts
        alert_counts = {
            "System Information Gathering": logs.count("System information gathering detected"),
            "Sensitive File Access": logs.count("Sensitive file access detected"),
            "Suspicious Network Activity": logs.count("Suspicious network activity detected"),
            "Package Management": logs.count("Package management tool executed"),
            "Container Escape Attempt": logs.count("Container escape attempt detected")
        }
        
        total_alerts = sum(alert_counts.values())
        
        self.log(f"Found {total_alerts} total alerts:")
        for rule, count in alert_counts.items():
            if count > 0:
                self.log(f"  ✅ {rule}: {count} alerts")
            else:
                self.log(f"  ⚠️  {rule}: {count} alerts")
        
        return total_alerts > 0
    
    def run_all_tests(self):
        """Run all Falco tests"""
        self.log("🛡️  Starting Falco Security Detection Tests")
        self.log("=" * 50)
        
        # Check if Falco is running
        if not self.check_falco_running():
            self.log("❌ Cannot proceed - Falco is not running", "ERROR")
            return False
        
        # Get initial log count
        initial_logs = self.get_falco_logs(10)
        self.log(f"Initial Falco log lines: {len(initial_logs.splitlines())}")
        
        # Run tests
        tests = [
            ("System Information Gathering", self.test_system_info_gathering),
            ("Sensitive File Access", self.test_sensitive_file_access),
            ("Suspicious Network Activity", self.test_network_activity),
            ("Package Management", self.test_package_management),
            ("Container Escape Attempt", self.test_container_escape_attempt)
        ]
        
        self.log("Running security tests...")
        for test_name, test_func in tests:
            try:
                test_func()
                self.test_results.append((test_name, True))
            except Exception as e:
                self.log(f"❌ Test failed: {test_name} - {e}", "ERROR")
                self.test_results.append((test_name, False))
        
        # Wait for Falco to process events
        self.log("Waiting for Falco to process events...")
        time.sleep(10)
        
        # Analyze results
        alerts_detected = self.analyze_falco_output()
        
        # Print summary
        self.log("=" * 50)
        self.log("🔍 Test Summary:")
        
        passed_tests = sum(1 for _, passed in self.test_results if passed)
        total_tests = len(self.test_results)
        
        self.log(f"Tests executed: {passed_tests}/{total_tests}")
        
        if alerts_detected:
            self.log("✅ Falco is working - Security alerts detected!")
        else:
            self.log("⚠️  No alerts detected - Check Falco configuration")
        
        self.log("\n🔧 To see detailed Falco logs:")
        self.log("   docker-compose logs falco | tail -20")
        
        self.log("\n📊 To monitor real-time alerts:")
        self.log("   docker-compose logs -f falco")
        
        return alerts_detected

if __name__ == "__main__":
    tester = FalcoTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
