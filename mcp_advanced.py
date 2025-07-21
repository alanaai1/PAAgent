#!/usr/bin/env python3
"""
Advanced Self-Improving Jarvis with Real Computer Control
Demonstrates the self-improvement loop with actual Cursor IDE integration
"""

import asyncio
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path
import logging
import pyautogui
import psutil
import os
from typing import Dict, List, Any

# Import our existing Jarvis functionality
from api_server import analyze_with_ai, generate_response, log_error

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AdvancedMCPJarvis:
    """Advanced self-improving Jarvis with real computer control"""
    
    def __init__(self):
        self.performance_threshold = 8.0
        self.current_performance = 5.0
        self.project_path = Path(__file__).parent
        self.memory = {}
        self.performance_log = []
        self.improvement_count = 0
        
        # Computer control settings
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 1.0  # Slower for safety
        
        # Define improvement patterns
        self.improvement_patterns = {
            'performance_optimization': {
                'code_snippets': [
                    'async def optimized_function():',
                    '    # Add caching for better performance',
                    '    if not hasattr(self, "_cache"):',
                    '        self._cache = {}',
                    '    return self._cache.get("result", "optimized")',
                ],
                'target_score_boost': 1.0
            },
            'memory_enhancement': {
                'code_snippets': [
                    'def enhanced_memory_store(self, key, value):',
                    '    # Enhanced memory with validation',
                    '    if key and value:',
                    '        self.memory[key] = {',
                    '            "value": value,',
                    '            "timestamp": datetime.now().isoformat(),',
                    '            "access_count": 0',
                    '        }',
                ],
                'target_score_boost': 0.8
            },
            'error_handling': {
                'code_snippets': [
                    'try:',
                    '    result = await self.execute_task()',
                    '    return result',
                    'except Exception as e:',
                    '    logger.error(f"Task failed: {e}")',
                    '    return self.fallback_response()',
                ],
                'target_score_boost': 0.6
            }
        }
    
    async def demonstrate_self_improvement(self):
        """Demonstrate the self-improvement process"""
        logger.info("🚀 Starting Self-Improvement Demonstration")
        
        # Show current state
        await self.show_current_state()
        
        # Perform improvement cycle
        for cycle in range(3):  # 3 improvement cycles
            logger.info(f"\n🔄 Improvement Cycle {cycle + 1}/3")
            
            # Analyze what needs improvement
            improvement = await self.analyze_next_improvement()
            
            if improvement:
                # Demonstrate the improvement process
                await self.demonstrate_code_improvement(improvement)
                
                # Update performance
                self.current_performance += improvement['target_score_boost']
                self.improvement_count += 1
                
                logger.info(f"📈 Performance improved to: {self.current_performance:.1f}")
                
                if self.current_performance >= self.performance_threshold:
                    logger.info("🎯 Performance target reached!")
                    break
            
            await asyncio.sleep(2)  # Pause between cycles
        
        # Show final state
        await self.show_final_state()
    
    async def show_current_state(self):
        """Show current system state"""
        logger.info("📊 Current System State:")
        logger.info(f"   Performance: {self.current_performance:.1f}/{self.performance_threshold}")
        logger.info(f"   Memory items: {len(self.memory)}")
        logger.info(f"   Improvements made: {self.improvement_count}")
    
    async def analyze_next_improvement(self) -> Dict[str, Any]:
        """Analyze what improvement to make next"""
        if self.current_performance < 6.0:
            return {
                'type': 'performance_optimization',
                'priority': 'high',
                'description': 'Add performance caching',
                **self.improvement_patterns['performance_optimization']
            }
        elif len(self.memory) < 3:
            return {
                'type': 'memory_enhancement',
                'priority': 'medium', 
                'description': 'Enhance memory system',
                **self.improvement_patterns['memory_enhancement']
            }
        else:
            return {
                'type': 'error_handling',
                'priority': 'medium',
                'description': 'Improve error handling',
                **self.improvement_patterns['error_handling']
            }
    
    async def demonstrate_code_improvement(self, improvement: Dict[str, Any]):
        """Demonstrate how Jarvis would improve its own code"""
        logger.info(f"🔧 Implementing: {improvement['description']}")
        
        # Step 1: Identify target file
        target_file = f"improvement_{improvement['type']}.py"
        logger.info(f"📁 Target file: {target_file}")
        
        # Step 2: Show what code would be added
        logger.info("📝 Code changes to implement:")
        for line in improvement['code_snippets']:
            logger.info(f"   + {line}")
        
        # Step 3: Simulate computer control actions
        await self.simulate_cursor_automation(target_file, improvement)
        
        # Step 4: Update memory with the improvement
        self.memory[f'improvement_{self.improvement_count}'] = {
            'type': improvement['type'],
            'description': improvement['description'],
            'timestamp': datetime.now().isoformat(),
            'performance_boost': improvement['target_score_boost']
        }
    
    async def simulate_cursor_automation(self, target_file: str, improvement: Dict[str, Any]):
        """Simulate what real Cursor automation would look like"""
        logger.info("🖱️ Computer Control Actions (Simulated):")
        
        # Action 1: Open Cursor
        logger.info("   1. Opening Cursor IDE...")
        # Real: pyautogui.hotkey('cmd', 'space'); pyautogui.write('Cursor'); pyautogui.press('enter')
        await asyncio.sleep(0.5)
        
        # Action 2: Create/Open file
        logger.info(f"   2. Opening file: {target_file}")
        # Real: pyautogui.hotkey('cmd', 'o'); pyautogui.write(target_file); pyautogui.press('enter')
        await asyncio.sleep(0.5)
        
        # Action 3: Add improvement code
        logger.info("   3. Adding improvement code...")
        # Real: pyautogui.write('\n'.join(improvement['code_snippets']))
        await asyncio.sleep(0.5)
        
        # Action 4: Save file
        logger.info("   4. Saving changes...")
        # Real: pyautogui.hotkey('cmd', 's')
        await asyncio.sleep(0.5)
        
        # Action 5: Run tests
        logger.info("   5. Running tests...")
        # Real: pyautogui.hotkey('cmd', '`'); pyautogui.write('python test.py'); pyautogui.press('enter')
        await asyncio.sleep(0.5)
        
        logger.info("   ✅ Code improvement implemented successfully")
    
    async def show_final_state(self):
        """Show final system state after improvements"""
        logger.info("\n🎉 Self-Improvement Complete!")
        logger.info("=" * 50)
        logger.info(f"📊 Final Performance: {self.current_performance:.1f}/{self.performance_threshold}")
        logger.info(f"🧠 Memory Items: {len(self.memory)}")
        logger.info(f"🔧 Improvements Made: {self.improvement_count}")
        
        logger.info("\n📝 Improvement History:")
        for key, improvement in self.memory.items():
            if key.startswith('improvement_'):
                logger.info(f"   • {improvement['description']} (+{improvement['performance_boost']})")
        
        if self.current_performance >= self.performance_threshold:
            logger.info("\n🚀 Jarvis has successfully self-improved and reached target performance!")
        else:
            logger.info(f"\n⏳ Still improving... Target: {self.performance_threshold}")

