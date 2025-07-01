#!/usr/bin/env python3
import os
from agents import Agent, Runner, function_tool
from googleapiclient.discovery import build
import pickle
from datetime import datetime
import pytz

def get_google_creds():
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            return pickle.load(token)
    return None

@function_tool
def analyze_and_act():
    """Analyze situation and take REAL action - not just talk about it"""
    creds = get_google_creds()
    if not creds:
        return "ERROR: No credentials to access your data"
    
    try:
        # Get services
        calendar = build("calendar", "v3", credentials=creds)
        gmail = build("gmail", "v1", credentials=creds)
        docs = build("docs", "v1", credentials=creds)
        
        uk_tz = pytz.timezone('Europe/London')
        now = datetime.now(uk_tz)
        
        # Get next 3 meetings
        events = calendar.events().list(
            calendarId="primary",
            timeMin=now.isoformat(),
            maxResults=3,
            singleEvents=True,
            orderBy="startTime"
        ).execute()
        
        next_meetings = events.get("items", [])
        if not next_meetings:
            return "No upcoming meetings found"
        
        # Focus on the FIRST important meeting
        target_meeting = next_meetings[0]
        meeting_title = target_meeting.get("summary", "Untitled Meeting")
        meeting_time = target_meeting.get("start", {}).get("dateTime", "")
        
        # Look for emails about this meeting
        search_term = meeting_title.split()[0] if meeting_title else "meeting"
        email_results = gmail.users().messages().list(
            userId="me",
            q=f'"{search_term}" newer_than:7d',
            maxResults=5
        ).execute()
        
        # Create ACTUAL prep document
        doc_title = f"{meeting_title} - Prep Document"
        doc = docs.documents().create(body={'title': doc_title}).execute()
        doc_id = doc['documentId']
        
        # Build real content
        content = f"{meeting_title}\n"
        content += f"Time: {meeting_time}\n"
        content += f"Prepared: {now.strftime('%Y-%m-%d %H:%M')}\n\n"
        content += "AGENDA & TALKING POINTS\n\n"
        
        # Add email context if found
        if email_results.get('messages'):
            content += "Context from recent emails:\n"
            for msg in email_results.get('messages', [])[:3]:
                try:
                    message = gmail.users().messages().get(
                        userId='me', 
                        id=msg['id'],
                        format='metadata',
                        metadataHeaders=['Subject']
                    ).execute()
                    headers = message.get('payload', {}).get('headers', [])
                    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
                    content += f"• {subject}\n"
                except:
                    pass
            content += "\n"
        
        content += "KEY DISCUSSION POINTS:\n"
        content += "1. \n2. \n3. \n\n"
        content += "ACTION ITEMS:\n"
        content += "• \n• \n\n"
        content += "FOLLOW-UP REQUIRED:\n"
        content += "• \n"
        
        # Actually insert the content
        requests = [{
            'insertText': {
                'location': {'index': 1},
                'text': content
            }
        }]
        
        docs.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': requests}
        ).execute()
        
        # Return what we ACTUALLY did
        return f"""ACTUAL ACTION TAKEN:

✅ Created prep document for: {meeting_title}
📅 Meeting time: {meeting_time}
📄 Document: https://docs.google.com/document/d/{doc_id}

The document includes:
- Meeting details
- Context from {len(email_results.get('messages', []))} related emails
- Template for agenda points
- Action items section

You can now open this document and fill in the specific points."""
        
    except Exception as e:
        return f"ERROR: {str(e)}"

# Simple agent that DOES things
chief = Agent(
    name="Action Chief of Staff",
    model="o4-mini",
    instructions="""You are a Chief of Staff that takes REAL actions.

    When you run analyze_and_act, it will:
    1. Find your next meeting
    2. Create an ACTUAL Google Doc prep document
    3. Return the real URL
    
    Just run the tool and report what actually happened.""",
    tools=[analyze_and_act]
)

result = Runner.run_sync(
    chief,
    "Create a prep document for my next important meeting."
)

print("\n✅ REAL Chief of Staff Action:")
print("=" * 50)
print(result.final_output)
