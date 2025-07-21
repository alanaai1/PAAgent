#!/usr/bin/env python3
"""
Complete MCP Demo - Jarvis → CEO Review → Send to Cursor → Cursor implements → Re-test
Demonstrates the full feedback loop with both servers running simultaneously
"""

import asyncio
import json
import subprocess
import time
import os
from datetime import datetime
import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import threading

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CompleteMCPDemo:
    """Complete MCP demonstration with both servers running"""
    
    def __init__(self):
        self.jarvis_server_url = "http://localhost:5000"
        self.ceo_review_url = "http://localhost:5003"
        self.cursor_feedback_file = "cursor_feedback.md"
        self.demo_results = []
        
    async def run_complete_demo(self, test_message: str = "What's urgent today?"):
        """Run complete MCP demonstration"""
        logger.info("🎯 COMPLETE MCP DEMO: Starting full feedback loop")
        
        try:
            # Step 1: Test Jarvis (api_server.py) - The Brain
            logger.info("🧠 STEP 1: Testing Jarvis (api_server.py) - The Brain")
            initial_response = await self._test_jarvis(test_message)
            logger.info(f"📊 Jarvis Response: {initial_response.get('message', 'No response')[:100]}...")
            
            # Step 2: CEO Review of Jarvis's performance
            logger.info("💼 STEP 2: CEO Review of Jarvis's performance")
            ceo_review = await self._get_ceo_review(test_message)
            logger.info(f"📈 CEO Score: {ceo_review.get('overall_score', 0):.2f}/1.0")
            
            # Step 3: Send feedback to Cursor
            logger.info("📤 STEP 3: Sending feedback to Cursor")
            cursor_feedback = await self._send_to_cursor(ceo_review)
            
            # Step 4: Simulate Cursor implementing improvements
            logger.info("🔧 STEP 4: Cursor implementing improvements")
            implementation_result = await self._simulate_cursor_implementation(ceo_review)
            
            # Step 5: Re-test Jarvis with improvements
            logger.info("🔄 STEP 5: Re-testing Jarvis with improvements")
            final_response = await self._test_jarvis(test_message)
            
            # Step 6: Compare results
            logger.info("📊 STEP 6: Comparing before/after results")
            comparison = await self._compare_results(initial_response, final_response, ceo_review)
            
            # Store demo results
            demo_result = {
                "cycle": len(self.demo_results) + 1,
                "initial_response": initial_response,
                "ceo_review": ceo_review,
                "cursor_feedback": cursor_feedback,
                "implementation_result": implementation_result,
                "final_response": final_response,
                "comparison": comparison,
                "timestamp": datetime.now().isoformat()
            }
            
            self.demo_results.append(demo_result)
            
            return demo_result
            
        except Exception as e:
            logger.error(f"Complete MCP demo failed: {e}")
            return {"error": str(e)}
    
    async def _test_jarvis(self, message: str) -> dict:
        """Test Jarvis (api_server.py) - The Brain"""
        try:
            response = requests.post(
                f"{self.jarvis_server_url}/api/jarvis/chat",
                json={"message": message, "personality": {"conscientiousness": 80}},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info("✅ Jarvis (api_server.py) responded successfully")
                return result
            else:
                logger.error(f"❌ Jarvis failed: {response.status_code}")
                return {"error": f"Jarvis failed: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ Jarvis error: {e}")
            return {"error": f"Jarvis error: {e}"}
    
    async def _get_ceo_review(self, message: str) -> dict:
        """Get CEO review of Jarvis's performance"""
        try:
            response = requests.post(
                f"{self.ceo_review_url}/api/mcp/run-review",
                json={"message": message},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                ceo_feedback = result.get("result", {}).get("cursor_feedback", {})
                logger.info("✅ CEO review completed successfully")
                return ceo_feedback
            else:
                logger.error(f"❌ CEO review failed: {response.status_code}")
                return {"error": f"CEO review failed: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ CEO review error: {e}")
            return {"error": f"CEO review error: {e}"}
    
    async def _send_to_cursor(self, ceo_review: dict) -> dict:
        """Send CEO feedback to Cursor"""
        try:
            # Format feedback for Cursor
            feedback_message = self._format_cursor_feedback(ceo_review)
            
            # Save feedback to file (simulating sending to Cursor)
            with open(self.cursor_feedback_file, 'w') as f:
                f.write(feedback_message)
            
            logger.info("✅ Feedback sent to Cursor")
            return {
                "status": "sent",
                "feedback_file": self.cursor_feedback_file,
                "message": "Feedback sent to Cursor's chat interface"
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to send to Cursor: {e}")
            return {"status": "failed", "error": str(e)}
    
    def _format_cursor_feedback(self, ceo_review: dict) -> str:
        """Format CEO feedback for Cursor"""
        score = ceo_review.get("overall_score", 0)
        verdict = ceo_review.get("ceo_verdict", "No verdict")
        improvement_areas = ceo_review.get("improvement_areas", [])
        
        feedback = f"""🎯 **CEO Review Feedback - {datetime.now().strftime('%Y-%m-%d %H:%M')}**

📊 **Jarvis Performance Score**: {score:.2f}/1.0
💼 **CEO Verdict**: {verdict}

🔧 **Improvements Needed in api_server.py**:
"""
        
        for area in improvement_areas:
            feedback += f"""
**{area['area'].replace('_', ' ').title()}** - {area['priority']} Priority
• Issue: {area['suggestion']}
• Code to implement:
```python
{area['code_improvement']}
```

"""
        
        feedback += f"""
🚀 **Next Steps for Cursor**:
1. Review this CEO feedback
2. Implement the suggested improvements in api_server.py
3. Test the improvements
4. Let me know when ready for re-testing

**Please implement these improvements and respond with 'IMPROVEMENTS_READY' when done.**
"""
        
        return feedback
    
    async def _simulate_cursor_implementation(self, ceo_review: dict) -> dict:
        """Simulate Cursor implementing the improvements"""
        try:
            logger.info("🔧 Simulating Cursor implementing improvements...")
            
            # Simulate Cursor reading the feedback and implementing improvements
            improvements_applied = []
            
            for area in ceo_review.get("improvement_areas", []):
                if area["priority"] == "HIGH":
                    improvement = await self._apply_improvement_to_api_server(area)
                    improvements_applied.append(improvement)
            
            logger.info(f"✅ Cursor applied {len(improvements_applied)} improvements")
            return {
                "status": "completed",
                "improvements_applied": improvements_applied,
                "message": "Cursor has implemented the CEO's suggested improvements"
            }
            
        except Exception as e:
            logger.error(f"❌ Cursor implementation failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def _apply_improvement_to_api_server(self, improvement: dict) -> dict:
        """Apply improvement to api_server.py"""
        try:
            area = improvement["area"]
            code_improvement = improvement["code_improvement"]
            
            # Read current api_server.py
            api_server_path = "api_server.py"
            with open(api_server_path, 'r') as f:
                content = f.read()
            
            # Add improvement comment
            improvement_comment = f"\n# CEO MCP Improvement - {area.replace('_', ' ').title()}\n"
            improvement_comment += f"# Applied: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
            
            # Add the improvement code
            if "add_action_items" in code_improvement:
                # Add action items function if not present
                if "def add_action_items" not in content:
                    content += improvement_comment + code_improvement + "\n"
                    logger.info("✅ Added add_action_items function")
            
            # Write back to file
            with open(api_server_path, 'w') as f:
                f.write(content)
            
            return {
                "area": area,
                "status": "applied",
                "file": api_server_path,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to apply improvement: {e}")
            return {"area": improvement.get("area", "unknown"), "status": "failed", "error": str(e)}
    
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
            "improvement_percentage": (improvement / max(initial_score, 0.1)) * 100 if initial_score > 0 else 0,
            "verdict": "IMPROVED" if improvement > 0 else "NO_CHANGE" if improvement == 0 else "DEGRADED"
        }

# Flask app for complete MCP demo
app = Flask(__name__)
CORS(app)

# Global demo instance
mcp_demo = CompleteMCPDemo()

@app.route('/api/mcp-demo/run', methods=['POST'])
def run_complete_demo():
    """Run complete MCP demonstration"""
    try:
        data = request.get_json()
        test_message = data.get('message', "What's urgent today?")
        
        # Run demo in background
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                mcp_demo.run_complete_demo(test_message)
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

@app.route('/api/mcp-demo/status', methods=['GET'])
def get_demo_status():
    """Get demo status"""
    return jsonify({
        "system": "Complete MCP Demo",
        "status": "operational",
        "demo_runs": len(mcp_demo.demo_results),
        "capabilities": [
            "Jarvis (api_server.py) testing",
            "CEO review of Jarvis performance",
            "Cursor feedback integration",
            "Automatic improvement implementation",
            "Before/after comparison"
        ],
        "last_demo": mcp_demo.demo_results[-1] if mcp_demo.demo_results else None
    })

if __name__ == '__main__':
    print("🎯 COMPLETE MCP DEMO")
    print("=" * 50)
    print("🚀 Full Feedback Loop:")
    print("• Jarvis (api_server.py) - The Brain")
    print("• CEO Review - Reviews Jarvis's performance")
    print("• Send to Cursor - Feedback to Cursor")
    print("• Cursor implements - Modifies api_server.py")
    print("• Re-test - Tests improved Jarvis")
    print("=" * 50)
    print("💡 Both servers must be running:")
    print("• Jarvis: python3 api_server.py (port 5000)")
    print("• CEO Review: python3 proper_mcp_system.py (port 5003)")
    print("=" * 50)
    
    app.run(port=5006, debug=True) 