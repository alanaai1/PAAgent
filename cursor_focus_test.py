#!/usr/bin/env python3
"""
Cursor Focus Test
Demonstrates proper Cursor IDE focus handling
"""

import pyautogui
import time

def test_cursor_focus():
    """Test proper Cursor focus handling"""
    
    print("🎯 CURSOR FOCUS TEST")
    print("=" * 40)
    print("This will open Cursor and ensure proper focus")
    print("=" * 40)
    
    # Safety settings
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.5
    
    try:
        print("\n1️⃣ Opening Cursor...")
        pyautogui.hotkey('cmd', 'space')
        time.sleep(2)  # Wait for Spotlight
        pyautogui.write('Cursor')
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(3)  # Wait for Cursor to load
        
        print("2️⃣ Ensuring Cursor focus...")
        # Get screen dimensions
        screen_width, screen_height = pyautogui.size()
        
        # Click in the middle of the screen to focus the editor
        print(f"   Clicking at ({screen_width//2}, {screen_height//2}) to focus editor")
        pyautogui.click(screen_width // 2, screen_height // 2)
        time.sleep(1)
        
        print("3️⃣ Testing text input...")
        # Try to type something
        pyautogui.write("// Cursor focus test - this should appear in the editor")
        time.sleep(1)
        
        print("4️⃣ Testing file operations...")
        # Try to open a file
        pyautogui.hotkey('cmd', 'o')
        time.sleep(1)
        pyautogui.write('jarvis_business_focused.py')
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(2)
        
        print("5️⃣ Testing find function...")
        pyautogui.hotkey('cmd', 'f')
        time.sleep(0.5)
        pyautogui.write('def generate_morning_briefing')
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(1)
        pyautogui.press('escape')
        
        print("6️⃣ Testing code addition...")
        # Add some test code
        pyautogui.press('end')
        pyautogui.press('enter', presses=2)
        pyautogui.write("# Focus test successful!")
        time.sleep(1)
        
        print("7️⃣ Saving file...")
        pyautogui.hotkey('cmd', 's')
        time.sleep(2)
        
        print("\n✅ CURSOR FOCUS TEST COMPLETE!")
        print("If you see the text in Cursor, focus is working properly")
        
    except Exception as e:
        print(f"\n❌ CURSOR FOCUS TEST FAILED: {str(e)}")
        print("Make sure Cursor is installed and accessible")

if __name__ == "__main__":
    test_cursor_focus() 