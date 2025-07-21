from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import os
import openai
import json
from datetime import datetime

# Import Google API functions
from calendar_assistant import (
    get_calendar_service,
    fetch_recent_emails,
    get_gmail_service
)

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = openai.OpenAI(api_key=OPENAI_API_KEY)

app = Flask(__name__)
CORS(app)

def log_error(function_name, error, context=""):
    """Consistent error logging"""
    print(f"ERROR in {function_name}: {error}")
    if context:
        print(f"Context: {context}")

def analyze_with_ai(user_message, emails, events):
    """Analyze business data using AI and return structured results"""
    
    # Prepare data summaries
    email_summary = _summarize_emails(emails[:10]) if emails else "No recent emails"
    calendar_summary = _summarize_calendar(events[:10]) if events else "No upcoming events"
    
    # Create analysis prompt
    prompt = f"""
    Analyze this business data and provide specific insights:
    
    EMAILS: {email_summary}
    CALENDAR: {calendar_summary}
    USER QUESTION: {user_message}
    
    Return JSON with:
    {{
        "urgent_priorities": [
            {{"sender": "name", "subject": "subject", "content": "content", "deadline": "date"}}
        ],
        "opportunities": [
            {{"company": "name", "value": "amount", "subject": "subject", "content": "content"}}
        ],
        "business_status": "brief status summary",
        "recommended_actions": [
            {{"action": "what to do", "reason": "why"}}
        ],
        "specific_emails": [
            {{"sender": "name", "subject": "subject", "content": "key content"}}
        ],
        "specific_meetings": [
            {{"title": "meeting", "attendees": ["email1"], "purpose": "purpose"}}
        ]
    }}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=2000
        )
        
        # Clean response content
        content = response.choices[0].message.content.strip()
        if content.startswith('```json'):
            content = content.replace('```json', '').replace('```', '').strip()
        
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            log_error("analyze_with_ai", f"JSON parsing failed: {e}", content[:200])
            return _create_fallback_analysis()
            
    except Exception as e:
        log_error("analyze_with_ai", f"API call failed: {e}")
        return _create_fallback_analysis()

def _create_fallback_analysis():
    """Create consistent fallback when AI analysis fails"""
    return {
        "urgent_priorities": [],
        "opportunities": [],
        "business_status": "Analysis unavailable",
        "recommended_actions": [],
        "specific_emails": [],
        "specific_meetings": []
    }

def _summarize_emails(emails):
    """Create email summary for AI analysis"""
    if not emails:
        return "No recent emails"
    
    summary = []
    for email in emails:
        sender = email.get('sender', 'Unknown')
        subject = email.get('subject', 'No subject')
        snippet = email.get('snippet', '')[:150]
        summary.append(f"From: {sender} | Subject: {subject} | Content: {snippet}")
    
    return "\n".join(summary)

def _summarize_calendar(events):
    """Create calendar summary for AI analysis"""
    if not events:
        return "No upcoming events"
    
    summary = []
    for event in events:
        title = event.get('summary', 'No title')
        start = event.get('start', {}).get('dateTime', 'No time')
        attendees = [att.get('email', '') for att in event.get('attendees', [])]
        summary.append(f"Meeting: {title} | Time: {start} | Attendees: {', '.join(attendees[:3])}")
    
    return "\n".join(summary)

def generate_greeting(personality):
    """Generate greeting based on personality"""
    formality = personality.get('formality', 50)
    
    if formality > 60:
        return "Good evening. How may I assist you?"
    elif formality > 30:
        return "Evening! What can I help with?"
    else:
        return "Hey! What's up?"

def generate_response(message, analysis, personality):
    """Generate response based on message type and analysis"""
    
    greeting = generate_greeting(personality)
    message_lower = message.lower()
    
    # Extract data from analysis
    urgent = analysis.get('urgent_priorities', [])
    opportunities = analysis.get('opportunities', [])
    status = analysis.get('business_status', 'Unknown')
    emails = analysis.get('specific_emails', [])
    meetings = analysis.get('specific_meetings', [])
    
    # Determine response type and generate content
    if any(word in message_lower for word in ['urgent', 'priority', 'important']):
        return _generate_urgent_response(greeting, urgent, emails)
    
    elif any(word in message_lower for word in ['email', 'draft', 'respond']):
        return _generate_email_response(greeting, emails)
    
    elif any(word in message_lower for word in ['meeting', 'calendar', 'schedule']):
        return _generate_meeting_response(greeting, meetings)
    
    elif any(word in message_lower for word in ['opportunity', 'strategic', 'business']):
        return _generate_opportunity_response(greeting, opportunities)
    
    else:
        return _generate_general_response(greeting, message, urgent, opportunities, status)

def _generate_urgent_response(greeting, urgent, emails):
    """Generate response for urgent priorities"""
    response = f"{greeting} Here are your urgent priorities:\n\n"
    
    if urgent:
        response += "**URGENT ITEMS:**\n"
        for i, item in enumerate(urgent[:5], 1):
            sender = item.get('sender', 'Unknown')
            subject = item.get('subject', 'No subject')
            content = item.get('content', '')[:100]
            deadline = item.get('deadline', '')
            
            response += f"{i}. **{sender}** - {subject}"
            if content:
                response += f" - {content}..."
            if deadline:
                response += f" (Due: {deadline})"
            response += "\n"
    else:
        response += "No urgent priorities detected.\n"
    
    response += f"\n**Analysis:** Based on {len(emails)} emails reviewed"
    return response

def _generate_email_response(greeting, emails):
    """Generate response for email-related queries"""
    response = f"{greeting} Here are your important emails:\n\n"
    
    if emails:
        response += "**RECENT EMAILS:**\n"
        for i, email in enumerate(emails[:5], 1):
            sender = email.get('sender', 'Unknown')
            subject = email.get('subject', 'No subject')
            content = email.get('content', '')[:100]
            
            response += f"{i}. **{sender}**: {subject}"
            if content:
                response += f" - {content}..."
            response += "\n"
    else:
        response += "No important emails found.\n"
    
    return response

def _generate_meeting_response(greeting, meetings):
    """Generate response for meeting-related queries"""
    response = f"{greeting} Here are your meetings:\n\n"
    
    if meetings:
        response += "**SCHEDULED MEETINGS:**\n"
        for meeting in meetings[:5]:
            title = meeting.get('title', 'No title')
            attendees = meeting.get('attendees', [])
            purpose = meeting.get('purpose', '')
            
            response += f"• **{title}**\n"
            if attendees:
                response += f"  Attendees: {', '.join(attendees[:3])}\n"
            if purpose:
                response += f"  Purpose: {purpose}\n"
            response += "\n"
    else:
        response += "No meetings scheduled.\n"
    
    return response

def _generate_opportunity_response(greeting, opportunities):
    """Generate response for opportunity-related queries"""
    response = f"{greeting} Here are your business opportunities:\n\n"
    
    if opportunities:
        response += "**OPPORTUNITIES:**\n"
        for i, opp in enumerate(opportunities[:5], 1):
            company = opp.get('company', 'Unknown')
            value = opp.get('value', '')
            content = opp.get('content', '')[:100]
            
            response += f"{i}. **{company}**"
            if value:
                response += f" - {value}"
            if content:
                response += f" - {content}..."
            response += "\n"
    else:
        response += "No opportunities identified.\n"
    
    return response

def _generate_general_response(greeting, message, urgent, opportunities, status):
    """Generate general response for other queries"""
    response = f"{greeting} I've analyzed your business data:\n\n"
    response += f"**Business Status:** {status}\n"
    response += f"**Urgent Items:** {len(urgent)}\n"
    response += f"**Opportunities:** {len(opportunities)}\n\n"
    response += f"Your question: '{message}'\n"
    response += "I've reviewed your emails and calendar to provide this summary."
    return response

@app.route('/api/jarvis/chat', methods=['POST'])
def jarvis_chat():
    """Main Jarvis chat endpoint"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        personality = data.get('personality', {})
        
        print(f"JARVIS: {message}")
        
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
            log_error("jarvis_chat", f"Failed to fetch data: {e}")
            events = []
            emails = []
        
        # Analyze with AI
        analysis = analyze_with_ai(message, emails, events)
        
        # Generate response
        response_text = generate_response(message, analysis, personality)
        
        return jsonify({
            'message': response_text,
            'type': 'response'
        })
        
    except Exception as e:
        log_error("jarvis_chat", f"Request failed: {e}")
        return jsonify({
            'message': "I'm having trouble right now. Please try again.",
            'type': 'error'
        })

if __name__ == '__main__':
    app.run(port=5000, debug=True) 