#!/usr/bin/env python3
"""
Enhanced API server using Vertex AI Claude with Gmail and Calendar integration
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import os
from vertex_claude_gcloud import VertexAIClaudeGCloud
from datetime import datetime
import json

# Import Google API functions
from calendar_assistant import (
    get_calendar_service,
    fetch_recent_emails,
    get_gmail_service
)

# Load environment variables
load_dotenv()

# Initialize Vertex AI client
PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT_ID', 'aai-mobileapp')
REGION = os.getenv('VERTEX_AI_REGION', 'us-east5')

client = VertexAIClaudeGCloud(project_id=PROJECT_ID, region=REGION)

app = Flask(__name__)
CORS(app)

def log_error(function_name, error, context=""):
    """Consistent error logging"""
    print(f"ERROR in {function_name}: {error}")
    if context:
        print(f"Context: {context}")

def generate_greeting(personality):
    """Generate greeting based on personality"""
    formality = personality.get('formality', 50)
    
    if formality > 60:
        return "Good evening. How may I assist you?"
    elif formality > 30:
        return "Evening! What can I help with?"
    else:
        return "Hey! What's up?"

def _generate_intelligent_response(message, emails, events, personality):
    """Generate intelligent response using Vertex AI with real data"""
    try:
        greeting = generate_greeting(personality)
        
        # Prepare data for analysis
        email_data = []
        calendar_data = []
        
        if emails:
            email_data = [
                {
                    'sender': email.get('sender', 'Unknown'),
                    'subject': email.get('subject', 'No subject'),
                    'snippet': email.get('snippet', '')[:200],
                    'date': email.get('date', 'Unknown')
                }
                for email in emails[:10]  # Limit to 10 emails
            ]
        
        if events:
            calendar_data = [
                {
                    'title': event.get('summary', 'No title'),
                    'start': event.get('start', {}).get('dateTime', 'No time'),
                    'attendees': [att.get('email', '') for att in event.get('attendees', [])],
                    'description': event.get('description', '')
                }
                for event in events[:10]  # Limit to 10 events
            ]
        
        # Create comprehensive prompt
        prompt = f"""
        You are Jarvis, an intelligent business assistant. The user has asked: "{message}"
        
        Here are their recent emails:
        {json.dumps(email_data, indent=2)}
        
        Here are their upcoming calendar events:
        {json.dumps(calendar_data, indent=2)}
        
        Provide a comprehensive, intelligent response that:
        1. Addresses the user's specific question
        2. Analyzes the email and calendar data intelligently
        3. Provides actionable insights and recommendations
        4. If asked for drafts or summaries, provide actual draft emails and summaries
        5. Be conversational, helpful, and business-focused
        6. Use the greeting: "{greeting}"
        
        Respond in a natural, conversational way as Jarvis would.
        """
        
        response = client.create_message(
            model="claude-3-7-sonnet",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.7
        )
        
        return response.strip()
        
    except Exception as e:
        log_error("_generate_intelligent_response", f"Vertex AI call failed: {e}")
        return f"{greeting} I'm having trouble analyzing your data right now. Please try again in a moment."

@app.route('/', methods=['GET'])
def health_check():
    """Quick health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Jarvis API (Vertex AI + Gmail/Calendar)',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/jarvis/test', methods=['GET'])
def jarvis_test():
    """Quick test endpoint"""
    return jsonify({
        'message': 'Jarvis is working with Vertex AI, Gmail, and Calendar!',
        'status': 'success',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/jarvis/chat', methods=['POST'])
def jarvis_chat():
    """Main Jarvis chat endpoint with Gmail and Calendar integration"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        print(f"JARVIS: {message}")
        
        # Get real data from Gmail and Calendar
        emails = []
        events = []
        
        try:
            # Get Gmail data
            gmail_service = get_gmail_service()
            if gmail_service:
                print("✅ Gmail service connected")
                emails = fetch_recent_emails(gmail_service, hours=72)
                print(f"📧 Found {len(emails)} recent emails")
            else:
                print("❌ Gmail service not available")
        except Exception as e:
            print(f"❌ Gmail fetch failed: {e}")
        
        try:
            # Get Calendar data
            calendar_service = get_calendar_service()
            if calendar_service:
                print("✅ Calendar service connected")
                from datetime import timezone
                now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
                events = calendar_service.events().list(
                    calendarId='primary',
                    timeMin=now,
                    maxResults=10,
                    singleEvents=True,
                    orderBy='startTime'
                ).execute().get('items', [])
                print(f"📅 Found {len(events)} upcoming events")
            else:
                print("❌ Calendar service not available")
        except Exception as e:
            print(f"❌ Calendar fetch failed: {e}")
        
        # Generate intelligent response
        personality = {
            'formality': 40,
            'humor': 25,
            'extraversion': 30
        }
        
        response_text = _generate_intelligent_response(message, emails, events, personality)
        
        return jsonify({
            'message': response_text,
            'timestamp': datetime.now().isoformat(),
            'type': 'response',
            'data_summary': {
                'emails_found': len(emails),
                'events_found': len(events)
            }
        })
        
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({
            'message': f"Sorry, I'm having trouble right now. Error: {str(e)}",
            'timestamp': datetime.now().isoformat(),
            'type': 'error'
        }), 500

if __name__ == '__main__':
    print("Starting Enhanced Jarvis API server with Vertex AI + Gmail/Calendar...")
    app.run(debug=True, port=5000) 