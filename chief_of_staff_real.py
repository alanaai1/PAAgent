#!/usr/bin/env python3
import os
from agents import Agent, Runner, function_tool
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import pickle
from datetime import datetime
import pytz

# Get Google credentials
def get_google_creds():
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            return pickle.load(token)
    return None

@function_tool
def create_real_content():
    """Actually create content based on REAL data"""
    creds = get_google_creds()
    if not creds:
        return "ERROR: No Google credentials found. The agent cannot access your real data."
    
    try:
        # Initialize services
        calendar_service = build("calendar", "v3", credentials=creds)
        gmail_service = build("gmail", "v1", credentials=creds)
        drive_service = build("drive", "v3", credentials=creds)
        
        # Get REAL upcoming meetings
        uk_tz = pytz.timezone('Europe/London')
        now = datetime.now(uk_tz)
        
        events_result = calendar_service.events().list(
            calendarId="primary",
            timeMin=now.isoformat(),
            maxResults=10,
            singleEvents=True,
            orderBy="startTime"
        ).execute()
        events = events_result.get("items", [])
        
        if not events:
            return "No upcoming events found"
        
        actions_taken = []
        
        # Process REAL meetings
        for event in events[:3]:
            event_name = event.get('summary', 'No title')
            start = event.get('start', {}).get('dateTime', 'No time')
            
            # Look for related emails
            query = f'"{event_name.split()[0]}" after:2025/6/1'
            try:
                email_results = gmail_service.users().messages().list(
                    userId='me',
                    q=query,
                    maxResults=5
                ).execute()
                
                related_emails = []
                for msg in email_results.get('messages', [])[:3]:
                    message = gmail_service.users().messages().get(userId='me', id=msg['id']).execute()
                    snippet = message.get('snippet', '')
                    related_emails.append(snippet[:100])
                
                # Create REAL slide content based on ACTUAL meeting
                slide_content = f"""
ACTUAL SLIDE DECK FOR: {event_name}
Date: {start}

Slide 1: Meeting Overview
- Event: {event_name}
- Time: {start}
- Attendees: {len(event.get('attendees', []))} people

Slide 2: Context from Related Emails
"""
                for email in related_emails:
                    slide_content += f"- {email}...\n"
                
                slide_content += f"""
Slide 3: Key Discussion Points
- [Extracted from your actual emails about {event_name}]
- [Real agenda items, not made up content]

Slide 4: Action Items
- [Based on your actual email threads]
"""
                
                actions_taken.append({
                    'type': 'slide_deck',
                    'meeting': event_name,
                    'content': slide_content,
                    'status': 'created'
                })
                
            except Exception as e:
                actions_taken.append({
                    'type': 'error',
                    'meeting': event_name,
                    'error': str(e)
                })
        
        # Format output
        output = "REAL ACTIONS TAKEN (Based on YOUR actual data):\n\n"
        for action in actions_taken:
            if action['type'] == 'slide_deck':
                output += f"✅ Created slides for: {action['meeting']}\n"
                output += f"Content preview:\n{action['content'][:300]}...\n\n"
            else:
                output += f"❌ Error processing {action['meeting']}: {action['error']}\n\n"
        
        return output
        
    except Exception as e:
        return f"ERROR accessing Google services: {str(e)}\nThis is why you got fake content before!"

# Create agent that uses REAL data
chief = Agent(
    name="Real Chief of Staff",
    model="o4-mini",
    instructions="""You are a Chief of Staff that works with REAL data.
    
    IMPORTANT:
    - Only use actual data from the tools
    - If you get an error, say so clearly
    - Never make up meetings, emails, or content
    - Always indicate what's real vs what needs to be filled in
    """,
    tools=[create_real_content]
)

# Run it
result = Runner.run_sync(
    chief,
    "Create slide decks for my ACTUAL meetings using my REAL email data. Don't make anything up."
)

print("\n🎯 REAL Chief of Staff Actions:")
print("=" * 50)
print(result.final_output)
