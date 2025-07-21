#!/usr/bin/env python3
"""
Production Jarvis with MCP Integration
Combines the existing chat functionality with self-improvement capabilities
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import asyncio
import threading
import time
from datetime import datetime
import logging

# Import existing Jarvis functionality
from api_server import (
    analyze_with_ai, generate_response, log_error,
    get_calendar_service, fetch_recent_emails, get_gmail_service,
    generate_greeting
)

# Import MCP capabilities
from mcp_advanced import AdvancedMCPJarvis, RealComputerControl

app = Flask(__name__)
CORS(app)

logger = logging.getLogger(__name__)

class ProductionJarvisMCP:
    """Production Jarvis with MCP self-improvement capabilities"""
    
    def __init__(self):
        self.mcp_jarvis = AdvancedMCPJarvis()
        self.memory = {}  # Conversation memory
        self.last_urgent_items = []  # Remember urgent items for context
        self.improvement_thread = None
        self.running = True
        
    def start_background_improvement(self):
        """Start background self-improvement process"""
        if not self.improvement_thread or not self.improvement_thread.is_alive():
            self.improvement_thread = threading.Thread(
                target=self._background_improvement_loop,
                daemon=True
            )
            self.improvement_thread.start()
            logger.info("🚀 Background self-improvement started")
    
    def _background_improvement_loop(self):
        """Background loop for continuous self-improvement"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            while self.running:
                # Check if improvement is needed (every 30 minutes)
                if self.mcp_jarvis.current_performance < self.mcp_jarvis.performance_threshold:
                    logger.info("🔧 Background self-improvement triggered")
                    loop.run_until_complete(self.mcp_jarvis.self_improve())
                
                # Wait before next check
                time.sleep(1800)  # 30 minutes
                
        except Exception as e:
            log_error("background_improvement_loop", e)
        finally:
            loop.close()
    
    def store_conversation_context(self, message: str, response: str, analysis: dict):
        """Store conversation context for memory continuity"""
        context_key = f"conversation_{int(time.time())}"
        
        self.memory[context_key] = {
            'message': message,
            'response': response,
            'analysis': analysis,
            'timestamp': datetime.now().isoformat()
        }
        
        # Extract urgent items for reference
        if analysis and 'urgent_priorities' in analysis:
            self.last_urgent_items = analysis['urgent_priorities']
            self.memory['current_urgent_items'] = self.last_urgent_items
    
    def get_context_for_message(self, message: str) -> dict:
        """Get relevant context for the current message"""
        message_lower = message.lower()
        
        # Check if user is referencing previous urgent items
        if any(phrase in message_lower for phrase in ['item 1', 'item 2', 'do item', 'first item', 'second item']):
            return {
                'urgent_items': self.last_urgent_items,
                'context_type': 'urgent_item_reference'
            }
        
        # Check if user wants to continue previous conversation
        if any(phrase in message_lower for phrase in ['continue', 'do it', 'go ahead', 'proceed']):
            recent_conversations = [
                ctx for ctx in self.memory.values() 
                if isinstance(ctx, dict) and 'message' in ctx
            ][-3:]  # Last 3 conversations
            
            return {
                'recent_conversations': recent_conversations,
                'context_type': 'continuation'
            }
        
        return {}
    
    def resolve_item_reference(self, message: str) -> str:
        """Resolve references like 'do item 1' to specific actions"""
        message_lower = message.lower()
        
        if 'item 1' in message_lower or 'first item' in message_lower:
            if self.last_urgent_items and len(self.last_urgent_items) > 0:
                first_item = self.last_urgent_items[0]
                sender = first_item.get('sender', 'Unknown')
                
                if 'github' in sender.lower():
                    return "help me secure GitHub"
                elif 'companies house' in first_item.get('content', '').lower():
                    return "help me verify Companies House"
                else:
                    return f"help me with {sender}"
        
        elif 'item 2' in message_lower or 'second item' in message_lower:
            if self.last_urgent_items and len(self.last_urgent_items) > 1:
                second_item = self.last_urgent_items[1]
                sender = second_item.get('sender', 'Unknown')
                
                if 'companies house' in second_item.get('content', '').lower():
                    return "help me verify Companies House"
                else:
                    return f"help me with {sender}"
        
        return message  # Return original if no resolution needed

# Global instance
jarvis_mcp = ProductionJarvisMCP()

