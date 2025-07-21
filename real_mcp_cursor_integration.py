#!/usr/bin/env python3
"""
Real MCP Cursor Integration - The Missing Piece
Actually connects CEO feedback to Cursor's code modification capabilities
"""

import asyncio
import json
import subprocess
import time
import os
import re
from datetime import datetime
import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import pyautogui

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RealMCPCursorIntegration:
    """Real MCP integration that actually modifies code based on CEO feedback"""
    
    def __init__(self):
        self.jarvis_server_url = "http://localhost:5000"
        self.ceo_review_url = "http://localhost:5003"
        self.project_path = "/Users/alangurung/Documents/MVP builds/PAAgent"
        self.target_files = ["api_server.py", "jarvis_business_focused.py"]
        self.improvement_history = []
        
        # Cursor automation settings
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 1.0
        
    async def run_complete_mcp_cycle(self, test_message: str = "What's urgent today?"):
        """Complete MCP cycle: Jarvis → CEO Review → Cursor Implementation → Re-test"""
        logger.info("🔄 REAL MCP: Starting complete improvement cycle")
        
        try:
            # Step 1: Run Jarvis and get initial response
            initial_response = await self._run_jarvis(test_message)
            logger.info(f"📊 Initial Jarvis response: {initial_response.get('message', 'No response')[:100]}...")
            
            # Step 2: CEO Review
            ceo_review = await self._get_ceo_review(test_message)
            logger.info(f"💼 CEO Review score: {ceo_review.get('overall_score', 0):.2f}")
            
            # Step 3: Extract actionable improvements
            improvements = await self._extract_actionable_improvements(ceo_review)
            
            # Step 4: Implement improvements in Cursor
            implementation_result = await self._implement_in_cursor(improvements)
            
            # Step 5: Re-test Jarvis with improvements
            final_response = await self._run_jarvis(test_message)
            
            # Step 6: Compare before/after
            comparison = await self._compare_results(initial_response, final_response, ceo_review)
            
            return {
                "cycle_complete": True,
                "initial_response": initial_response,
                "ceo_review": ceo_review,
                "improvements_implemented": improvements,
                "implementation_result": implementation_result,
                "final_response": final_response,
                "improvement_comparison": comparison,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Real MCP cycle failed: {e}")
            return {"error": str(e)}
    
    async def _run_jarvis(self, message: str) -> dict:
        """Run Jarvis API"""
        try:
            response = requests.post(
                f"{self.jarvis_server_url}/api/jarvis/chat",
                json={"message": message, "personality": {"conscientiousness": 80}},
                timeout=30
            )
            return response.json() if response.status_code == 200 else {"error": f"Jarvis failed: {response.status_code}"}
        except Exception as e:
            return {"error": f"Jarvis error: {e}"}
    
    async def _get_ceo_review(self, message: str) -> dict:
        """Get CEO review of Jarvis response"""
        try:
            response = requests.post(
                f"{self.ceo_review_url}/api/mcp/run-review",
                json={"message": message},
                timeout=30
            )
            result = response.json() if response.status_code == 200 else {"error": f"CEO review failed: {response.status_code}"}
            return result.get("result", {}).get("cursor_feedback", {})
        except Exception as e:
            return {"error": f"CEO review error: {e}"}
    
    async def _extract_actionable_improvements(self, ceo_review: dict) -> list:
        """Extract specific code improvements from CEO feedback"""
        improvements = []
        
        if "improvement_areas" not in ceo_review:
            return improvements
        
        for area in ceo_review["improvement_areas"]:
            if area["priority"] == "HIGH":
                code_improvement = area.get("code_improvement", "")
                
                # Parse the code improvement
                parsed_improvement = self._parse_code_improvement(code_improvement, area["area"])
                if parsed_improvement:
                    improvements.append(parsed_improvement)
        
        return improvements
    
    def _parse_code_improvement(self, code_text: str, area: str) -> dict:
        """Parse code improvement into actionable format"""
        try:
            # Extract function definitions and code blocks
            lines = code_text.strip().split('\n')
            
            # Find the main function/class to modify
            target_function = None
            code_to_add = []
            
            for line in lines:
                if line.strip().startswith('def ') or line.strip().startswith('class '):
                    target_function = line.strip()
                elif line.strip() and not line.strip().startswith('#'):
                    code_to_add.append(line)
            
            return {
                "area": area,
                "target_function": target_function,
                "code_to_add": code_to_add,
                "insertion_point": "end_of_function" if target_function else "new_function"
            }
        except Exception as e:
            logger.error(f"Failed to parse code improvement: {e}")
            return None
    
    async def _implement_in_cursor(self, improvements: list) -> dict:
        """Actually implement improvements using Cursor automation"""
        if not improvements:
            return {"status": "no_improvements", "message": "No actionable improvements found"}
        
        try:
            # Open Cursor
            await self._open_cursor()
            
            results = []
            for improvement in improvements:
                result = await self._implement_single_improvement(improvement)
                results.append(result)
            
            # Save all changes
            await self._save_changes()
            
            return {
                "status": "implemented",
                "improvements_applied": len(results),
                "results": results
            }
            
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    async def _open_cursor(self):
        """Open Cursor IDE"""
        try:
            # Open Cursor via Spotlight
            pyautogui.hotkey('cmd', 'space')
            time.sleep(1)
            pyautogui.write('Cursor')
            time.sleep(1)
            pyautogui.press('enter')
            time.sleep(3)  # Wait for Cursor to open
            
            # Open the project
            pyautogui.hotkey('cmd', 'o')
            time.sleep(1)
            pyautogui.write(self.project_path)
            time.sleep(1)
            pyautogui.press('enter')
            time.sleep(2)
            
            logger.info("✅ Cursor opened and project loaded")
            
        except Exception as e:
            logger.error(f"Failed to open Cursor: {e}")
            raise
    
    async def _implement_single_improvement(self, improvement: dict) -> dict:
        """Implement a single improvement in the code"""
        try:
            area = improvement["area"]
            target_function = improvement["target_function"]
            code_to_add = improvement["code_to_add"]
            
            # Open the target file
            await self._open_file("api_server.py")
            
            if target_function:
                # Find and modify existing function
                await self._find_function(target_function)
                await self._add_code_to_function(code_to_add)
            else:
                # Add new function at end of file
                await self._add_new_function(code_to_add)
            
            return {
                "area": area,
                "status": "implemented",
                "code_added": len(code_to_add)
            }
            
        except Exception as e:
            return {
                "area": improvement.get("area", "unknown"),
                "status": "failed",
                "error": str(e)
            }
    
    async def _open_file(self, filename: str):
        """Open specific file in Cursor"""
        try:
            pyautogui.hotkey('cmd', 'p')
            time.sleep(0.5)
            pyautogui.write(filename)
            time.sleep(0.5)
            pyautogui.press('enter')
            time.sleep(1)
        except Exception as e:
            logger.error(f"Failed to open file {filename}: {e}")
            raise
    
    async def _find_function(self, function_signature: str):
        """Find specific function in file"""
        try:
            pyautogui.hotkey('cmd', 'f')
            time.sleep(0.5)
            pyautogui.write(function_signature.split('(')[0].replace('def ', ''))
            time.sleep(0.5)
            pyautogui.press('enter')
            time.sleep(1)
            pyautogui.press('escape')
        except Exception as e:
            logger.error(f"Failed to find function: {e}")
            raise
    
    async def _add_code_to_function(self, code_lines: list):
        """Add code to existing function"""
        try:
            # Go to end of function
            pyautogui.press('end')
            time.sleep(0.5)
            pyautogui.press('enter')
            time.sleep(0.5)
            
            # Add each line
            for line in code_lines:
                pyautogui.write(line)
                pyautogui.press('enter')
                time.sleep(0.2)
                
        except Exception as e:
            logger.error(f"Failed to add code to function: {e}")
            raise
    
    async def _add_new_function(self, code_lines: list):
        """Add new function at end of file"""
        try:
            # Go to end of file
            pyautogui.hotkey('cmd', 'end')
            time.sleep(0.5)
            pyautogui.press('enter', presses=2)
            time.sleep(0.5)
            
            # Add each line
            for line in code_lines:
                pyautogui.write(line)
                pyautogui.press('enter')
                time.sleep(0.2)
                
        except Exception as e:
            logger.error(f"Failed to add new function: {e}")
            raise
    
    async def _save_changes(self):
        """Save all changes"""
        try:
            pyautogui.hotkey('cmd', 's')
            time.sleep(2)
            logger.info("✅ Changes saved")
        except Exception as e:
            logger.error(f"Failed to save changes: {e}")
            raise
    
    async def _compare_results(self, initial: dict, final: dict, ceo_review: dict) -> dict:
        """Compare before/after results"""
        initial_score = ceo_review.get("overall_score", 0)
        
        # Get new CEO review of final response
        final_review = await self._get_ceo_review("What's urgent today?")
        final_score = final_review.get("overall_score", 0)
        
        improvement = final_score - initial_score
        
        return {
            "initial_score": initial_score,
            "final_score": final_score,
            "improvement": improvement,
            "improvement_percentage": (improvement / max(initial_score, 0.1)) * 100 if initial_score > 0 else 0
        }

# Flask app for real MCP integration
app = Flask(__name__)
CORS(app)

# Global MCP integrator
mcp_integrator = RealMCPCursorIntegration()

@app.route('/api/real-mcp/run-cycle', methods=['POST'])
def run_real_mcp_cycle():
    """Run complete MCP improvement cycle"""
    try:
        data = request.get_json()
        test_message = data.get('message', "What's urgent today?")
        
        # Run cycle in background
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                mcp_integrator.run_complete_mcp_cycle(test_message)
            )
        finally:
            loop.close()
        
        return jsonify({
            "status": "success",
            "result": result
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })

@app.route('/api/real-mcp/status', methods=['GET'])
def get_real_mcp_status():
    """Get real MCP system status"""
    return jsonify({
        "system": "Real MCP Cursor Integration",
        "status": "operational",
        "capabilities": [
            "Jarvis execution",
            "CEO review integration", 
            "Cursor code modification",
            "Automatic improvement implementation",
            "Before/after comparison"
        ],
        "improvement_history": mcp_integrator.improvement_history
    })

if __name__ == '__main__':
    print("🔄 REAL MCP Cursor Integration")
    print("=" * 50)
    print("🚀 Capabilities:")
    print("• Runs Jarvis and gets CEO review")
    print("• Extracts actionable code improvements")
    print("• Actually modifies code in Cursor")
    print("• Re-tests and compares results")
    print("• Complete feedback loop")
    print("=" * 50)
    
    app.run(port=5004, debug=True) 