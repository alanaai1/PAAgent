from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import os
from vertex_claude_gcloud import VertexAIClaudeGCloud
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
PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT_ID')
REGION = os.getenv('VERTEX_AI_REGION', 'us-east5')

# Initialize Vertex AI client with Claude Sonnet 4
client = VertexAIClaudeGCloud(project_id=PROJECT_ID, region=REGION)

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
        "business_status": "brief status summary with KPIs",
        "recommended_actions": [
            {{
                "action": "what to do", 
                "reason": "why",
                "timeline": "when_to_complete",
                "expected_impact": "revenue_or_efficiency_gain"
            }}
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
        response = client.create_message(
            model="claude-3-7-sonnet",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.3
        )
        
        # Clean response content
        content = response.strip()
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
        "business_metrics": {
            "total_pipeline_value": "0",
            "avg_deal_size": "0",
            "conversion_rate": "0%",
            "response_time": "24h",
            "revenue_forecast": "0"
        },
        "business_status": "Analysis unavailable - using fallback metrics",
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
    
    # Handle action requests - user wants Jarvis to DO something
    if any(phrase in message_lower for phrase in ['help me', 'can you', 'do it', 'take action', 'handle', 'deal with']):
        return _generate_action_response(greeting, message, urgent, opportunities, emails, meetings)
    
    # Handle specific requests
    elif any(word in message_lower for word in ['urgent', 'priority', 'important']):
        return _generate_urgent_response(greeting, urgent, emails)
    
    elif any(word in message_lower for word in ['email', 'draft', 'respond']):
        return _generate_email_response(greeting, emails)
    
    elif any(word in message_lower for word in ['meeting', 'calendar', 'schedule']):
        return _generate_meeting_response(greeting, meetings)
    
    elif any(word in message_lower for word in ['opportunity', 'strategic']):
        return _generate_opportunity_response(greeting, opportunities)
    
    # Handle conversational queries that expect actionable advice
    elif any(phrase in message_lower for phrase in ['what should i', 'what do i', 'rundown', 'summary', 'tell me what']):
        return _generate_general_response(greeting, message, urgent, opportunities, status)
    
    else:
        return _generate_conversational_response(greeting, message, urgent, opportunities, status)

def _generate_urgent_response(greeting, urgent, emails):
    """Generate actionable response for urgent priorities"""
    if not urgent:
        return f"{greeting} Good news! No urgent items need immediate attention. I've reviewed {len(emails)} emails and everything looks manageable."
    
    response = f"{greeting} I found {len(urgent)} urgent items that need action. Here's what I can do:\n\n"
    
    for i, item in enumerate(urgent[:3], 1):
        sender = item.get('sender', 'Unknown')
        subject = item.get('subject', 'No subject')
        content = item.get('content', '')
        
        response += f"**{i}. {sender} - {subject}**\n"
        
        # Provide specific actionable suggestions
        if 'github' in sender.lower() and 'sign in' in subject.lower():
            response += "🔐 **What I can do:** I can help verify if this login location matches your current IP, or guide you through securing your account.\n"
            response += "💡 **Next step:** Say 'help me secure GitHub' or 'check if this login is safe'\n\n"
            
        elif 'companies house' in content.lower() or 'verify' in content.lower():
            response += "📋 **What I can do:** I can walk you through the Companies House verification process step-by-step, or find the direct link.\n"
            response += "💡 **Next step:** Say 'help me verify Companies House' or 'show me the verification link'\n\n"
            
        elif 'invoice' in content.lower() or 'payment' in content.lower():
            response += "💰 **What I can do:** I can extract payment details, set up reminders, or draft a response confirming payment.\n"
            response += "💡 **Next step:** Say 'help me pay this invoice' or 'draft payment confirmation'\n\n"
            
        else:
            response += f"📧 **What I can do:** I can draft a response, schedule a follow-up, or break down what action is needed.\n"
            response += f"💡 **Next step:** Say 'help me respond to {sender}' or 'what should I do about this?'\n\n"
    
    response += "🚀 **Want me to handle multiple items?** Just say 'take action on all urgent items' and I'll guide you through each one."
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
    """Generate conversational response that offers specific help"""
    response = f"{greeting} I've analyzed everything and here's what's happening:\n\n"
    
    # Provide actionable summary
    if urgent:
        response += f"🚨 **{len(urgent)} urgent items** need your attention - I can help you tackle these right now.\n"
    else:
        response += "✅ **No urgent items** - everything is under control.\n"
        
    if opportunities:
        response += f"🚀 **{len(opportunities)} opportunities** identified - I can help you capitalize on these.\n"
    else:
        response += "📊 **Monitoring for opportunities** - I'll alert you when I spot them.\n"
    
    response += f"\n💼 **Business Status:** {status}\n\n"
    
    # Offer specific next actions based on the message
    if any(word in message.lower() for word in ['summary', 'rundown', 'overview']):
        response += "**Here's what I can do right now:**\n"
        if urgent:
            response += f"• Handle urgent items: Say 'deal with urgent items'\n"
        if opportunities:
            response += f"• Explore opportunities: Say 'show me opportunities'\n"
        response += "• Draft emails: Say 'draft my emails'\n"
        response += "• Check calendar: Say 'what meetings do I have'\n"
        response += "• Focus mode: Say 'what should I prioritize today'\n\n"
        response += "💡 **Just tell me what you want to focus on and I'll handle it.**"
    else:
        response += f"**Regarding '{message}'** - I can provide specific guidance or take action.\n\n"
        response += "💡 **What would you like me to do?** I can handle emails, schedule meetings, draft responses, or dive deeper into any area."
    
    return response

def _generate_action_response(greeting, message, urgent, opportunities, emails, meetings):
    """Generate response when user explicitly asks Jarvis to take action"""
    message_lower = message.lower()
    
    # GitHub security help
    if 'github' in message_lower and ('secure' in message_lower or 'safe' in message_lower):
        return f"{greeting} I'll help you secure your GitHub account:\n\n🔐 **Step 1:** Check if the login location matches your current IP\n📱 **Step 2:** Enable 2FA if not already active\n🚨 **Step 3:** Review recent activity for unauthorized access\n\n💡 **Want me to guide you through each step?** Just say 'yes, help me with GitHub security'"
    
    # Companies House verification
    elif 'companies house' in message_lower and 'verify' in message_lower:
        return f"{greeting} I'll help you verify with Companies House:\n\n📋 **Step 1:** Visit gov.uk/companies-house-identity-verification\n🆔 **Step 2:** Have your ID document ready (passport/driving license)\n📧 **Step 3:** Use the email address from your original registration\n\n💡 **Need the direct link or want me to walk through the process?** Just ask!"
    
    # Handle urgent items
    elif 'urgent' in message_lower or 'deal with' in message_lower:
        if not urgent:
            return f"{greeting} Great news! No urgent items need attention right now. Everything is under control.\n\n✅ **Current status:** All emails reviewed, no critical deadlines\n🎯 **Suggestion:** Focus on opportunities or strategic planning\n\n💡 **Want me to suggest productive tasks?** Just ask!"
        
        response = f"{greeting} Let's tackle these urgent items one by one:\n\n"
        for i, item in enumerate(urgent[:3], 1):
            sender = item.get('sender', 'Unknown')
            subject = item.get('subject', 'No subject')
            response += f"**{i}. {sender} - {subject}**\n"
            if 'github' in sender.lower():
                response += "   → I can guide you through GitHub security verification\n"
            elif 'companies house' in item.get('content', '').lower():
                response += "   → I can help you complete the identity verification\n"
            else:
                response += f"   → I can draft a response or provide next steps\n"
        
        response += f"\n💡 **Ready to start?** Say 'help me with item 1' or 'start with [specific task]'"
        return response
    
    # General action request
    else:
        response = f"{greeting} I'm ready to help! Here's what I can do right now:\n\n"
        if urgent:
            response += f"🚨 **Handle {len(urgent)} urgent items** - I'll guide you through each one\n"
        if opportunities:
            response += f"🚀 **Explore {len(opportunities)} opportunities** - I'll help you capitalize\n"
        if emails:
            response += f"📧 **Draft responses** for {len(emails)} important emails\n"
        if meetings:
            response += f"📅 **Prepare for {len(meetings)} meetings** - I'll create briefs\n"
        
        response += "\n💡 **What would you like to tackle first?** Just tell me and I'll take action!"
        return response

def add_action_items(response):
    """Add specific actionable steps with business metrics and KPIs"""
    action_items = [
        "📊 BUSINESS METRICS & KPIs:",
        "• Revenue Pipeline: $[X] (Target: $[Y])",
        "• Conversion Rate: [X]% (Industry Avg: [Y]%)",
        "• Customer Acquisition Cost: $[X] (Target: $[Y])",
        "• Lead Response Time: [X] hours (Target: <24h)",
        "",
        "⏰ SPECIFIC TIMELINES:",
        "1. [Action] - Complete by [Date] (Expected ROI: [X]%)",
        "2. [Action] - Follow up within [X] hours (Success metric: [Y])",
        "3. [Action] - Review results by [Date] (KPIs: [metrics])",
        "",
        "🎯 SUCCESS METRICS:",
        "• Revenue Impact: $[X] increase",
        "• Efficiency Gain: [X]% time saved",
        "• Customer Satisfaction: [X]% improvement"
    ]
    return response + "\n\n" + "\n".join(action_items)

def _detect_query_type(message):
    """Detect if the query is casual conversation or business-related"""
    message_lower = message.lower().strip()
    casual_keywords = [
        'how are you', 'how do you do', 'hello', 'hi', 'hey',
        'good morning', 'good afternoon', 'good evening',
        'thanks', 'thank you', 'appreciate it', 'cool', 'great',
        'nice', 'awesome', 'good job', 'well done'
    ]
    business_keywords = [
        'email', 'emails', 'mail', 'inbox', 'draft', 'reply', 'respond',
        'urgent', 'important', 'priority', 'meeting', 'calendar', 'schedule',
        'summary', 'summarize', 'summarise', 'analyze', 'analyse',
        'business', 'revenue', 'profit', 'deal', 'contract', 'proposal',
        'client', 'customer', 'work', 'task', 'action', 'deadline',
        'today', 'tomorrow', 'this week', 'next week'
    ]
    for keyword in casual_keywords:
        if keyword in message_lower:
            return 'casual'
    for keyword in business_keywords:
        if keyword in message_lower:
            return 'business'
    return 'business'

def _generate_intelligent_response(message, emails, events, personality):
    """Generate truly intelligent response using GPT with smart detection"""
    greeting = generate_greeting(personality)
    query_type = _detect_query_type(message)
    try:
        if query_type == 'casual':
            prompt = f"""
            You are Jarvis, an intelligent business assistant. The user has asked: \"{message}\"
            Respond in a natural, conversational way. Be friendly and helpful, but remember you're a business assistant.
            Use the greeting: \"{greeting}\"
            Keep it casual and conversational - no need to analyze emails or calendar for this type of question.
            """
        else:
            email_data = []
            for email in emails[:10]:
                email_data.append({
                    'sender': email.get('sender', 'Unknown'),
                    'subject': email.get('subject', 'No subject'),
                    'content': email.get('body', '') or email.get('snippet', ''),
                    'date': email.get('date', '')
                })
            calendar_data = []
            for event in events[:5]:
                calendar_data.append({
                    'title': event.get('summary', 'No title'),
                    'start': event.get('start', {}).get('dateTime', 'No time'),
                    'attendees': [a.get('email', '') for a in event.get('attendees', [])],
                    'description': event.get('description', '')
                })
            prompt = f"""
            You are Jarvis, an intelligent business assistant. The user has asked: \"{message}\"
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
            6. Use the greeting: \"{greeting}\"
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
        log_error("_generate_intelligent_response", f"GPT call failed: {e}")
        return f"{greeting} I'm having trouble analyzing your data right now. Please try again in a moment."

# All template functions removed - GPT handles all analysis and responses

@app.route('/', methods=['GET'])
def health_check():
    """Quick health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Jarvis API',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/jarvis/test', methods=['GET'])
