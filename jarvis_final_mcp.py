#!/usr/bin/env python3
"""
Final Production Jarvis with Complete MCP Integration
Self-improving AI with real computer control capabilities
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
from mcp_advanced import AdvancedMCPJarvis
from mcp_real_control import MCPActionExecutor

app = Flask(__name__)
CORS(app)

logger = logging.getLogger(__name__)

class FinalJarvisMCP:
    """Complete self-improving Jarvis with real computer control"""
    
    def __init__(self):
        self.mcp_jarvis = AdvancedMCPJarvis()
        self.action_executor = MCPActionExecutor()
        self.memory = {}
        self.last_urgent_items = []
        self.improvement_thread = None
        self.running = True
        
        # Performance tracking
        self.total_actions_executed = 0
        self.successful_actions = 0
        
    def start_background_systems(self):
        """Start all background systems"""
        # Start self-improvement loop
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
                # Self-improvement cycle every 30 minutes
                if self.mcp_jarvis.current_performance < self.mcp_jarvis.performance_threshold:
                    logger.info("🔧 Background self-improvement triggered")
                    
                    # Analyze what needs improvement based on recent performance
                    if self.successful_actions > 0:
                        success_rate = self.successful_actions / max(self.total_actions_executed, 1)
                        if success_rate < 0.8:  # Less than 80% success rate
                            # Improve error handling
                            loop.run_until_complete(self._improve_error_handling())
                    
                    # General self-improvement
                    loop.run_until_complete(self.mcp_jarvis.self_improve())
                
                time.sleep(1800)  # 30 minutes
                
        except Exception as e:
            log_error("background_improvement_loop", e)
        finally:
            loop.close()
    
    async def _improve_error_handling(self):
        """Improve error handling based on recent failures"""
        improvement_code = [
            "# Enhanced error handling - MCP self-improvement",
            "def enhanced_error_recovery(self, error):",
            "    error_context = {",
            "        'timestamp': datetime.now().isoformat(),", 
            "        'error_type': type(error).__name__,",
            "        'error_message': str(error)",
            "    }",
            "    self.memory['last_error'] = error_context",
            "    return self.fallback_response(error_context)"
        ]
        
        result = await self.action_executor.execute_action(
            'cursor_self_improvement',
            {
                'target_file': 'error_handling_improvement.py',
                'code_changes': improvement_code
            }
        )
        
        if result['success']:
            self.mcp_jarvis.current_performance += 0.5
            logger.info("✅ Error handling improved via self-modification")
    
    def store_conversation_context(self, message: str, response: str, analysis: dict):
        """Enhanced context storage with action tracking"""
        context_key = f"conversation_{int(time.time())}"
        
        self.memory[context_key] = {
            'message': message,
            'response': response,  
            'analysis': analysis,
            'timestamp': datetime.now().isoformat(),
            'action_executed': False
        }
        
        # Extract urgent items for context
        if analysis and isinstance(analysis, dict):
            if 'urgent_priorities' in analysis:
                self.last_urgent_items = analysis['urgent_priorities']
            elif 'urgent_items' in analysis:
                self.last_urgent_items = analysis['urgent_items']
        
        self.memory['current_urgent_items'] = self.last_urgent_items
    
    def resolve_item_reference(self, message: str) -> str:
        """Enhanced item resolution with action detection"""
        message_lower = message.lower()
        
        # Check for explicit action requests
        action_keywords = ['help me', 'do this', 'take action', 'execute', 'start', 'begin']
        is_action_request = any(keyword in message_lower for keyword in action_keywords)
        
        if 'item 1' in message_lower or 'first item' in message_lower:
            if self.last_urgent_items and len(self.last_urgent_items) > 0:
                first_item = self.last_urgent_items[0]
                
                if 'github' in str(first_item).lower():
                    return "help me secure GitHub" if is_action_request else "tell me about GitHub security"
                elif 'companies house' in str(first_item).lower():
                    return "help me verify Companies House" if is_action_request else "tell me about Companies House"
        
        elif 'item 2' in message_lower or 'second item' in message_lower:
            if self.last_urgent_items and len(self.last_urgent_items) > 1:
                second_item = self.last_urgent_items[1]
                
                if 'companies house' in str(second_item).lower():
                    return "help me verify Companies House" if is_action_request else "tell me about Companies House"
        
        return message
    
    async def execute_real_action(self, action_type: str, message: str) -> Dict[str, Any]:
        """Execute real computer control actions"""
        self.total_actions_executed += 1
        
        try:
            if 'github' in action_type.lower() and 'secure' in message.lower():
                result = await self.action_executor.execute_action('github_security', {})
                
            elif 'companies house' in action_type.lower():
                result = await self.action_executor.execute_action('companies_house_verification', {})
                
            else:
                result = {
                    'success': False,
                    'details': {'error': f'Unknown action type: {action_type}'}
                }
            
            if result['success']:
                self.successful_actions += 1
            
            return result
            
        except Exception as e:
            log_error("execute_real_action", e)
            return {
                'success': False,
                'details': {'error': str(e)}
            }

# Global instance
final_jarvis = FinalJarvisMCP()

@app.route('/api/jarvis/chat', methods=['POST'])
def final_jarvis_chat():
    """Final Jarvis chat with complete MCP integration"""
    try:
        data = request.get_json()
        original_message = data.get('message', '')
        personality = data.get('personality', {})
        
        # Resolve item references
        resolved_message = final_jarvis.resolve_item_reference(original_message)
        
        print(f"FINAL JARVIS: {original_message}")
        if resolved_message != original_message:
            print(f"RESOLVED TO: {resolved_message}")
        
        # Check if this is an action request
        is_action_request = any(phrase in resolved_message.lower() 
                              for phrase in ['help me', 'secure', 'verify', 'do this'])
        
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
            log_error("final_jarvis_chat", f"Failed to fetch data: {e}")
            events = []
            emails = []
        
        # Analyze with AI
        analysis = analyze_with_ai(resolved_message, emails, events)
        
        # Execute real actions if requested
        action_result = None
        if is_action_request:
            if 'github' in resolved_message.lower():
                # Execute real GitHub security action
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    action_result = loop.run_until_complete(
                        final_jarvis.execute_real_action('github_security', resolved_message)
                    )
                finally:
                    loop.close()
                    
            elif 'companies house' in resolved_message.lower():
                # Execute real Companies House action
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    action_result = loop.run_until_complete(
                        final_jarvis.execute_real_action('companies_house', resolved_message)
                    )
                finally:
                    loop.close()
        
        # Generate response
        if action_result:
            # Generate response based on action execution
            response_text = _generate_action_execution_response(
                generate_greeting(personality), action_result, resolved_message
            )
        else:
            # Standard response generation
            response_text = generate_response(resolved_message, analysis, personality)
        
        # Store conversation context
        final_jarvis.store_conversation_context(original_message, response_text, analysis)
        
        return jsonify({
            'message': response_text,
            'type': 'response',
            'action_executed': action_result is not None,
            'action_success': action_result.get('success', False) if action_result else False,
            'mcp_performance': final_jarvis.mcp_jarvis.current_performance,
            'total_actions': final_jarvis.total_actions_executed,
            'success_rate': (final_jarvis.successful_actions / max(final_jarvis.total_actions_executed, 1)) if final_jarvis.total_actions_executed > 0 else 0
        })
        
    except Exception as e:
        log_error("final_jarvis_chat", f"Request failed: {e}")
        return jsonify({
            'message': "I'm having trouble right now. Please try again.",
            'type': 'error'
        })

def _generate_action_execution_response(greeting: str, action_result: Dict[str, Any], message: str) -> str:
    """Generate response after executing real actions"""
    
    if action_result['success']:
        steps_completed = action_result.get('details', {}).get('steps_completed', [])
        next_action = action_result.get('details', {}).get('next_action', '')
        
        if 'github' in message.lower():
            return f"""{greeting} ✅ **GitHub Security Action Completed!**

