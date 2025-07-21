#!/usr/bin/env python3
"""
Self-Improving Jarvis with MCP (Model Context Protocol)
A self-evolving digital assistant that can modify its own code
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

class MCPJarvis:
    """Self-improving Jarvis with computer control capabilities"""
    
    def __init__(self):
        self.performance_threshold = 8.0  # Target performance score (out of 10)
        self.current_performance = 5.0    # Starting performance
        self.project_path = Path(__file__).parent
        self.memory = {}  # Conversation and context memory
        self.performance_log = []
        
        # Computer control settings
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.5
        
    async def main_loop(self):
        """Main self-improvement loop"""
        logger.info("🤖 Jarvis Self-Improvement Loop Started")
        
        while self.current_performance < self.performance_threshold:
            try:
                # Execute business tasks and measure performance
                performance_score = await self.execute_and_evaluate()
                
                if performance_score < self.performance_threshold:
                    logger.info(f"📊 Performance: {performance_score:.1f}/{self.performance_threshold} - Improving...")
                    await self.self_improve()
                else:
                    logger.info(f"✅ Performance target reached: {performance_score:.1f}")
                    break
                    
                # Wait before next cycle
                await asyncio.sleep(300)  # 5 minutes between cycles
                
            except Exception as e:
                log_error("main_loop", e)
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    async def execute_and_evaluate(self) -> float:
        """Execute tasks and evaluate performance"""
        try:
            # Simulate task execution (replace with real business tasks)
            results = await self.execute_business_tasks()
            
            # Self-evaluate performance
            score = await self.evaluate_performance(results)
            
            # Log performance
            self.performance_log.append({
                'timestamp': datetime.now().isoformat(),
                'score': score,
                'results': results
            })
            
            self.current_performance = score
            return score
            
        except Exception as e:
            log_error("execute_and_evaluate", e)
            return 0.0
    
    async def execute_business_tasks(self) -> Dict[str, Any]:
        """Execute actual business tasks"""
        results = {
            'tasks_completed': 0,
            'errors': [],
            'success_rate': 0.0,
            'response_time': 0.0
        }
        
        try:
            start_time = time.time()
            
            # Task 1: Check for urgent items (existing functionality)
            urgent_analysis = analyze_with_ai("What's urgent today?", [], [])
            if urgent_analysis:
                results['tasks_completed'] += 1
            
            # Task 2: Test conversation memory
            memory_test = self.test_conversation_memory()
            if memory_test:
                results['tasks_completed'] += 1
            
            # Task 3: Test computer control
            computer_test = await self.test_computer_control()
            if computer_test:
                results['tasks_completed'] += 1
            
            results['response_time'] = time.time() - start_time
            results['success_rate'] = results['tasks_completed'] / 3
            
        except Exception as e:
            results['errors'].append(str(e))
            
        return results
    
    def test_conversation_memory(self) -> bool:
        """Test if conversation memory is working"""
        try:
            # Store test memory
            self.memory['test_urgent_items'] = [
                {'id': 1, 'type': 'github_security', 'status': 'pending'},
                {'id': 2, 'type': 'companies_house', 'status': 'pending'}
            ]
            
            # Retrieve and validate
            retrieved = self.memory.get('test_urgent_items', [])
            return len(retrieved) == 2
            
        except Exception as e:
            log_error("test_conversation_memory", e)
            return False
    
    async def test_computer_control(self) -> bool:
        """Test basic computer control capabilities"""
        try:
            # Test screenshot capability
            screenshot = pyautogui.screenshot()
            if screenshot:
                # Test mouse movement (safe movement)
                current_pos = pyautogui.position()
                pyautogui.moveTo(current_pos.x + 10, current_pos.y + 10)
                pyautogui.moveTo(current_pos.x, current_pos.y)  # Move back
                return True
            return False
            
        except Exception as e:
            log_error("test_computer_control", e)
            return False
    
    async def evaluate_performance(self, results: Dict[str, Any]) -> float:
        """Evaluate performance based on task results"""
        score = 0.0
        
        # Base score from success rate
        score += results.get('success_rate', 0) * 5  # Up to 5 points
        
        # Speed bonus (faster = better)
        response_time = results.get('response_time', 10)
        if response_time < 5:
            score += 2  # Fast execution bonus
        elif response_time < 10:
            score += 1  # Moderate speed bonus
        
        # Error penalty
        error_count = len(results.get('errors', []))
        score -= error_count * 0.5  # -0.5 per error
        
        # Memory persistence bonus
        if len(self.memory) > 0:
            score += 1  # Memory working bonus
        
        # Computer control bonus
        if results.get('tasks_completed', 0) >= 3:
            score += 2  # All systems working bonus
        
        return max(0.0, min(10.0, score))  # Clamp between 0-10
    
    async def self_improve(self):
        """Core self-improvement function"""
        logger.info("🔧 Starting self-improvement process...")
        
        try:
            # Analyze what needs improvement
            improvements = await self.analyze_improvement_opportunities()
            
            if improvements:
                # Implement the most critical improvement
                top_improvement = improvements[0]
                await self.implement_improvement(top_improvement)
                
                # Test the changes
                test_passed = await self.run_tests()
                
                if test_passed:
                    logger.info("✅ Self-improvement successful")
                    await self.commit_changes(top_improvement)
                else:
                    logger.warning("❌ Self-improvement failed tests, rolling back")
                    await self.rollback_changes()
            
        except Exception as e:
            log_error("self_improve", e)
    
    async def analyze_improvement_opportunities(self) -> List[Dict[str, Any]]:
        """Analyze what can be improved"""
        improvements = []
        
        # Check performance log for patterns
        if len(self.performance_log) >= 3:
            recent_scores = [entry['score'] for entry in self.performance_log[-3:]]
            avg_score = sum(recent_scores) / len(recent_scores)
            
            if avg_score < 6.0:
                improvements.append({
                    'type': 'performance_optimization',
                    'priority': 'high',
                    'description': 'Optimize core performance functions',
                    'target_file': 'mcp_jarvis.py',
                    'target_function': 'execute_business_tasks'
                })
        
        # Check for missing conversation memory
        if not self.memory:
            improvements.append({
                'type': 'memory_enhancement',
                'priority': 'medium',
                'description': 'Enhance conversation memory capabilities',
                'target_file': 'mcp_jarvis.py',
                'target_function': 'test_conversation_memory'
            })
        
        # Check computer control reliability
        if self.current_performance < 7.0:
            improvements.append({
                'type': 'computer_control_enhancement',
                'priority': 'medium',
                'description': 'Improve computer control reliability',
                'target_file': 'mcp_jarvis.py',
                'target_function': 'test_computer_control'
            })
        
        return sorted(improvements, key=lambda x: {'high': 3, 'medium': 2, 'low': 1}[x['priority']], reverse=True)
    
    async def implement_improvement(self, improvement: Dict[str, Any]):
        """Implement a specific improvement using computer control"""
        logger.info(f"🔨 Implementing: {improvement['description']}")
        
        try:
            if improvement['type'] == 'performance_optimization':
                await self.optimize_performance_code()
            elif improvement['type'] == 'memory_enhancement':
                await self.enhance_memory_system()
            elif improvement['type'] == 'computer_control_enhancement':
                await self.enhance_computer_control()
                
        except Exception as e:
            log_error("implement_improvement", e)
    
    async def optimize_performance_code(self):
        """Optimize performance-related code"""
        # Simulate code optimization
        # In real implementation, this would use computer control to:
        # 1. Open Cursor
        # 2. Navigate to the target function
        # 3. Apply optimizations
        # 4. Save changes
        
        logger.info("📈 Optimizing performance code...")
        
        # For now, we'll just update our internal performance tracking
        if hasattr(self, 'performance_optimizations'):
            self.performance_optimizations += 1
        else:
            self.performance_optimizations = 1
        
        # Simulate a small performance boost
        self.current_performance += 0.5
    
    async def enhance_memory_system(self):
        """Enhance the conversation memory system"""
        logger.info("🧠 Enhancing memory system...")
        
        # Add persistent memory storage
        self.memory['persistent_context'] = {
            'improvement_history': [],
            'performance_targets': {'current': self.performance_threshold},
            'successful_patterns': []
        }
        
        # Simulate improvement
        self.current_performance += 0.3
    
    async def enhance_computer_control(self):
        """Enhance computer control capabilities"""
        logger.info("🖱️ Enhancing computer control...")
        
        # Add error handling and retry logic
        self.memory['computer_control_config'] = {
            'retry_attempts': 3,
            'safety_checks': True,
            'screenshot_validation': True
        }
        
        # Simulate improvement
        self.current_performance += 0.4
    
    async def run_tests(self) -> bool:
        """Run test suite to validate improvements"""
        logger.info("🧪 Running test suite...")
        
        try:
            # Test core functionality
            test_results = await self.execute_business_tasks()
            
            # Validate performance didn't degrade
            if test_results.get('success_rate', 0) >= 0.6:  # At least 60% success
                return True
            else:
                return False
                
        except Exception as e:
            log_error("run_tests", e)
            return False
    
    async def commit_changes(self, improvement: Dict[str, Any]):
        """Commit successful improvements"""
        logger.info("💾 Committing improvements...")
        
        # Log the successful improvement
        if 'improvement_history' not in self.memory:
            self.memory['improvement_history'] = []
        
        self.memory['improvement_history'].append({
            'timestamp': datetime.now().isoformat(),
            'improvement': improvement,
            'performance_before': self.current_performance - 0.5,  # Estimate
            'performance_after': self.current_performance
        })
    
    async def rollback_changes(self):
        """Rollback failed improvements"""
        logger.info("↩️ Rolling back changes...")
        
        # Reset performance to previous level
        if len(self.performance_log) > 0:
            self.current_performance = self.performance_log[-1]['score']
    
    def get_memory_context(self, key: str) -> Any:
        """Retrieve context from memory"""
        return self.memory.get(key)
    
    def store_memory_context(self, key: str, value: Any):
        """Store context in memory"""
        self.memory[key] = value
    
    async def open_cursor_and_navigate(self, file_path: str, function_name: str = None):
        """Open Cursor IDE and navigate to specific file/function"""
        try:
            # This would use computer control to:
            # 1. Open Cursor application
            # 2. Open the specified file
            # 3. Navigate to the function if specified
            
            logger.info(f"🎯 Opening Cursor for: {file_path}")
            
            # Simulate opening Cursor (in real implementation, use pyautogui)
            # pyautogui.hotkey('cmd', 'space')  # Open Spotlight
            # pyautogui.write('Cursor')
            # pyautogui.press('enter')
            
            # For now, just log the action
            logger.info(f"📝 Would open {file_path}" + (f" at function {function_name}" if function_name else ""))
            
        except Exception as e:
            log_error("open_cursor_and_navigate", e)

# CLI interface for running Jarvis
async def main():
    """Main entry point"""
    print("🤖 Starting Self-Improving Jarvis...")
    print("=" * 50)
    
    jarvis = MCPJarvis()
    
    try:
        await jarvis.main_loop()
    except KeyboardInterrupt:
        print("\n👋 Jarvis shutting down...")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 