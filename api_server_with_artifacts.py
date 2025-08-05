#!/usr/bin/env python3
"""
Enhanced API Server with Artifact System Integration
Combines Vertex AI, Gmail, Calendar, and Artifact Management
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from datetime import datetime
import logging

# Import existing modules
from vertex_claude_gcloud import VertexAIClaudeGCloud
from calendar_assistant import get_calendar_events, send_email
from artifact_system import artifact_manager, analyze_emails, get_artifact_data, update_draft, send_draft, mark_email_complete

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize Vertex AI client
client = VertexAIClaudeGCloud()

# System prompt for the AI assistant
SYSTEM_PROMPT = """You are Jarvis, an intelligent AI assistant that helps manage emails, calendar, and tasks. You have access to:

1. Email Management: Analyze emails, create drafts, and track responses
2. Calendar Integration: Check and manage calendar events
3. Artifact System: Persistent storage for ongoing conversations and tasks

When users ask about emails, use the artifact system to:
- Analyze important emails
- Create draft responses
- Track which emails have been handled
- Provide real-time updates

Be helpful, concise, and proactive in managing their workflow."""

@app.route('/')
def home():
    return jsonify({
        'status': 'Jarvis AI Assistant is running',
        'features': ['email_management', 'calendar_integration', 'artifact_system', 'slack_integration'],
        'endpoints': {
            'chat': '/jarvis_chat',
            'analyze_emails': '/analyze_emails',
            'artifacts': '/api/artifacts',
            'calendar': '/calendar_events'
        }
    })

@app.route('/jarvis_chat', methods=['POST'])
def jarvis_chat():
    """Main chat endpoint with artifact system integration"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        slack_context = data.get('slack_context', {})
        
        # Check for email-related commands
        if any(keyword in user_message.lower() for keyword in ['email', 'emails', 'analyze', 'draft']):
            return handle_email_request(user_message, slack_context)
        
        # Check for calendar-related commands
        if any(keyword in user_message.lower() for keyword in ['calendar', 'schedule', 'meeting', 'event']):
            return handle_calendar_request(user_message, slack_context)
        
        # Default AI response
        return handle_general_chat(user_message, slack_context)
        
    except Exception as e:
        logger.error(f"Error in jarvis_chat: {e}")
        return jsonify({
            'response': "I'm having trouble processing your request right now. Please try again.",
            'error': str(e)
        }), 500

def handle_email_request(user_message, slack_context):
    """Handle email-related requests"""
    try:
        # Check if user wants to analyze emails
        if 'analyze' in user_message.lower() or 'check' in user_message.lower():
            # Use artifact system to analyze emails
            response_message = analyze_emails()
            
            # Get the latest artifact
            artifacts = list(artifact_manager.artifacts.keys())
            if artifacts:
                latest_artifact_id = artifacts[-1]
                artifact_data = get_artifact_data(latest_artifact_id)
                
                return jsonify({
                    'response': response_message,
                    'artifact_id': latest_artifact_id,
                    'artifact_data': artifact_data,
                    'type': 'email_analysis'
                })
        
        # Check if user wants to see existing artifacts
        elif 'show' in user_message.lower() or 'list' in user_message.lower():
            artifacts = []
            for artifact_id, artifact in artifact_manager.artifacts.items():
                summary = artifact_manager.get_artifact_summary(artifact_id)
                if summary:
                    artifacts.append(summary)
            
            if artifacts:
                return jsonify({
                    'response': f"I found {len(artifacts)} email artifacts. Here's what we have:",
                    'artifacts': artifacts,
                    'type': 'artifact_list'
                })
            else:
                return jsonify({
                    'response': "No email artifacts found. Would you like me to analyze your emails?",
                    'type': 'no_artifacts'
                })
        
        # Default email response
        else:
            return jsonify({
                'response': "I can help you with email management. Try saying 'analyze my emails' or 'show email artifacts'.",
                'type': 'email_help'
            })
            
    except Exception as e:
        logger.error(f"Error handling email request: {e}")
        return jsonify({
            'response': "I'm having trouble with email management right now. Please try again.",
            'error': str(e)
        }), 500

def handle_calendar_request(user_message, slack_context):
    """Handle calendar-related requests"""
    try:
        # Get calendar events
        events = get_calendar_events()
        
        if events:
            event_summary = f"I found {len(events)} upcoming events:\n"
            for event in events[:5]:  # Show first 5 events
                event_summary += f"• {event.get('summary', 'No title')} - {event.get('start', {}).get('dateTime', 'No time')}\n"
            
            return jsonify({
                'response': event_summary,
                'events': events,
                'type': 'calendar_events'
            })
        else:
            return jsonify({
                'response': "No upcoming calendar events found.",
                'type': 'no_events'
            })
            
    except Exception as e:
        logger.error(f"Error handling calendar request: {e}")
        return jsonify({
            'response': "I'm having trouble accessing your calendar right now.",
            'error': str(e)
        }), 500

