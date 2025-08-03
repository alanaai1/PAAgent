#!/usr/bin/env python3
"""
Cursor Message Sender
Sends improvement feedback directly to Cursor's chat interface
"""

import subprocess
import time
import json
import os
from datetime import datetime

class CursorMessageSender:
    """Send messages to Cursor's chat interface"""
    
    def __init__(self):
        self.cursor_app = "/Applications/Cursor.app"
        self.message_file = "cursor_message.md"
        
    def send_improvement_feedback(self, ceo_review: dict):
        """Send CEO feedback as a message to Cursor"""
        try:
            # Extract data from CEO review
            score = ceo_review.get("overall_score", 0)
            improvements = ceo_review.get("improvement_areas", [])
            
            # Format message for Cursor
            message = f"""
🎯 **MCP IMPROVEMENT FEEDBACK - {datetime.now().strftime('%H:%M:%S')}**

📊 **Current Jarvis Score**: {score:.2f}/1.0

🔧 **IMPROVEMENTS NEEDED**:
"""
            
            for i, area in enumerate(improvements, 1):
                message += f"""
**{i}. {area.get('area', 'General').replace('_', ' ').title()}** - {area.get('priority', 'Medium')} Priority
• Issue: {area.get('suggestion', 'No suggestion')}
• Code to implement:
```python
{area.get('code_improvement', '# Add improvement code here')}
```
"""
            
            message += f"""
💡 **ACTION REQUIRED**:
Please implement these improvements in api_server.py to enhance Jarvis's performance.

🔄 **Next review cycle will test the improvements.**

---
*Sent by MCP Coordinator at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
            
            # Save message to file
            with open(self.message_file, "w") as f:
                f.write(message)
            
            # Try to open Cursor and focus on the file
            self._open_cursor_with_message()
            
            print("✅ Improvement feedback sent to Cursor")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send feedback: {e}")
            return False
    
    def _open_cursor_with_message(self):
        """Open Cursor and focus on the message file"""
        try:
            # Open Cursor with the message file
            subprocess.run([
                "open", "-a", "Cursor", self.message_file
            ], check=True)
            
            # Wait a moment for Cursor to open
            time.sleep(2)
            
            # Try to copy message to clipboard for easy pasting
            self._copy_to_clipboard()
            
            print("📁 Message opened in Cursor")
            
        except Exception as e:
            print(f"⚠️ Could not open Cursor: {e}")
    
    def _copy_to_clipboard(self):
        """Copy message to clipboard"""
        try:
            with open(self.message_file, "r") as f:
                content = f.read()
            
            # Use pbcopy to copy to clipboard
            subprocess.run([
                "pbcopy"
            ], input=content.encode(), check=True)
            
            print("📋 Message copied to clipboard - paste in Cursor chat")
            
        except Exception as e:
            print(f"⚠️ Could not copy to clipboard: {e}")
    
    def send_simple_message(self, message: str):
        """Send a simple message to Cursor"""
        try:
            # Save simple message
            with open(self.message_file, "w") as f:
                f.write(f"🤖 **MCP Message**: {message}\n\n*{datetime.now().strftime('%H:%M:%S')}*")
            
            # Open in Cursor
            self._open_cursor_with_message()
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to send simple message: {e}")
            return False

def test_cursor_sender():
    """Test the Cursor message sender"""
    sender = CursorMessageSender()
    
    # Test with sample CEO review
    test_review = {
        "overall_score": 0.47,
        "improvement_areas": [
            {
                "area": "business_focus",
                "priority": "High",
                "suggestion": "Add more specific business metrics and KPIs",
                "code_improvement": """
def add_business_metrics(response):
    metrics = {
        "revenue_impact": "High",
        "time_saved": "2 hours/week",
        "roi_estimate": "300%"
    }
    return response + f"\\n\\n📊 Business Impact: {metrics}"
"""
            },
            {
                "area": "action_orientation", 
                "priority": "Medium",
                "suggestion": "Include specific next steps with timelines",
                "code_improvement": """
def add_action_steps(response):
    steps = [
        "1. Review proposal by EOD",
        "2. Schedule client meeting tomorrow", 
        "3. Follow up in 48 hours"
    ]
    return response + "\\n\\n🎯 Next Steps:\\n" + "\\n".join(steps)
"""
            }
        ]
    }
    
    success = sender.send_improvement_feedback(test_review)
    
    if success:
        print("✅ Test message sent to Cursor successfully!")
    else:
        print("❌ Test failed")

if __name__ == "__main__":
    test_cursor_sender() 