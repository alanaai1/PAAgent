#!/usr/bin/env python3
import os
from agents import Agent, Runner, function_tool
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta, timezone
import pickle
import pytz
import base64
from email.mime.text import MIMEText

# Get Google credentials
def get_google_creds():
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            return pickle.load(token)
    return None

# EXISTING FUNCTION - Enhanced
@function_tool
def analyze_everything():
    """Analyze calendar, emails, AND all Google Drive documents"""
    creds = get_google_creds()
    if not creds:
        return "No Google access - run your api_server.py first to authenticate"
    
    # Initialize all services
    calendar_service = build("calendar", "v3", credentials=creds)
    gmail_service = build("gmail", "v1", credentials=creds)
    drive_service = build("drive", "v3", credentials=creds)
    
    # UK timezone
    uk_tz = pytz.timezone('Europe/London')
    now = datetime.now(uk_tz)
    
    # 1. Calendar Analysis
    events_result = calendar_service.events().list(
        calendarId="primary",
        timeMin=now.isoformat(),
        maxResults=20,
        singleEvents=True,
        orderBy="startTime"
    ).execute()
    events = events_result.get("items", [])
    
    calendar_summary = f"CALENDAR ({len(events)} upcoming events):\n"
    for event in events[:10]:
        start = event["start"].get("dateTime", event["start"].get("date"))
        calendar_summary += f"- {event.get('summary', 'No title')} at {start}\n"
    
    # 2. Email Analysis
    results = gmail_service.users().messages().list(
        userId="me",
        q="is:unread OR is:important",
        maxResults=20
    ).execute()
    messages = results.get("messages", [])
    
    email_summary = f"\nEMAILS ({len(messages)} important/unread):\n"
    for msg in messages[:10]:
        try:
            message = gmail_service.users().messages().get(userId="me", id=msg["id"]).execute()
            headers = message["payload"].get("headers", [])
            subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
            sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown")
            email_summary += f"- From {sender}: {subject}\n"
        except:
            pass
    
    # 3. Google Drive Analysis
    drive_summary = "\nGOOGLE DRIVE DOCUMENTS:\n"
    results = drive_service.files().list(
        pageSize=30,
        fields="files(id, name, mimeType, modifiedTime, webViewLink)",
        orderBy="modifiedTime desc",
        q="trashed=false"
    ).execute()
    files = results.get("files", [])
    
    docs = [f for f in files if "document" in f.get("mimeType", "")]
    sheets = [f for f in files if "spreadsheet" in f.get("mimeType", "")]
    
    drive_summary += f"- {len(docs)} Google Docs\n"
    drive_summary += f"- {len(sheets)} Google Sheets\n"
    
    # List recent documents
    for file in files[:10]:
        drive_summary += f"- {file['name']} (modified {file['modifiedTime'][:10]})\n"
    
    return calendar_summary + email_summary + drive_summary

# NEW FUNCTION - Draft emails
@function_tool
def draft_email(to_email: str, subject: str, context: str):
    """Draft an email based on context and save to Gmail drafts"""
    creds = get_google_creds()
    if not creds:
        return "No Google access"
    
    gmail_service = build("gmail", "v1", credentials=creds)
    
    # Use GPT to write the email
    from openai import OpenAI
    client = OpenAI()
    
    prompt = f"""Write a professional email:
To: {to_email}
Subject: {subject}
Context: {context}

Write a clear, concise email. Be professional but friendly."""
    
    response = client.chat.completions.create(
        model="o4-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    
    email_body = response.choices[0].message.content
    
    # Create draft in Gmail
    message = MIMEText(email_body)
    message['to'] = to_email
    message['subject'] = subject
    
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    
    try:
        draft = gmail_service.users().drafts().create(
            userId='me',
            body={'message': {'raw': raw}}
        ).execute()
        
        return f"✅ Draft created! Email to {to_email} about '{subject}'. Check your Gmail drafts. Content:\n\n{email_body}"
    except Exception as e:
        return f"Error creating draft: {e}"

# NEW FUNCTION - Create calendar blocks
@function_tool
def create_calendar_block(title: str, duration_minutes: int, date_str: str = "tomorrow"):
    """Block time on calendar for focused work"""
    creds = get_google_creds()
    if not creds:
        return "No Google access"
    
    calendar_service = build("calendar", "v3", credentials=creds)
    
    # Parse date
    uk_tz = pytz.timezone('Europe/London')
    if date_str == "tomorrow":
        start_date = datetime.now(uk_tz) + timedelta(days=1)
        start_date = start_date.replace(hour=9, minute=0)  # Default 9 AM
    else:
        # Parse the date string
        start_date = datetime.now(uk_tz).replace(hour=9, minute=0)
    
    end_date = start_date + timedelta(minutes=duration_minutes)
    
    event = {
        'summary': title,
        'description': f'Time blocked by AI Chief of Staff for: {title}',
        'start': {
            'dateTime': start_date.isoformat(),
            'timeZone': 'Europe/London',
        },
        'end': {
            'dateTime': end_date.isoformat(),
            'timeZone': 'Europe/London',
        },
        'reminders': {
            'useDefault': True,
        },
    }
    
    try:
        event = calendar_service.events().insert(calendarId='primary', body=event).execute()
        return f"✅ Calendar block created: '{title}' for {duration_minutes} minutes on {start_date.strftime('%Y-%m-%d at %H:%M')}"
    except Exception as e:
        return f"Error creating calendar block: {e}"

# Create the enhanced Chief of Staff agent
chief = Agent(
    name="AI Chief of Staff Pro",
    model="o4-mini",
    instructions="""You are an elite AI Chief of Staff with ACTION capabilities. You can:
    
    1. ANALYZE: Review calendar, emails, and documents
    2. DRAFT: Create email drafts in Gmail
    3. SCHEDULE: Block time on calendar for important work
    
    Your approach:
    - First analyze everything to understand the situation
    - Then take specific actions to help
    - Be proactive - don't just advise, DO things
    
    Example workflow:
    - See an important meeting → Block prep time before it
    - Notice an unanswered email → Draft a response
    - Find a deadline → Create calendar reminder
    
    Always explain what actions you're taking and why.""",
    tools=[analyze_everything, draft_email, create_calendar_block]
)

# Run it
result = Runner.run_sync(
    chief,
    """Analyze my schedule and emails. Then:
    1. Draft a response to any important emails
    2. Block prep time for any critical meetings
    3. Tell me what else needs attention"""
)

print("\n🤖 Enhanced Chief of Staff Actions:")
print("=" * 50)
print(result.final_output)
