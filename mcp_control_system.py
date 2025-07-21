#!/usr/bin/env python3
"""
MCP Control System with User Override
Allows user to take control with ESC key and provides safety mechanisms
"""

import pyautogui
import keyboard
import threading
import time
import signal
import sys
from datetime import datetime

class MCPControlSystem:
    """Control system for MCP with user override capabilities"""
    
    def __init__(self):
        self.user_control_active = False
        self.emergency_stop_triggered = False
        self.last_user_activity = datetime.now()
        self.control_thread = None
        self.safety_timeout = 30  # seconds - auto-disable if no activity
        
        # Safety settings
        pyautogui.FAILSAFE = True  # Move mouse to corner to stop
        pyautogui.PAUSE = 0.5  # Slower, safer operations
        
        print("🎮 MCP CONTROL SYSTEM INITIALIZED")
        print("=" * 50)
        print("🔧 SAFETY CONTROLS:")
        print("   • Press ESC to take control")
        print("   • Press Ctrl+C to emergency stop")
        print("   • Move mouse to corner to stop pyautogui")
        print("   • 30-second timeout if no activity")
        print("=" * 50)
    
    def start_control_monitoring(self):
        """Start monitoring for user control signals"""
        print("🎮 Starting control monitoring...")
        
        # Set up keyboard listeners
        keyboard.on_press_key('esc', self._take_user_control)
        keyboard.add_hotkey('ctrl+c', self._emergency_stop)
        
        # Start monitoring thread
        self.control_thread = threading.Thread(target=self._monitor_user_activity, daemon=True)
        self.control_thread.start()
        
        print("✅ Control monitoring active")
        print("   Press ESC to take control")
        print("   Press Ctrl+C for emergency stop")
    
    def _take_user_control(self, e):
        """User pressed ESC - take control"""
        self.user_control_active = True
        self.last_user_activity = datetime.now()
        
        print("\n🚨 USER CONTROL ACTIVATED!")
        print("   MCP computer control DISABLED")
        print("   You now have full control")
        print("   Press ESC again to release control")
        
        # Disable pyautogui temporarily
        pyautogui.FAILSAFE = True
    
    def _emergency_stop(self, e):
        """Emergency stop - completely disable MCP control"""
        self.emergency_stop_triggered = True
        self.user_control_active = True
        
        print("\n🚨 EMERGENCY STOP TRIGGERED!")
        print("   All MCP computer control DISABLED")
        print("   System requires manual restart")
        
        # Completely disable pyautogui
        pyautogui.FAILSAFE = True
        sys.exit(0)
    
    def _monitor_user_activity(self):
        """Monitor for user activity and auto-disable if needed"""
        while not self.emergency_stop_triggered:
            time.sleep(1)
            
            if self.user_control_active:
                # Check if user has been inactive
                time_since_activity = (datetime.now() - self.last_user_activity).total_seconds()
                
                if time_since_activity > self.safety_timeout:
                    print(f"\n⏰ {self.safety_timeout}s timeout reached - releasing user control")
                    self.user_control_active = False
                    print("   MCP control re-enabled")
    
    def is_user_control_active(self):
        """Check if user has taken control"""
        return self.user_control_active or self.emergency_stop_triggered
    
    def safe_computer_action(self, action_name: str, action_func, *args, **kwargs):
        """Safely execute computer action with user override protection"""
        
        if self.is_user_control_active():
            print(f"🚫 BLOCKED: {action_name} - User control active")
            return False
        
        print(f"🤖 EXECUTING: {action_name}")
        
        try:
            # Check for user control before each action
            if self.is_user_control_active():
                print(f"🚫 ABORTED: {action_name} - User took control")
                return False
            
            result = action_func(*args, **kwargs)
            
            # Update activity timestamp
            self.last_user_activity = datetime.now()
            
            print(f"✅ COMPLETED: {action_name}")
            return result
            
        except Exception as e:
            print(f"❌ FAILED: {action_name} - {str(e)}")
            return False
    
    def safe_cursor_operation(self, operation_name: str, target_file: str = None):
        """Safely execute Cursor IDE operations with user override"""
        
        if self.is_user_control_active():
            print(f"🚫 BLOCKED: Cursor {operation_name} - User control active")
            return False
        
        print(f"📝 CURSOR: {operation_name}")
        if target_file:
            print(f"   Target: {target_file}")
        
        try:
            # Check for user control
            if self.is_user_control_active():
                print(f"🚫 ABORTED: Cursor {operation_name} - User took control")
                return False
            
            # Execute the operation
            if operation_name == "open_cursor":
                return self._safe_open_cursor()
            elif operation_name == "open_file":
                return self._safe_open_file(target_file)
            elif operation_name == "find_function":
                return self._safe_find_function(target_file)
            elif operation_name == "add_code":
                return self._safe_add_code(target_file)
            elif operation_name == "save_file":
                return self._safe_save_file()
            else:
                print(f"❌ UNKNOWN OPERATION: {operation_name}")
                return False
                
        except Exception as e:
            print(f"❌ CURSOR FAILED: {operation_name} - {str(e)}")
            return False
    
    def _safe_open_cursor(self):
        """Safely open Cursor IDE"""
        if self.is_user_control_active():
            return False
        
        print("   🖱️ Opening Cursor IDE...")
        pyautogui.hotkey('cmd', 'space')
        time.sleep(1)
        pyautogui.write('Cursor')
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(3)
        
        self.last_user_activity = datetime.now()
        return True
    
    def _safe_open_file(self, filename: str):
        """Safely open file in Cursor"""
        if self.is_user_control_active():
            return False
        
        print(f"   📁 Opening {filename}...")
        pyautogui.hotkey('cmd', 'o')
        time.sleep(1)
        pyautogui.write(filename)
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(2)
        
        self.last_user_activity = datetime.now()
        return True
    
    def _safe_find_function(self, function_name: str):
        """Safely find function in Cursor"""
        if self.is_user_control_active():
            return False
        
        print(f"   🔍 Finding function {function_name}...")
        pyautogui.hotkey('cmd', 'f')
        time.sleep(0.5)
        pyautogui.write(f"def {function_name}")
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(1)
        pyautogui.press('escape')
        
        self.last_user_activity = datetime.now()
        return True
    
    def _safe_add_code(self, code: str):
        """Safely add code to current position"""
        if self.is_user_control_active():
            return False
        
        print("   ✍️ Adding code...")
        pyautogui.press('end')
        pyautogui.press('enter', presses=2)
        pyautogui.write(code)
        time.sleep(1)
        
        self.last_user_activity = datetime.now()
        return True
    
    def _safe_save_file(self):
        """Safely save current file"""
        if self.is_user_control_active():
            return False
        
        print("   💾 Saving file...")
        pyautogui.hotkey('cmd', 's')
        time.sleep(2)
        
        self.last_user_activity = datetime.now()
        return True
    
    def get_control_status(self):
        """Get current control status"""
        return {
            "user_control_active": self.user_control_active,
            "emergency_stop_triggered": self.emergency_stop_triggered,
            "time_since_activity": (datetime.now() - self.last_user_activity).total_seconds(),
            "safety_timeout": self.safety_timeout
        }
    
    def print_status(self):
        """Print current control status"""
        status = self.get_control_status()
        
        print("\n🎮 MCP CONTROL STATUS:")
        print("=" * 30)
        print(f"User Control: {'🔴 ACTIVE' if status['user_control_active'] else '🟢 INACTIVE'}")
        print(f"Emergency Stop: {'🔴 TRIGGERED' if status['emergency_stop_triggered'] else '🟢 CLEAR'}")
        print(f"Time Since Activity: {status['time_since_activity']:.1f}s")
        print(f"Safety Timeout: {status['safety_timeout']}s")
        
        if status['user_control_active']:
            print("\n🚨 USER HAS CONTROL - MCP operations blocked")
        else:
            print("\n🤖 MCP has control - Press ESC to take control")

def main():
    """Test the control system"""
    
    print("🎮 MCP CONTROL SYSTEM TEST")
    print("=" * 40)
    
    control = MCPControlSystem()
    control.start_control_monitoring()
    
    print("\n🧪 Testing control system...")
    print("Press ESC to take control, Ctrl+C to emergency stop")
    
    try:
        while True:
            time.sleep(2)
            control.print_status()
            
            # Simulate some MCP operations
            if not control.is_user_control_active():
                print("🤖 MCP would execute operations here...")
            else:
                print("🚫 MCP operations blocked by user control")
                
    except KeyboardInterrupt:
        print("\n👋 Control system test ended")

if __name__ == "__main__":
    main() 