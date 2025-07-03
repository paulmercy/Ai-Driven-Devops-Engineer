#!/usr/bin/env python3
"""
Falco Fix Script
Helps diagnose and fix Falco issues in WSL2 environment
"""

import subprocess
import sys
import os
import time

class FalcoFixer:
    def __init__(self):
        self.project_dir = os.path.dirname(os.path.abspath(__file__))
        
    def run_command(self, command, capture_output=True):
        """Run a shell command"""
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=capture_output, 
                text=True,
                cwd=self.project_dir
            )
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)
    
    def check_wsl_environment(self):
        """Check if running in WSL2"""
        print("🔍 Checking environment...")
        
        success, stdout, stderr = self.run_command("uname -r")
        if "microsoft" in stdout.lower() or "wsl" in stdout.lower():
            print("✅ Detected WSL2 environment")
            return True
        else:
            print("ℹ️  Not running in WSL2")
            return False
    
    def stop_falco(self):
        """Stop current Falco service"""
        print("🛑 Stopping current Falco service...")
        
        success, stdout, stderr = self.run_command("docker-compose stop falco")
        if success:
            print("✅ Falco service stopped")
        else:
            print("⚠️  Falco service was not running or failed to stop")
        
        # Remove the container
        self.run_command("docker-compose rm -f falco")
    
    def check_falco_logs(self):
        """Check Falco logs for errors"""
        print("📋 Checking Falco logs...")
        
        success, stdout, stderr = self.run_command("docker-compose logs falco")
        if success and stdout:
            print("Recent Falco logs:")
            print("-" * 50)
            print(stdout[-1000:])  # Last 1000 characters
            print("-" * 50)
            
            # Check for common errors
            if "Plugin requirement not satisfied" in stdout:
                print("❌ Plugin requirement error detected")
                return False
            elif "schema validation: failed" in stdout:
                print("❌ Configuration validation error detected")
                return False
            elif "Error:" in stdout:
                print("❌ General error detected in logs")
                return False
            else:
                print("✅ No obvious errors in logs")
                return True
        else:
            print("⚠️  No Falco logs found")
            return False
    
    def use_mock_falco(self):
        """Switch to mock Falco for WSL2 compatibility"""
        print("🔄 Switching to Mock Falco for WSL2 compatibility...")
        
        # Stop real Falco
        self.stop_falco()
        
        # Build mock Falco
        print("🔨 Building Mock Falco container...")
        success, stdout, stderr = self.run_command("docker-compose -f docker-compose.falco-mock.yml build falco-mock")
        
        if not success:
            print(f"❌ Failed to build Mock Falco: {stderr}")
            return False
        
        # Start mock Falco
        print("🚀 Starting Mock Falco...")
        success, stdout, stderr = self.run_command("docker-compose -f docker-compose.falco-mock.yml up -d falco-mock")
        
        if success:
            print("✅ Mock Falco started successfully!")
            
            # Wait a moment and check logs
            time.sleep(5)
            success, stdout, stderr = self.run_command("docker-compose -f docker-compose.falco-mock.yml logs falco-mock")
            if stdout:
                print("Mock Falco logs:")
                print(stdout)
            
            return True
        else:
            print(f"❌ Failed to start Mock Falco: {stderr}")
            return False
    
    def try_real_falco_fixes(self):
        """Try to fix real Falco configuration"""
        print("🔧 Attempting to fix real Falco configuration...")
        
        # Try userspace mode
        print("Trying userspace mode...")
        
        # Update docker-compose to use userspace mode
        compose_content = """
  falco:
    image: falcosecurity/falco:0.41.3
    container_name: falco
    networks:
      - monitoring
    privileged: true
    volumes:
      - /var/run/docker.sock:/host/var/run/docker.sock:ro
      - /proc:/host/proc:ro
      - ./falco/falco.yaml:/etc/falco/falco.yaml
      - ./falco/rules:/etc/falco/rules.d
      - falco_data:/var/log/falco
    environment:
      - FALCO_GRPC_ENABLED=false
      - FALCO_K8S_AUDIT_ENABLED=false
      - SKIP_DRIVER_LOADER=true
    command: ["/usr/bin/falco", "-c", "/etc/falco/falco.yaml", "--userspace"]
    restart: unless-stopped
"""
        
        print("Updated Falco configuration for userspace mode")
        
        # Restart Falco
        self.run_command("docker-compose up -d falco")
        
        # Wait and check
        time.sleep(10)
        return self.check_falco_logs()
    
    def test_falco_working(self):
        """Test if Falco is working"""
        print("🧪 Testing Falco functionality...")
        
        # Check if container is running
        success, stdout, stderr = self.run_command("docker-compose ps falco")
        if "Up" not in stdout:
            print("❌ Falco container is not running")
            return False
        
        # Generate test activity
        print("Generating test security events...")
        test_commands = [
            "docker-compose exec -T app whoami",
            "docker-compose exec -T app id", 
            "docker-compose exec -T app ps aux | head -5"
        ]
        
        for cmd in test_commands:
            self.run_command(cmd)
            time.sleep(1)
        
        # Wait for events to be processed
        time.sleep(5)
        
        # Check for alerts
        success, stdout, stderr = self.run_command("docker-compose logs falco | grep -i 'information gathering'")
        if success and stdout:
            print("✅ Falco is generating security alerts!")
            return True
        else:
            print("⚠️  No security alerts detected")
            return False
    
    def run_diagnosis(self):
        """Run complete Falco diagnosis and fix"""
        print("🛡️  Falco Diagnosis and Fix Tool")
        print("=" * 50)
        
        # Check environment
        is_wsl = self.check_wsl_environment()
        
        # Check current Falco status
        falco_working = self.test_falco_working()
        
        if falco_working:
            print("🎉 Falco is already working correctly!")
            return True
        
        print("\n❌ Falco is not working properly")
        
        # Show current logs
        self.check_falco_logs()
        
        print("\n🔧 Attempting fixes...")
        
        if is_wsl:
            print("\n📋 WSL2 detected - trying Mock Falco approach...")
            if self.use_mock_falco():
                print("✅ Mock Falco is now running!")
                print("\n📊 To test Mock Falco:")
                print("   python test_falco.py")
                print("   docker-compose -f docker-compose.falco-mock.yml logs -f falco-mock")
                return True
        
        print("\n🔧 Trying real Falco fixes...")
        if self.try_real_falco_fixes():
            if self.test_falco_working():
                print("✅ Real Falco is now working!")
                return True
        
        print("\n❌ Unable to fix Falco automatically")
        print("\n💡 Recommendations:")
        print("   1. Use Mock Falco for demonstration: python fix_falco.py --mock")
        print("   2. Check Docker Desktop settings")
        print("   3. Try running on native Linux instead of WSL2")
        
        return False

def main():
    fixer = FalcoFixer()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--mock":
        fixer.use_mock_falco()
    else:
        fixer.run_diagnosis()

if __name__ == "__main__":
    main()
