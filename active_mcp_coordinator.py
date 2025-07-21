#!/usr/bin/env python3
"""
Active MCP Coordinator - Automatically runs the complete cycle
Jarvis → CEO Review → Send to Cursor → Cursor implements → Re-test
"""

import asyncio
import json
import time
import requests
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ActiveMCPCoordinator:
    """Active coordinator that automatically runs the MCP cycle"""
    
    def __init__(self):
        self.jarvis_url = "http://localhost:5000"
        self.ceo_review_url = "http://localhost:5003"
        self.cycle_count = 0
        self.running = True
        
    async def start_active_cycle(self):
        """Start the active MCP cycle that runs automatically"""
        logger.info("🚀 ACTIVE MCP COORDINATOR: Starting automatic cycle")
        
        while self.running:
            try:
                self.cycle_count += 1
                logger.info(f"🔄 CYCLE {self.cycle_count}: Starting automatic MCP cycle")
                
                # Step 1: Test Jarvis
                logger.info("🧠 STEP 1: Testing Jarvis (api_server.py)")
                jarvis_response = await self._test_jarvis("What's urgent today?")
                
                if jarvis_response.get("error"):
                    logger.error(f"❌ Jarvis failed: {jarvis_response['error']}")
                    await asyncio.sleep(10)
                    continue
                
                logger.info(f"✅ Jarvis responded: {jarvis_response.get('message', 'No message')[:100]}...")
                
                # Step 2: Get CEO Review
                logger.info("💼 STEP 2: Getting CEO Review")
                ceo_review = await self._get_ceo_review("What's urgent today?")
                
                if ceo_review.get("error"):
                    logger.error(f"❌ CEO Review failed: {ceo_review['error']}")
                    await asyncio.sleep(10)
                    continue
                
                score = ceo_review.get("overall_score", 0)
                logger.info(f"📊 CEO Score: {score:.2f}/1.0")
                
                # Step 3: Send feedback to Cursor
                logger.info("📤 STEP 3: Sending feedback to Cursor")
                feedback_result = await self._send_feedback_to_cursor(ceo_review)
                
                # Step 4: Implement improvements
                logger.info("🔧 STEP 4: Implementing improvements")
                implementation_result = await self._implement_improvements(ceo_review)
                
                # Step 5: Re-test Jarvis
                logger.info("🔄 STEP 5: Re-testing Jarvis with improvements")
                final_response = await self._test_jarvis("What's urgent today?")
                
                # Step 6: Compare results
                logger.info("📊 STEP 6: Comparing results")
                comparison = await self._compare_results(jarvis_response, final_response, ceo_review)
                
                # Log results
                logger.info(f"🎯 CYCLE {self.cycle_count} COMPLETE:")
                logger.info(f"   Initial Score: {comparison.get('initial_score', 0):.2f}")
                logger.info(f"   Final Score: {comparison.get('final_score', 0):.2f}")
                logger.info(f"   Improvement: {comparison.get('improvement', 0):.2f}")
                logger.info(f"   Verdict: {comparison.get('verdict', 'UNKNOWN')}")
                
                # Wait before next cycle
                logger.info("⏳ Waiting 30 seconds before next cycle...")
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"❌ Cycle {self.cycle_count} failed: {e}")
                await asyncio.sleep(10)
    
    async def _test_jarvis(self, message: str) -> dict:
        """Test Jarvis API"""
        try:
            response = requests.post(
                f"{self.jarvis_url}/api/jarvis/chat",
                json={"message": message, "personality": {"conscientiousness": 80}},
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Jarvis failed: {response.status_code}"}
                
        except Exception as e:
            return {"error": f"Jarvis error: {e}"}
    
    async def _get_ceo_review(self, message: str) -> dict:
        """Get CEO review"""
        try:
            response = requests.post(
                f"{self.ceo_review_url}/api/mcp/run-review",
                json={"message": message},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("result", {}).get("cursor_feedback", {})
            else:
                return {"error": f"CEO review failed: {response.status_code}"}
                
        except Exception as e:
            return {"error": f"CEO review error: {e}"}
    
    async def _send_feedback_to_cursor(self, ceo_review: dict) -> dict:
        """Send feedback to Cursor"""
        try:
            # Format feedback
            feedback = self._format_feedback(ceo_review)
            
            # Try real Cursor integration first
            try:
                from real_cursor_integration import RealCursorIntegration
                cursor = RealCursorIntegration()
                
                # Try to send real message to Cursor
                success = await cursor.send_improvement_feedback(ceo_review)
                
                if success:
                    logger.info("✅ Real feedback sent to Cursor chat")
                else:
                    logger.warning("⚠️ Real Cursor send failed, using file fallback")
                    # Fallback to file method
                    self._save_feedback_to_file(feedback)
                
                await cursor.close()
                
            except Exception as e:
                logger.warning(f"⚠️ Real Cursor integration failed: {e}")
                # Fallback to file method
                self._save_feedback_to_file(feedback)
            
            return {"status": "sent", "feedback": feedback}
            
        except Exception as e:
            logger.error(f"❌ Failed to send feedback: {e}")
            return {"error": str(e)}
    
    def _save_feedback_to_file(self, feedback: str):
        """Fallback: save feedback to file"""
        try:
            with open("cursor_feedback.md", "w") as f:
                f.write(feedback)
            logger.info("📁 Feedback saved to cursor_feedback.md")
        except Exception as e:
            logger.error(f"❌ Failed to save feedback to file: {e}")
    
    def _format_feedback(self, ceo_review: dict) -> str:
        """Format CEO feedback"""
        score = ceo_review.get("overall_score", 0)
        verdict = ceo_review.get("ceo_verdict", "No verdict")
        
        feedback = f"""🎯 **CEO Review Feedback - Cycle {self.cycle_count}**

📊 **Jarvis Performance Score**: {score:.2f}/1.0
💼 **CEO Verdict**: {verdict}

🔧 **Improvements Needed**:
"""
        
        for area in ceo_review.get("improvement_areas", []):
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
    
    async def _implement_improvements(self, ceo_review: dict) -> dict:
        """Implement improvements automatically"""
        try:
            improvements_applied = []
            
            for area in ceo_review.get("improvement_areas", []):
                if area["priority"] == "HIGH":
                    improvement = await self._apply_improvement(area)
                    improvements_applied.append(improvement)
            
            logger.info(f"✅ Applied {len(improvements_applied)} improvements")
            return {
                "status": "completed",
                "improvements_applied": improvements_applied
            }
            
        except Exception as e:
            logger.error(f"❌ Implementation failed: {e}")
            return {"error": str(e)}
    
    async def _apply_improvement(self, improvement: dict) -> dict:
        """Apply a single improvement"""
        try:
            area = improvement["area"]
            code_improvement = improvement["code_improvement"]
            
            # Read current api_server.py
            with open("api_server.py", "r") as f:
                content = f.read()
            
            # Add improvement comment
            improvement_comment = f"\n# CEO MCP Improvement - {area.replace('_', ' ').title()}\n"
            improvement_comment += f"# Applied: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
            
            # Add the improvement code
            if "add_action_items" in code_improvement and "def add_action_items" not in content:
                content += improvement_comment + code_improvement + "\n"
                logger.info("✅ Added add_action_items function")
            
            # Write back to file
            with open("api_server.py", "w") as f:
                f.write(content)
            
            return {
                "area": area,
                "status": "applied",
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

async def main():
    """Run the active MCP coordinator"""
    print("🚀 ACTIVE MCP COORDINATOR")
    print("=" * 50)
    print("🎯 Automatic Cycle:")
    print("• Jarvis → CEO Review → Send to Cursor")
    print("• Cursor implements → Re-test")
    print("• Continuous improvement loop")
    print("=" * 50)
    print("💡 Both servers must be running:")
    print("• Jarvis: python3 api_server.py (port 5000)")
    print("• CEO Review: python3 proper_mcp_system.py (port 5003)")
    print("=" * 50)
    
    coordinator = ActiveMCPCoordinator()
    await coordinator.start_active_cycle()

if __name__ == '__main__':
    asyncio.run(main()) 