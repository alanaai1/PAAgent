from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import os
import json
from datetime import datetime

# Google AI Studio imports
import google.generativeai as genai

# Import Google API functions
from calendar_assistant import (
    get_calendar_service,
    fetch_recent_emails,
    get_gmail_service
)

# Load environment variables
load_dotenv()

# Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Initialize Google AI Studio
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash')
    print("✅ Google AI Studio initialized successfully")
else:
    model = None
    print("❌ GEMINI_API_KEY not set. AI features will be disabled.")
    print("To enable AI, set GEMINI_API_KEY in your .env file")

app = Flask(__name__)
CORS(app)

def log_error(function_name, error, context=""):
    """Consistent error logging"""
    print(f"ERROR in {function_name}: {error}")
    if context:
        print(f"Context: {context}")

def _safe_float(value, default=0.0):
    """Safely convert value to float, handling string values"""
    try:
        if isinstance(value, str):
            # Handle common string values
            if value.lower() in ['unknown', 'none', 'null', '']:
                return default
            # Remove currency symbols and commas
            cleaned = value.replace('$', '').replace(',', '').replace('%', '')
            return float(cleaned) if cleaned.strip() else default
        return float(value) if value is not None else default
    except (ValueError, TypeError):
        return default

def analyze_with_ai(user_message, emails, events):
    """Analyze business data using AI and return structured results"""
    
    if not model:
        return _create_fallback_analysis()
    
    # Prepare data summaries
    email_summary = _summarize_emails(emails[:10]) if emails else "No recent emails"
    calendar_summary = _summarize_calendar(events[:10]) if events else "No upcoming events"
    
    # Create analysis prompt
    prompt = f"""
    Analyze this business data and provide specific insights with metrics and KPIs:
    
    EMAILS: {email_summary}
    CALENDAR: {calendar_summary}
    USER QUESTION: {user_message}
    
    Return JSON with enhanced business intelligence:
    {{
        "urgent_priorities": [
            {{
                "sender": "name", 
                "subject": "subject", 
                "content": "content", 
                "deadline": "date",
                "value": "estimated_revenue_impact",
                "priority_score": "1-10"
            }}
        ],
        "opportunities": [
            {{
                "company": "name", 
                "value": "amount", 
                "subject": "subject", 
                "content": "content",
                "probability": "win_probability_percentage",
                "timeline": "expected_close_date",
                "roi_estimate": "expected_return_on_investment"
            }}
        ],
        "business_metrics": {{
            "total_pipeline_value": "sum_of_all_opportunities",
            "avg_deal_size": "average_opportunity_value",
            "conversion_rate": "leads_to_opportunities_percentage",
            "response_time": "average_response_time_hours",
            "revenue_forecast": "projected_revenue_next_quarter"
        }},
        "action_items": [
            {{
                "task": "description",
                "priority": "high/medium/low",
                "deadline": "date",
                "assigned_to": "person",
                "value": "estimated_impact"
            }}
        ],
        "insights": [
            {{
                "type": "opportunity/risk/trend",
                "description": "detailed_insight",
                "impact": "high/medium/low",
                "recommendation": "specific_action"
            }}
        ]
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        content = response.text.strip()
        if content.startswith('```json'):
            content = content.replace('```json', '').replace('```', '').strip()
        
        return json.loads(content)
    except Exception as e:
        log_error("analyze_with_ai", f"AI analysis failed: {e}")
        return _create_fallback_analysis()

def _create_fallback_analysis():
    """Create fallback analysis when AI is unavailable"""
    return {
        "urgent_priorities": [],
        "opportunities": [],
        "business_metrics": {
            "total_pipeline_value": "0",
            "avg_deal_size": "0",
            "conversion_rate": "0%",
            "response_time": "0",
            "revenue_forecast": "0"
        },
        "action_items": [],
        "insights": []
    }

def _summarize_emails(emails):
    """Summarize email data for AI analysis"""
    if not emails:
        return "No emails found"
    
    summaries = []
    for email in emails[:5]:  # Limit to 5 emails
        sender = email.get('sender', 'Unknown')
        subject = email.get('subject', 'No subject')
        body = email.get('body', '')[:200]  # Truncate long emails
        summaries.append(f"From: {sender}, Subject: {subject}, Content: {body}")
    
    return " | ".join(summaries)

def _summarize_calendar(events):
    """Summarize calendar data for AI analysis"""
    if not events:
        return "No events found"
    
    summaries = []
    for event in events[:5]:  # Limit to 5 events
        summary = event.get('summary', 'No title')
        start = event.get('start', {}).get('dateTime', event.get('start', {}).get('date', 'No time'))
        summaries.append(f"Event: {summary}, Time: {start}")
    
    return " | ".join(summaries)

def generate_greeting(personality):
    """Generate personalized greeting based on personality"""
    greetings = {
        'professional': "Hello! I'm Jarvis, your business intelligence assistant.",
        'friendly': "Hey there! Jarvis here, ready to help with your business insights.",
        'direct': "Jarvis here. What do you need to know about your business data?"
    }
    return greetings.get(personality, greetings['professional'])

def generate_response(message, analysis, personality):
    """Generate intelligent response based on analysis"""
    greeting = generate_greeting(personality)
    
    # Extract key data
    urgent = analysis.get('urgent_priorities', [])
    opportunities = analysis.get('opportunities', [])
    metrics = analysis.get('business_metrics', {})
    action_items = analysis.get('action_items', [])
    insights = analysis.get('insights', [])
    
    # Determine response type
    if 'urgent' in message.lower() or urgent:
        return _generate_urgent_response(greeting, urgent, analysis.get('emails', []))
    elif 'email' in message.lower():
        return _generate_email_response(greeting, analysis.get('emails', []))
    elif 'meeting' in message.lower() or 'calendar' in message.lower():
        return _generate_meeting_response(greeting, analysis.get('events', []))
    elif 'opportunity' in message.lower() or opportunities:
        return _generate_opportunity_response(greeting, opportunities)
    elif 'action' in message.lower() or action_items:
        return _generate_action_response(greeting, message, urgent, opportunities, analysis.get('emails', []), analysis.get('events', []))
    else:
        return _generate_general_response(greeting, message, urgent, opportunities, metrics)

def _generate_urgent_response(greeting, urgent, emails):
    """Generate response for urgent priorities"""
    if not urgent:
        return f"{greeting} No urgent priorities detected in your recent data."
    
    response = f"{greeting} I've identified {len(urgent)} urgent priorities:\n\n"
    for i, item in enumerate(urgent[:3], 1):
        response += f"{i}. **{item.get('subject', 'Priority')}** from {item.get('sender', 'Unknown')}\n"
        response += f"   Priority Score: {item.get('priority_score', 'N/A')}/10\n"
        response += f"   Estimated Value: {item.get('value', 'N/A')}\n"
        response += f"   Deadline: {item.get('deadline', 'N/A')}\n\n"
    
    return response

def _generate_email_response(greeting, emails):
    """Generate response for email-related queries"""
    if not emails:
        return f"{greeting} No recent emails found to analyze."
    
    response = f"{greeting} Here's what I found in your recent emails:\n\n"
    for i, email in enumerate(emails[:3], 1):
        response += f"{i}. **{email.get('subject', 'No subject')}** from {email.get('sender', 'Unknown')}\n"
        response += f"   {email.get('body', 'No content')[:100]}...\n\n"
    
    return response

def _generate_meeting_response(greeting, meetings):
    """Generate response for meeting-related queries"""
    if not meetings:
        return f"{greeting} No upcoming meetings found."
    
    response = f"{greeting} Here are your upcoming meetings:\n\n"
    for i, meeting in enumerate(meetings[:3], 1):
        response += f"{i}. **{meeting.get('summary', 'No title')}**\n"
        response += f"   Time: {meeting.get('start', {}).get('dateTime', 'N/A')}\n\n"
    
    return response

def _generate_opportunity_response(greeting, opportunities):
    """Generate response for opportunity-related queries"""
    if not opportunities:
        return f"{greeting} No opportunities detected in your recent data."
    
    response = f"{greeting} I've identified {len(opportunities)} opportunities:\n\n"
    for i, opp in enumerate(opportunities[:3], 1):
        response += f"{i}. **{opp.get('company', 'Unknown')}** - {opp.get('subject', 'Opportunity')}\n"
        response += f"   Value: {opp.get('value', 'N/A')}\n"
        response += f"   Probability: {opp.get('probability', 'N/A')}%\n"
        response += f"   Timeline: {opp.get('timeline', 'N/A')}\n\n"
    
    return response

def _generate_general_response(greeting, message, urgent, opportunities, metrics):
    """Generate general response"""
    response = f"{greeting} Here's your business overview:\n\n"
    
    if urgent:
        response += f"🚨 **{len(urgent)} urgent priorities** need attention\n"
    
    if opportunities:
        response += f"💰 **{len(opportunities)} opportunities** identified\n"
    
    response += f"📊 **Pipeline Value**: {metrics.get('total_pipeline_value', 'N/A')}\n"
    response += f"📈 **Avg Deal Size**: {metrics.get('avg_deal_size', 'N/A')}\n"
    response += f"⚡ **Response Time**: {metrics.get('response_time', 'N/A')} hours\n"
    
    return response

def _generate_action_response(greeting, message, urgent, opportunities, emails, meetings):
    """Generate response with action items"""
    response = f"{greeting} Here are your recommended actions:\n\n"
    
    if urgent:
        response += "🚨 **URGENT ACTIONS:**\n"
        for item in urgent[:2]:
            response += f"• Address {item.get('subject', 'priority')} from {item.get('sender', 'Unknown')}\n"
        response += "\n"
    
    if opportunities:
        response += "💰 **OPPORTUNITY ACTIONS:**\n"
        for opp in opportunities[:2]:
            response += f"• Follow up with {opp.get('company', 'Unknown')} about {opp.get('subject', 'opportunity')}\n"
        response += "\n"
    
    response += "📅 **SCHEDULED ACTIONS:**\n"
    response += "• Review and prioritize your inbox\n"
    response += "• Update your pipeline tracking\n"
    response += "• Schedule follow-up calls\n"
    
    return response

def add_action_items(response):
    """Add action items to response"""
    action_items = [
        "📧 Review and respond to urgent emails",
        "📅 Prepare for upcoming meetings",
        "💰 Follow up on high-value opportunities",
        "📊 Update your pipeline tracking",
        "⏰ Schedule important follow-ups"
    ]
    
    response += "\n\n**Recommended Actions:**\n"
    for item in action_items[:3]:
        response += f"• {item}\n"
    
    return response

def _detect_query_type(message):
    """Detect the type of query from user message"""
    message_lower = message.lower()
    
    if any(word in message_lower for word in ['urgent', 'priority', 'critical']):
        return 'urgent'
    elif any(word in message_lower for word in ['email', 'inbox', 'mail']):
        return 'email'
    elif any(word in message_lower for word in ['meeting', 'calendar', 'schedule']):
        return 'meeting'
    elif any(word in message_lower for word in ['opportunity', 'deal', 'pipeline']):
        return 'opportunity'
    elif any(word in message_lower for word in ['action', 'task', 'todo']):
        return 'action'
    else:
        return 'general'

def _generate_intelligent_response(message, emails, events, personality):
    """Generate truly intelligent response using AI with smart detection"""
    
    if not model:
        return f"Hello! I'm Jarvis. AI features are currently disabled. Please check your configuration."
    
    try:
        # Prepare data for AI
        email_data = []
        for email in emails[:5]:  # Limit to 5 emails
            email_data.append({
                "sender": email.get('sender', 'Unknown'),
                "subject": email.get('subject', 'No subject'),
                "body": email.get('body', '')[:200]  # Truncate long emails
            })
        
        calendar_data = []
        for event in events[:5]:  # Limit to 5 events
            calendar_data.append({
                "summary": event.get('summary', 'No title'),
                "start": event.get('start', {}).get('dateTime', event.get('start', {}).get('date', 'No time')),
                "description": event.get('description', 'No description')
            })
        
        greeting = generate_greeting(personality)
        
        try:
        
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
        
        try:
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            log_error("_generate_intelligent_response", f"AI call failed: {e}")
            return f"{greeting} I'm having trouble analyzing your data right now. Please try again in a moment."
    except Exception as e:
        log_error("_generate_intelligent_response", f"Response generation failed: {e}")
        return f"{greeting} I'm having trouble right now. Please try again."

@app.route('/', methods=['GET'])
def health_check():
    """Quick health check endpoint"""
    return jsonify({
        "status": "healthy",
        "ai_enabled": model is not None,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/jarvis/test', methods=['GET'])
def jarvis_test():
    """Test endpoint for Jarvis functionality"""
    return jsonify({
        "message": "Jarvis is online and ready!",
        "ai_status": "enabled" if model else "disabled",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/jarvis/chat', methods=['POST'])
def jarvis_chat():
    """Main chat endpoint for Jarvis"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        message = data.get('message', '')
        personality = data.get('personality', 'professional')
        
        if not message:
            return jsonify({"error": "No message provided"}), 400
        
        # Get Google services
        calendar_service = get_calendar_service()
        gmail_service = get_gmail_service()
        
        # Fetch data
        emails = fetch_recent_emails(gmail_service) if gmail_service else []
        events = []
        
        if calendar_service:
            try:
                now = datetime.now(datetime.UTC).isoformat() + 'Z'
                events_result = calendar_service.events().list(
                    calendarId='primary',
                    timeMin=now,
                    maxResults=10,
                    singleEvents=True,
                    orderBy='startTime'
                ).execute()
                events = events_result.get('items', [])
            except Exception as e:
                log_error("jarvis_chat", f"Calendar fetch failed: {e}")
        
        # Generate response
        response = _generate_intelligent_response(message, emails, events, personality)
        
        return jsonify({
            "response": response,
            "timestamp": datetime.now().isoformat(),
            "data_sources": {
                "emails_analyzed": len(emails),
                "events_analyzed": len(events)
            }
        })
        
    except Exception as e:
        log_error("jarvis_chat", f"Chat endpoint failed: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
