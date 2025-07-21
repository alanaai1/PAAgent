#!/usr/bin/env python3
"""
Real Cursor Integration
Actually sends messages to Cursor's chat interface
"""

import asyncio
import aiohttp
import json
import time
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RealCursorIntegration:
    """Real integration with Cursor's chat interface"""
    
    def __init__(self):
        self.cursor_websocket_url = "ws://localhost:3000"  # Cursor's WebSocket
        self.cursor_http_url = "http://localhost:3000"     # Cursor's HTTP API
        self.session = None
        
    async def connect_to_cursor(self):
        """Connect to Cursor's WebSocket interface"""
        try:
            self.session = aiohttp.ClientSession()
            logger.info("🔌 Attempting to connect to Cursor...")
            
            # Try WebSocket first
            try:
                async with self.session.ws_connect(self.cursor_websocket_url) as ws:
                    logger.info("✅ Connected to Cursor via WebSocket")
                    return ws
            except Exception as e:
                logger.warning(f"⚠️ WebSocket failed: {e}")
                
            # Fallback to HTTP
            logger.info("🔄 Trying HTTP connection to Cursor...")
            async with self.session.get(f"{self.cursor_http_url}/api/status") as response:
                if response.status == 200:
                    logger.info("✅ Connected to Cursor via HTTP")
                    return "http"
                else:
                    logger.error("❌ Cursor not accessible")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Failed to connect to Cursor: {e}")
            return None
    
    async def send_message_to_cursor(self, message: str, improvement_type: str = "general"):
        """Send a message directly to Cursor's chat interface"""
        try:
            # Format the message for Cursor
            cursor_message = {
                "type": "mcp_feedback",
                "content": message,
                "improvement_type": improvement_type,
                "timestamp": datetime.now().isoformat(),
                "source": "mcp_coordinator"
            }
            
            # Try WebSocket first
            try:
                async with self.session.ws_connect(self.cursor_websocket_url) as ws:
                    await ws.send_json(cursor_message)
                    logger.info("✅ Message sent to Cursor via WebSocket")
                    return True
            except Exception as e:
                logger.warning(f"⚠️ WebSocket send failed: {e}")
            
            # Fallback to HTTP
            try:
                async with self.session.post(
                    f"{self.cursor_http_url}/api/chat",
                    json=cursor_message,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        logger.info("✅ Message sent to Cursor via HTTP")
                        return True
                    else:
                        logger.error(f"❌ HTTP send failed: {response.status}")
                        return False
            except Exception as e:
                logger.error(f"❌ HTTP send failed: {e}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to send message to Cursor: {e}")
            return False
    
    async def send_improvement_feedback(self, ceo_review: dict):
        """Send CEO feedback as improvement suggestions to Cursor"""
        try:
            # Extract improvement suggestions
            improvements = ceo_review.get("improvements", [])
            score = ceo_review.get("score", 0)
            
            # Format message for Cursor
            message = f"""
🎯 MCP IMPROVEMENT FEEDBACK

📊 Current Score: {score}/1.0

🔧 IMPROVEMENTS NEEDED:
"""
            
            for i, improvement in enumerate(improvements, 1):
                message += f"""
{i}. {improvement.get('type', 'General')}:
   - {improvement.get('description', 'No description')}
   - Priority: {improvement.get('priority', 'Medium')}
   - Code: {improvement.get('code', 'No code provided')}
"""
            
            message += f"""
💡 ACTION REQUIRED:
Please implement these improvements in api_server.py to enhance Jarvis's performance.

🔄 Next review cycle will test the improvements.
"""
            
            # Send to Cursor
            success = await self.send_message_to_cursor(message, "improvement_feedback")
            
            if success:
                logger.info("✅ Improvement feedback sent to Cursor")
                return True
            else:
                logger.warning("⚠️ Failed to send feedback to Cursor, saving to file")
                # Fallback to file
                self._save_feedback_to_file(message)
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to send improvement feedback: {e}")
            return False
    
    def _save_feedback_to_file(self, message: str):
        """Fallback: save feedback to file"""
        try:
            with open("cursor_feedback.md", "w") as f:
                f.write(f"# Cursor Feedback - {datetime.now()}\n\n")
                f.write(message)
            logger.info("📁 Feedback saved to cursor_feedback.md")
        except Exception as e:
            logger.error(f"❌ Failed to save feedback: {e}")
    
    async def wait_for_cursor_implementation(self, timeout: int = 60):
        """Wait for Cursor to implement improvements"""
        logger.info(f"⏳ Waiting {timeout}s for Cursor implementation...")
        
        # Monitor api_server.py for changes
        initial_mtime = self._get_file_mtime("api_server.py")
        
        for i in range(timeout):
            await asyncio.sleep(1)
            current_mtime = self._get_file_mtime("api_server.py")
            
            if current_mtime > initial_mtime:
                logger.info("✅ Detected changes in api_server.py")
                return True
        
        logger.warning("⚠️ No changes detected in api_server.py")
        return False
    
    def _get_file_mtime(self, filename: str) -> float:
        """Get file modification time"""
        try:
            import os
            return os.path.getmtime(filename)
        except:
            return 0
    
    async def close(self):
        """Close the session"""
        if self.session:
            await self.session.close()

# Test function
async def test_cursor_integration():
    """Test the Cursor integration"""
    cursor = RealCursorIntegration()
    
    try:
        # Test connection
        connection = await cursor.connect_to_cursor()
        if not connection:
            logger.error("❌ Could not connect to Cursor")
            return False
        
        # Test message sending
        test_message = "🧪 MCP Test: This is a test message from the MCP system"
        success = await cursor.send_message_to_cursor(test_message, "test")
        
        if success:
            logger.info("✅ Cursor integration test successful")
            return True
        else:
            logger.warning("⚠️ Cursor integration test failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Cursor integration test failed: {e}")
        return False
    finally:
        await cursor.close()

if __name__ == "__main__":
    asyncio.run(test_cursor_integration()) 