def handle_general_chat(user_message, slack_context):
    """Handle general chat requests"""
    try:
        # Create context-aware prompt
        context = ""
        if slack_context:
            context = f"User context: {slack_context.get('channel', '')} - {slack_context.get('user', '')}"
        
        # Prepare messages for Claude
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"{context}\n\nUser: {user_message}"}
        ]
        
        # Get response from Vertex AI
        response = client.create_message(
            model="claude-3-7-sonnet",
            messages=messages,
            max_tokens=1024,
            temperature=0.3
        )
        
        return jsonify({
            'response': response.strip(),
            'type': 'general_chat'
        })
        
    except Exception as e:
        logger.error(f"Error in general chat: {e}")
        return jsonify({
            'response': "I'm having trouble processing your request right now. Please try again.",
            'error': str(e)
        }), 500

# Artifact system endpoints
@app.route('/api/artifacts/analyze-emails', methods=['POST'])
def analyze_emails_endpoint():
    """Analyze emails and create artifact"""
    try:
        response_message = analyze_emails()
        artifacts = list(artifact_manager.artifacts.keys())
        artifact_id = artifacts[-1] if artifacts else None
        
        return jsonify({
            'success': True,
            'message': response_message,
            'artifact_id': artifact_id
        })
    except Exception as e:
        logger.error(f"Error analyzing emails: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/artifacts/<artifact_id>', methods=['GET'])
def get_artifact_endpoint(artifact_id):
    """Get artifact data"""
    try:
        artifact_data = get_artifact_data(artifact_id)
        if artifact_data:
            return jsonify({
                'success': True,
                'artifact': artifact_data
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Artifact not found'
            }), 404
    except Exception as e:
        logger.error(f"Error getting artifact: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/artifacts/<artifact_id>/drafts/<draft_id>', methods=['PUT'])
def update_draft_endpoint(artifact_id, draft_id):
    """Update a draft"""
    try:
        data = request.get_json()
        content = data.get('content')
        
        if not content:
            return jsonify({
                'success': False,
                'error': 'Content is required'
            }), 400
        
        update_draft(artifact_id, draft_id, content)
        
        return jsonify({
            'success': True,
            'message': 'Draft updated successfully'
        })
    except Exception as e:
        logger.error(f"Error updating draft: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/artifacts/<artifact_id>/drafts/<draft_id>/send', methods=['POST'])
def send_draft_endpoint(artifact_id, draft_id):
    """Send a draft email"""
    try:
        success = send_draft(artifact_id, draft_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Email sent successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to send email'
            }), 500
    except Exception as e:
        logger.error(f"Error sending draft: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/artifacts/<artifact_id>/emails/<email_id>/complete', methods=['POST'])
def mark_email_complete_endpoint(artifact_id, email_id):
    """Mark an email as handled"""
    try:
        mark_email_complete(artifact_id, email_id)
        
        return jsonify({
            'success': True,
            'message': 'Email marked as handled'
        })
    except Exception as e:
        logger.error(f"Error marking email complete: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/artifacts', methods=['GET'])
def list_artifacts_endpoint():
    """List all artifacts"""
    try:
        artifacts = []
        for artifact_id, artifact in artifact_manager.artifacts.items():
            summary = artifact_manager.get_artifact_summary(artifact_id)
            if summary:
                artifacts.append(summary)
        
        return jsonify({
            'success': True,
            'artifacts': artifacts
        })
    except Exception as e:
        logger.error(f"Error listing artifacts: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/calendar_events', methods=['GET'])
def calendar_events_endpoint():
    """Get calendar events"""
    try:
        events = get_calendar_events()
        return jsonify({
            'success': True,
            'events': events
        })
    except Exception as e:
        logger.error(f"Error getting calendar events: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/send_email', methods=['POST'])
def send_email_endpoint():
    """Send an email"""
    try:
        data = request.get_json()
        to = data.get('to')
        subject = data.get('subject')
        body = data.get('body')
        
        if not all([to, subject, body]):
            return jsonify({
                'success': False,
                'error': 'to, subject, and body are required'
            }), 400
        
        success = send_email(to, subject, body)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Email sent successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to send email'
            }), 500
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("🚀 Starting Jarvis AI Assistant with Artifact System...")
    print("📧 Email Management: Available")
    print("📅 Calendar Integration: Available")
    print("💾 Artifact System: Available")
    print("🔗 Slack Integration: Available")
    print("🌐 API Server: http://localhost:5000")
    print("📊 Artifact API: http://localhost:5000/api/artifacts")
    
    app.run(debug=True, host='0.0.0.0', port=5000) 