@app.route('/api/jarvis/chat', methods=['POST'])
def jarvis_chat_with_mcp():
    """Enhanced Jarvis chat with MCP memory and context awareness"""
    try:
        data = request.get_json()
        original_message = data.get('message', '')
        personality = data.get('personality', {})
        
        # Resolve item references using MCP memory
        resolved_message = jarvis_mcp.resolve_item_reference(original_message)
        
        print(f"JARVIS MCP: {original_message}")
        if resolved_message != original_message:
            print(f"RESOLVED TO: {resolved_message}")
        
        # Get context from MCP memory
        context = jarvis_mcp.get_context_for_message(resolved_message)
        
        # Get business data
        try:
            calendar_service = get_calendar_service()
            gmail_service = get_gmail_service()
            
            events = calendar_service.events().list(
                calendarId='primary',
                timeMin=datetime.utcnow().isoformat() + 'Z',
                maxResults=10,
                singleEvents=True,
                orderBy='startTime'
            ).execute().get('items', [])
            
            emails = fetch_recent_emails(gmail_service, hours=24)
            
        except Exception as e:
            log_error("jarvis_chat_with_mcp", f"Failed to fetch data: {e}")
            events = []
            emails = []
        
        # Analyze with AI
        analysis = analyze_with_ai(resolved_message, emails, events)
        
        # Generate response with context awareness
        if context.get('context_type') == 'urgent_item_reference':
            # User is asking about specific urgent items
            greeting = generate_greeting(personality)
            response_text = _generate_contextual_action_response(
                greeting, resolved_message, context['urgent_items']
            )
        else:
            # Normal response generation
            response_text = generate_response(resolved_message, analysis, personality)
        
        # Store conversation context in MCP memory
        jarvis_mcp.store_conversation_context(original_message, response_text, analysis)
        
        return jsonify({
            'message': response_text,
            'type': 'response',
            'context_used': context.get('context_type', 'none'),
            'mcp_performance': jarvis_mcp.mcp_jarvis.current_performance
        })
        
    except Exception as e:
        log_error("jarvis_chat_with_mcp", f"Request failed: {e}")
        return jsonify({
            'message': "I'm having trouble right now. Please try again.",
            'type': 'error'
        })

def _generate_contextual_action_response(greeting: str, message: str, urgent_items: list) -> str:
    """Generate response when user references specific urgent items"""
    message_lower = message.lower()
    
    if 'github' in message_lower and 'secure' in message_lower:
        return f"""{greeting} I'll help you secure your GitHub account right now:

🔐 **GitHub Security Action Plan:**

**Step 1: Verify Login Location**
• I can check if the recent login location matches your current IP
• Compare the login timestamp with your actual activity

**Step 2: Enable Two-Factor Authentication**
• If not already enabled, I'll guide you through 2FA setup
• Use your phone or authenticator app for maximum security

**Step 3: Review Account Activity**
• Check recent commits, repository access, and account changes
• Look for any unauthorized activity or suspicious patterns

**Step 4: Secure Account Settings**
• Update password if needed
• Review authorized applications and revoke suspicious ones
• Enable security alerts for future monitoring

💡 **Next:** Would you like me to start with Step 1 and check the login location? Say 'yes, check GitHub login' and I'll begin the verification process."""

    elif 'companies house' in message_lower:
        return f"""{greeting} I'll help you complete the Companies House identity verification:

📋 **Companies House Verification Action Plan:**

**Step 1: Gather Required Documents**
• Valid photo ID (passport or driving license)
• Proof of address (utility bill or bank statement)
• Company authentication code from your confirmation statement

**Step 2: Access Verification Portal**
• I can navigate you to: gov.uk/companies-house-identity-verification
• Help you log in with your Companies House account

**Step 3: Complete Verification Process**
• Upload clear photos of your documents
• Follow the step-by-step identity verification
• Submit the verification request

**Step 4: Confirmation & Follow-up**
• You'll receive email confirmation within 5 working days
• I can help you track the verification status

💡 **Ready to start?** Say 'begin Companies House verification' and I'll guide you through each step, or 'gather documents first' if you need to prepare."""

    else:
        return f"""{greeting} I understand you want to take action on this urgent item.

**What I can do:**
• Provide step-by-step guidance for resolving this issue
• Help you draft any necessary responses or communications
• Set up reminders and follow-up actions
• Connect you with relevant resources or contacts

**To get started:**
• Tell me specifically what you'd like me to help with
• Say 'guide me through this' for step-by-step instructions
• Or ask 'what are my options' to see all available actions

💡 **I'm ready to take immediate action - just let me know how you'd like to proceed!**"""

@app.route('/api/jarvis/mcp/status', methods=['GET'])
def get_mcp_status():
    """Get MCP system status"""
    return jsonify({
        'performance': jarvis_mcp.mcp_jarvis.current_performance,
        'target': jarvis_mcp.mcp_jarvis.performance_threshold,
        'improvements_made': jarvis_mcp.mcp_jarvis.improvement_count,
        'memory_items': len(jarvis_mcp.memory),
        'last_urgent_items': len(jarvis_mcp.last_urgent_items),
        'background_improvement_active': (
            jarvis_mcp.improvement_thread and 
            jarvis_mcp.improvement_thread.is_alive()
        )
    })

@app.route('/api/jarvis/mcp/improve', methods=['POST'])
def trigger_manual_improvement():
    """Manually trigger self-improvement"""
    try:
        # Run improvement in background
        improvement_thread = threading.Thread(
            target=lambda: asyncio.run(jarvis_mcp.mcp_jarvis.self_improve()),
            daemon=True
        )
        improvement_thread.start()
        
        return jsonify({
            'status': 'improvement_started',
            'message': 'Self-improvement process initiated'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

if __name__ == '__main__':
    print("🤖 Starting Production Jarvis with MCP...")
    print("=" * 50)
    print("Features enabled:")
    print("• Chat with conversation memory")
    print("• Context-aware responses")
    print("• Item reference resolution ('do item 1')")
    print("• Background self-improvement")
    print("• Real computer control capabilities")
    print("=" * 50)
    
    # Start background self-improvement
    jarvis_mcp.start_background_improvement()
    
    # Start Flask server
    app.run(port=5001, debug=True)  # Using port 5001 to avoid conflicts 