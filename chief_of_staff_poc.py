import os
from agents import Agent, Runner, function_tool
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import pickle

# Set your OpenAI key

# Google auth
def get_google_creds():
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            return pickle.load(token)
    return None

@function_tool
def analyze_calendar():
    """Get and analyze today's calendar events"""
    creds = get_google_creds()
    if not creds:
        return "No calendar access"
    
    service = build('calendar', 'v3', credentials=creds)
    now = datetime.utcnow().isoformat() + 'Z'
    
    events_result = service.events().list(
        calendarId='primary',
        timeMin=now,
        maxResults=10,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    events = events_result.get('items', [])
    summary = f"You have {len(events)} upcoming events:\n"
    for event in events[:5]:
        start = event['start'].get('dateTime', event['start'].get('date'))
        summary += f"- {event.get('summary', 'No title')} at {start}\n"
    
    return summary

@function_tool
def analyze_emails():
    """Get recent important emails"""
    creds = get_google_creds()
    if not creds:
        return "No email access"
        
    service = build('gmail', 'v1', credentials=creds)
    results = service.users().messages().list(
        userId='me',
        q='is:unread',
        maxResults=10
    ).execute()
    
    messages = results.get('messages', [])
    return f"You have {len(messages)} unread emails"

# Create the Chief of Staff agent
chief = Agent(
    name='AI Chief of Staff',
    model='o4-mini',
    instructions='''You are an AI Chief of Staff. Your job:
    1. Analyze calendar and emails
    2. Identify what needs immediate attention
    3. Provide specific, actionable recommendations
    4. Flag any conflicts or issues
    
    Be direct, specific, and focus on what matters most.''',
    tools=[analyze_calendar, analyze_emails]
)

# Run it
result = Runner.run_sync(
    chief,
    "What are my priorities today? Check my calendar and emails for anything urgent."
)

print("\n🤖 Chief of Staff Analysis:")
print("="*50)
print(result.messages[-1].content)