class RealComputerControl:
    """Real computer control implementation for production use"""
    
    @staticmethod
    async def open_cursor():
        """Actually open Cursor IDE"""
        try:
            # Method 1: Use Spotlight search
            pyautogui.hotkey('cmd', 'space')
            await asyncio.sleep(0.5)
            pyautogui.write('Cursor')
            await asyncio.sleep(0.5)
            pyautogui.press('enter')
            await asyncio.sleep(2)  # Wait for Cursor to open
            return True
        except Exception as e:
            log_error("open_cursor", e)
            return False
    
    @staticmethod
    async def open_file(file_path: str):
        """Open a specific file in Cursor"""
        try:
            pyautogui.hotkey('cmd', 'o')
            await asyncio.sleep(0.5)
            pyautogui.write(file_path)
            await asyncio.sleep(0.5)
            pyautogui.press('enter')
            await asyncio.sleep(1)
            return True
        except Exception as e:
            log_error("open_file", e)
            return False
    
    @staticmethod
    async def add_code(code_lines: List[str]):
        """Add code to the current file"""
        try:
            # Go to end of file
            pyautogui.hotkey('cmd', 'down')
            await asyncio.sleep(0.2)
            
            # Add new lines
            pyautogui.press('enter', presses=2)
            
            # Type each line
            for line in code_lines:
                pyautogui.write(line)
                pyautogui.press('enter')
                await asyncio.sleep(0.1)
            
            return True
        except Exception as e:
            log_error("add_code", e)
            return False
    
    @staticmethod
    async def save_file():
        """Save the current file"""
        try:
            pyautogui.hotkey('cmd', 's')
            await asyncio.sleep(0.5)
            return True
        except Exception as e:
            log_error("save_file", e)
            return False
    
    @staticmethod
    async def run_tests():
        """Open terminal and run tests"""
        try:
            # Open terminal
            pyautogui.hotkey('cmd', '`')
            await asyncio.sleep(1)
            
            # Run test command
            pyautogui.write('python3 -m pytest test_improvements.py -v')
            pyautogui.press('enter')
            await asyncio.sleep(2)
            
            return True
        except Exception as e:
            log_error("run_tests", e)
            return False

# Demo script
async def main():
    """Run the self-improvement demonstration"""
    print("🤖 Advanced Self-Improving Jarvis")
    print("=" * 50)
    print("This demonstration shows how Jarvis can:")
    print("• Analyze its own performance")
    print("• Identify improvement opportunities") 
    print("• Use computer control to modify its code")
    print("• Test and validate improvements")
    print("• Evolve continuously")
    print("=" * 50)
    
    jarvis = AdvancedMCPJarvis()
    
    try:
        await jarvis.demonstrate_self_improvement()
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"❌ Demo error: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 