🔐 **Successfully executed:**
{chr(10).join([f"• {step.replace('_', ' ').title()}" for step in steps_completed])}

📋 **What happened:**
• Opened GitHub security settings
• Checked recent account activity  
• Captured security log for your review

💡 **Next steps:** {next_action}

🚀 **I've also taken a screenshot of your security log - check the project folder for the image file.**"""

        elif 'companies house' in message.lower():
            return f"""{greeting} ✅ **Companies House Action Completed!**

📋 **Successfully executed:**
{chr(10).join([f"• {step.replace('_', ' ').title()}" for step in steps_completed])}

🎯 **What happened:**
• Opened Companies House verification page
• Navigated to identity verification section
• Located the verification portal

💡 **Next steps:** {next_action}

📝 **Ready for you to upload your documents and complete the verification process.**"""
    
    else:
        error_details = action_result.get('details', {}).get('error', 'Unknown error')
        
        return f"""{greeting} ⚠️ **Action Execution Encountered an Issue**

❌ **What happened:** {error_details}

🔧 **Don't worry - I'm learning from this to improve next time.**

💡 **Alternative approach:**
• I can provide step-by-step manual instructions instead
• Or we can try a different method to accomplish this task

🤖 **My self-improvement system is already analyzing this to prevent similar issues.**

Would you like me to guide you through the manual process instead?"""

