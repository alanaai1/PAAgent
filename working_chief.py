#!/usr/bin/env python3
import os
from agents import Agent, Runner, function_tool
import pickle

# Load credentials ONCE at module level
CREDS = None
if os.path.exists("token.pickle"):
    with open("token.pickle", "rb") as token:
        CREDS = pickle.load(token)

@function_tool
def analyze_situation():
    """Get real data from your Google services"""
    if not CREDS:
        return {"error": "No credentials found. Run api_server.py first to authenticate."}
    
    try:
        from googleapiclient.discovery import build
        from datetime import datetime
        import pytz
        
        # Build services with the loaded credentials
        calendar = build('calendar', 'v3', credentials=CREDS)
        gmail = build('gmail', 'v1', credentials=CREDS)
        drive = build('drive', 'v3', credentials=CREDS)
        
        uk_tz = pytz.timezone('Europe/London')
        now = datetime.now(uk_tz)
        
        # Get calendar
        events = calendar.events().list(
            calendarId='primary',
            timeMin=now.isoformat(),
            maxResults=5,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        output = "CURRENT SITUATION:\n\n"
        
        # Calendar summary
        items = events.get('items', [])
        output += f"📅 Next {len(items)} meetings:\n"
        for event in items:
            start = event['start'].get('dateTime', event['start'].get('date'))
            output += f"• {event.get('summary', 'No title')} - {start}\n"
        
        # Email summary
        messages = gmail.users().messages().list(
            userId='me',
            q='is:unread is:important',
            maxResults=5
        ).execute()
        
        output += f"\n📧 {len(messages.get('messages', []))} important unread emails\n"
        
        # Drive summary
        files = drive.files().list(
            pageSize=5,
            orderBy='modifiedTime desc',
            fields='files(name, modifiedTime)'
        ).execute()
        
        output += f"\n📄 Recently modified docs:\n"
        for file in files.get('files', []):
            output += f"• {file['name']}\n"
        
        return output
        
    except Exception as e:
        return f"Error accessing services: {str(e)}"

@function_tool
def take_action(action_plan: str):
    """Execute the planned action"""
    if not CREDS:
        return "Cannot take action without credentials"
    
    # This is where you'd implement actual actions
    # For now, just acknowledge the plan
    return f"Action acknowledged: {action_plan}"

# Create agent
chief = Agent(
    name="Working Chief of Staff",
    model="o4-mini",
    instructions="""You are a Chief of Staff that follows this process:
    
    1. OBSERVE: Use analyze_situation to see the current state
    2. ORIENT: Identify what needs attention based on the data
    3. DECIDE: Choose the highest-impact action
    4. ACT: Use take_action to execute
    
    Show your thinking at each step.""",
    tools=[analyze_situation, take_action]
)

# Run it
result = Runner.run_sync(
    chief,
    "Analyze my situation and tell me what to focus on."
)

print("\n🎯 Chief of Staff Analysis:")
print("=" * 50)
print(result.final_output)
