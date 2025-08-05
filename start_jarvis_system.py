#!/usr/bin/env python3
"""
Startup script for Jarvis AI System with Slack integration
"""
import os
import sys
import time
import subprocess
import signal
import threading
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class JarvisSystem:
    """Manages the Jarvis AI system components"""
    
    def __init__(self):
        self.processes = {}
        self.running = False
        
    def start_api_server(self):
        """Start the API server"""
        print("🚀 Starting API Server...")
        try:
            process = subprocess.Popen(
                [sys.executable, "api_server.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.processes['api_server'] = process
            print("✅ API Server started")
            return True
        except Exception as e:
            print(f"❌ Failed to start API Server: {e}")
            return False
    
    def start_slack_bot(self):
        """Start the Slack bot"""
        print("🤖 Starting Slack Bot...")
        try:
            process = subprocess.Popen(
                [sys.executable, "slack_bot.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.processes['slack_bot'] = process
            print("✅ Slack Bot started")
            return True
        except Exception as e:
            print(f"❌ Failed to start Slack Bot: {e}")
            return False
    
    def check_dependencies(self):
        """Check if required dependencies are installed"""
        print("🔍 Checking dependencies...")
        
        required_packages = [
            'slack_bolt',
            'requests',
            'flask',
            'google.auth',
            'anthropic'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
                print(f"✅ {package}")
            except ImportError:
                print(f"❌ {package}")
                missing_packages.append(package)
        
        if missing_packages:
            print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
            print("Install with: pip install -r requirements.txt")
            return False
        
        return True
    
    def check_environment(self):
        """Check environment variables"""
        print("\n🔍 Checking environment variables...")
        
        required_vars = [
            'GOOGLE_CLOUD_PROJECT_ID',
            'VERTEX_AI_REGION'
        ]
        
        optional_vars = [
            'SLACK_BOT_TOKEN',
            'SLACK_APP_TOKEN',
            'API_SERVER_URL'
        ]
        
        missing_required = []
        missing_optional = []
        
        for var in required_vars:
            if os.getenv(var):
                print(f"✅ {var}")
            else:
                print(f"❌ {var}")
                missing_required.append(var)
        
        for var in optional_vars:
            if os.getenv(var):
                print(f"✅ {var}")
            else:
                print(f"⚠️  {var} (optional)")
                missing_optional.append(var)
        
        if missing_required:
            print(f"\n❌ Missing required environment variables: {', '.join(missing_required)}")
            return False
        
        if not os.getenv('SLACK_BOT_TOKEN') or not os.getenv('SLACK_APP_TOKEN'):
            print(f"\n⚠️  Slack integration will be disabled (missing tokens)")
            print("   Set SLACK_BOT_TOKEN and SLACK_APP_TOKEN to enable Slack")
        
        return True
    
    def monitor_processes(self):
        """Monitor running processes"""
        while self.running:
            for name, process in self.processes.items():
                if process.poll() is not None:
                    print(f"⚠️  {name} process stopped unexpectedly")
                    # Restart the process
                    if name == 'api_server':
                        self.start_api_server()
                    elif name == 'slack_bot':
                        self.start_slack_bot()
            
            time.sleep(5)
    
    def start_system(self):
        """Start the complete Jarvis system"""
        print("=" * 60)
        print("JARVIS AI SYSTEM STARTUP")
        print("=" * 60)
        
        # Check dependencies
        if not self.check_dependencies():
            print("\n❌ Dependencies check failed")
            return False
        
        # Check environment
        if not self.check_environment():
            print("\n❌ Environment check failed")
            return False
        
        print("\n🚀 Starting Jarvis AI System...")
        
        # Start API server
        if not self.start_api_server():
            return False
        
        # Wait for API server to start
        time.sleep(3)
        
        # Start Slack bot (if tokens are available)
        if os.getenv('SLACK_BOT_TOKEN') and os.getenv('SLACK_APP_TOKEN'):
            if not self.start_slack_bot():
                print("⚠️  Slack bot failed to start, continuing without Slack")
        else:
            print("⚠️  Skipping Slack bot (missing tokens)")
        
        # Start monitoring
        self.running = True
        monitor_thread = threading.Thread(target=self.monitor_processes)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        print("\n✅ Jarvis AI System is running!")
        print("\n📋 System Status:")
        print(f"   API Server: {'✅ Running' if 'api_server' in self.processes else '❌ Stopped'}")
        print(f"   Slack Bot: {'✅ Running' if 'slack_bot' in self.processes else '❌ Stopped'}")
        
        print("\n🔗 Endpoints:")
        print(f"   API Server: http://localhost:5000")
        print(f"   Health Check: http://localhost:5000/")
        print(f"   Chat API: http://localhost:5000/api/jarvis/chat")
        
        print("\n📝 Usage:")
        print(f"   • Send POST requests to /api/jarvis/chat")
        print(f"   • Mention @Jarvis in Slack (if configured)")
        print(f"   • Use /jarvis command in Slack (if configured)")
        
        print("\n⏹️  Press Ctrl+C to stop the system")
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down Jarvis AI System...")
            self.stop_system()
    
    def stop_system(self):
        """Stop all processes"""
        self.running = False
        
        for name, process in self.processes.items():
            print(f"🛑 Stopping {name}...")
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"✅ {name} stopped")
            except subprocess.TimeoutExpired:
                print(f"⚠️  Force killing {name}")
                process.kill()
            except Exception as e:
                print(f"❌ Error stopping {name}: {e}")
        
        print("✅ Jarvis AI System stopped")

def main():
    """Main entry point"""
    system = JarvisSystem()
    system.start_system()

if __name__ == "__main__":
    main() 