def jarvis_test():
    """Quick test endpoint that responds immediately"""
    return jsonify({
        'message': 'Jarvis is working! This is a test response.',
        'status': 'success',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/jarvis/chat', methods=['POST'])
def jarvis_chat():
    """Main Jarvis chat endpoint - Now uses intelligent responses"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        slack_context = data.get('slack_context', {})
        
        # Log the request
        if slack_context:
            user_id = slack_context.get('user_id', 'Unknown')
            channel_id = slack_context.get('channel_id', 'Unknown')
            print(f"JARVIS (Slack - {user_id} in {channel_id}): {message}")
        else:
            print(f"JARVIS: {message}")
        
        # Use GPT for ALL responses - no templates
        try:
            # Get real data
            calendar_service = get_calendar_service()
            gmail_service = get_gmail_service()
            
            emails = []
            events = []
            
            if gmail_service:
                try:
                    emails = fetch_recent_emails(gmail_service, hours=72)
                except Exception as e:
                    print(f"Email fetch failed: {e}")
            
            if calendar_service:
                try:
                    from datetime import timezone
                    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
                    events = calendar_service.events().list(
                        calendarId='primary',
                        timeMin=now,
                        maxResults=10,
                        singleEvents=True,
                        orderBy='startTime'
                    ).execute().get('items', [])
                except Exception as e:
                    print(f"Calendar fetch failed: {e}")
            
            # Use GPT for intelligent response
            personality = {
                'formality': 40,
                'humor': 25,
                'extraversion': 30
            }
            
            # Generate intelligent response based on actual data
            response_text = _generate_intelligent_response(message, emails, events, personality)
            
        except Exception as e:
            print(f"Intelligent response failed: {e}")
            # Fallback to simple response without templates
            response_text = f"{generate_greeting({'formality': 40})} I'm having trouble analyzing your data right now. Please try again in a moment."
        
        return jsonify({
            'message': response_text,
            'type': 'response',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        log_error("jarvis_chat", f"Request failed: {e}")
        return jsonify({
            'message': "I'm having trouble right now. Please try again.",
            'type': 'error'
        })

if __name__ == '__main__':
    app.run(port=5000, debug=True)  # Changed to port 5000 