#!/usr/bin/env python3
"""
Quick Cursor Test
Direct Cursor automation without server dependencies
"""

import pyautogui
import time

def quick_cursor_test():
    """Quick test of Cursor automation"""
    
    print("🎯 QUICK CURSOR TEST")
    print("=" * 40)
    print("Testing Cursor automation directly")
    print("=" * 40)
    
    # Safety settings
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.3
    
    try:
        print("\n1️⃣ Opening Cursor...")
        pyautogui.hotkey('cmd', 'space')
        time.sleep(1.5)
        pyautogui.write('Cursor')
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(3)
        
        print("2️⃣ Ensuring focus...")
        screen_width, screen_height = pyautogui.size()
        pyautogui.click(screen_width // 2, screen_height // 2)
        time.sleep(1)
        
        print("3️⃣ Testing text input...")
        pyautogui.write("// Quick Cursor test - this should appear")
        time.sleep(1)
        
        print("4️⃣ Testing file open...")
        pyautogui.hotkey('cmd', 'o')
        time.sleep(1)
        pyautogui.write('jarvis_business_focused.py')
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(2)
        
        print("5️⃣ Testing find...")
        pyautogui.hotkey('cmd', 'f')
        time.sleep(0.5)
        pyautogui.write('def')
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(1)
        pyautogui.press('escape')
        
        print("6️⃣ Adding test code...")
        pyautogui.press('end')
        pyautogui.press('enter', presses=2)
        pyautogui.write("# Quick test successful!")
        time.sleep(1)
        
        print("7️⃣ Saving...")
        pyautogui.hotkey('cmd', 's')
        time.sleep(2)
        
        print("\n✅ QUICK CURSOR TEST COMPLETE!")
        print("If you see the text in Cursor, automation is working!")
        
    except Exception as e:
        print(f"\n❌ QUICK CURSOR TEST FAILED: {str(e)}")

if __name__ == "__main__":
    quick_cursor_test() 