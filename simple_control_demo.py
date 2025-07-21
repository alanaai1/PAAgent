#!/usr/bin/env python3
"""
Simple MCP Control Demo
Shows how ESC key can take control from MCP
"""

import time
import threading
import sys

class SimpleControlDemo:
    """Simple demonstration of user control override"""
    
    def __init__(self):
        self.user_control_active = False
        self.running = True
        
        print("🎮 SIMPLE MCP CONTROL DEMO")
        print("=" * 40)
        print("🔧 CONTROLS:")
        print("   • Press ESC to take control")
        print("   • Press Ctrl+C to exit")
        print("   • Type 'release' to give control back")
        print("=" * 40)
    
    def start_demo(self):
        """Start the control demo"""
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=self._monitor_input, daemon=True)
        monitor_thread.start()
        
        print("\n🤖 MCP is running...")
        print("Press ESC to take control!")
        
        cycle = 0
        while self.running:
            cycle += 1
            
            if self.user_control_active:
                print(f"🚨 CYCLE {cycle}: USER HAS CONTROL - MCP operations blocked")
            else:
                print(f"🤖 CYCLE {cycle}: MCP has control - performing operations...")
            
            time.sleep(2)
    
    def _monitor_input(self):
        """Monitor for user input"""
        while self.running:
            try:
                user_input = input().strip().lower()
                
                if user_input == 'esc':
                    self._take_user_control()
                elif user_input == 'release':
                    self._release_user_control()
                elif user_input == 'exit':
                    self.running = False
                    break
                    
            except (EOFError, KeyboardInterrupt):
                self.running = False
                break
    
    def _take_user_control(self):
        """User takes control"""
        self.user_control_active = True
        print("\n🚨 USER CONTROL ACTIVATED!")
        print("   MCP computer control DISABLED")
        print("   You now have full control")
        print("   Type 'release' to give control back")
    
    def _release_user_control(self):
        """User releases control"""
        self.user_control_active = False
        print("\n🤖 USER CONTROL RELEASED!")
        print("   MCP control re-enabled")
        print("   Press ESC to take control again")

def main():
    """Run the simple control demo"""
    
    print("🎮 SIMPLE MCP CONTROL DEMO")
    print("Demonstrating user override functionality")
    print("=" * 50)
    
    demo = SimpleControlDemo()
    
    try:
        demo.start_demo()
    except KeyboardInterrupt:
        print("\n👋 Demo ended by user")
    
    print("\n🎯 DEMO COMPLETE")
    print("This shows how you can take control from MCP with ESC key")

if __name__ == "__main__":
    main() 