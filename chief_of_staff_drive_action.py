#!/usr/bin/env python3
import os
from agents import Agent, Runner, function_tool
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload
import pickle
from datetime import datetime
import pytz

def get_google_creds():
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            return pickle.load(token)
    return None

@function_tool
def create_meeting_prep():
    """Create meeting prep using Drive (no Docs API needed)"""
    creds = get_google_creds()
    if not creds:
        return "ERROR: No credentials"
    
    try:
        calendar = build("calendar", "v3", credentials=creds)
        gmail = build("gmail", "v1", credentials=creds)
        drive = build("drive", "v3", credentials=creds)
        
        uk_tz = pytz.timezone('Europe/London')
        now = datetime.now(uk_tz)
        
        # Get next meeting
        events = calendar.events().list(
            calendarId="primary",
            timeMin=now.isoformat(),
            maxResults=1,
            singleEvents=True,
            orderBy="startTime"
        ).execute()
        
        meetings = events.get("items", [])
        if not meetings:
            return "No upcoming meetings"
        
        meeting = meetings[0]
        title = meeting.get("summary", "Meeting")
        time = meeting.get("start", {}).get("dateTime", "")
        
        # Create content
        content = f"""MEETING PREP: {title}
        
Time: {time}
Prepared: {now.strftime('%Y-%m-%d %H:%M')}

AGENDA ITEMS:
1. [Add your agenda items here]
2. 
3. 

KEY TALKING POINTS:
- 
- 
- 

ACTION ITEMS TO DISCUSS:
- 
- 

QUESTIONS TO ASK:
- 
- 

FOLLOW-UP REQUIRED:
- 
"""
        
        # Search for related emails
        search = title.split()[0] if title else "meeting"
        emails = gmail.users().messages().list(
            userId="me",
            q=f'"{search}" newer_than:3d',
            maxResults=3
        ).execute()
        
        if emails.get('messages'):
            content += f"\nRELATED EMAILS FOUND: {len(emails['messages'])}\n"
            for msg in emails['messages']:
                try:
                    message = gmail.users().messages().get(
                        userId='me',
                        id=msg['id'],
                        format='metadata',
                        metadataHeaders=['Subject', 'From']
                    ).execute()
                    headers = message['payload']['headers']
                    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
                    sender = next((h['value'] for h in headers if h['name'] == 'From'), '')
                    content += f"• From {sender}: {subject}\n"
                except:
                    pass
        
        # Create file in Drive
        file_metadata = {
            'name': f'{title} - Prep Notes.txt',
            'mimeType': 'text/plain'
        }
        
        media = MediaInMemoryUpload(
            content.encode('utf-8'),
            mimetype='text/plain'
        )
        
        file = drive.files().create(
            body=file_metadata,
            media_body=media,
            fields='id,webViewLink'
        ).execute()
        
        return f"""✅ CREATED MEETING PREP:

Meeting: {title}
Time: {time}
Document: {file.get('webViewLink')}

The prep document includes:
- Meeting details
- {len(emails.get('messages', []))} related emails found
- Template sections for agenda, talking points, and actions

Click the link to open and edit your prep notes!"""
        
    except Exception as e:
        return f"ERROR: {str(e)}"

chief = Agent(
    name="Drive Chief of Staff",
    model="o4-mini",
    instructions="Create meeting prep documents using Google Drive.",
    tools=[create_meeting_prep]
)

result = Runner.run_sync(chief, "Create prep for my next meeting")

print("\n📄 Meeting Prep Created:")
print("=" * 50)
print(result.final_output)