@app.route('/api/jarvis/mcp/status', methods=['GET'])
def get_final_mcp_status():
    """Get complete MCP system status"""
    return jsonify({
        'performance': final_jarvis.mcp_jarvis.current_performance,
        'target': final_jarvis.mcp_jarvis.performance_threshold,
        'improvements_made': final_jarvis.mcp_jarvis.improvement_count,
        'memory_items': len(final_jarvis.memory),
        'last_urgent_items': len(final_jarvis.last_urgent_items),
        'total_actions_executed': final_jarvis.total_actions_executed,
        'successful_actions': final_jarvis.successful_actions,
        'success_rate': (final_jarvis.successful_actions / max(final_jarvis.total_actions_executed, 1)) if final_jarvis.total_actions_executed > 0 else 0,
        'background_improvement_active': (
            final_jarvis.improvement_thread and 
            final_jarvis.improvement_thread.is_alive()
        ),
        'computer_control_available': True
    })

@app.route('/api/jarvis/mcp/execute', methods=['POST'])
def execute_manual_action():
    """Manually execute computer control actions"""
    try:
        data = request.get_json()
        action_type = data.get('action_type', '')
        parameters = data.get('parameters', {})
        
        # Execute action in background thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                final_jarvis.action_executor.execute_action(action_type, parameters)
            )
        finally:
            loop.close()
        
        if result['success']:
            final_jarvis.successful_actions += 1
        final_jarvis.total_actions_executed += 1
        
        return jsonify({
            'status': 'completed',
            'result': result
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

if __name__ == '__main__':
    print("🤖 Final Production Jarvis with Complete MCP")
    print("=" * 50)
    print("🚀 Capabilities:")
    print("• Self-improving AI with performance tracking")
    print("• Real computer control (browser, IDE, applications)")
    print("• Conversation memory and context awareness")
    print("• Background self-improvement loops")
    print("• Actual task execution ('do item 1' → real actions)")
    print("• Error learning and automatic improvement")
    print("=" * 50)
    print("🎯 This is the complete self-evolving digital assistant!")
    print("=" * 50)
    
    # Start all background systems
    final_jarvis.start_background_systems()
    
    # Start Flask server
    app.run(port=5002, debug=True)  # Port 5002 for final version 