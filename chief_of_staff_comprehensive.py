#!/usr/bin/env python3
import os
from agents import Agent, Runner, function_tool
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import pickle

# Google auth
def get_google_creds():
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            return pickle.load(token)
    return None

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
    
    # 1. Calendar Analysis
    from datetime import timezone
    import pytz
    uk_tz = pytz.timezone('Europe/London')
    now = datetime.now(uk_tz).isoformat()
    events_result = calendar_service.events().list(
        calendarId="primary",
        timeMin=now,
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
    
    # 3. Google Drive Analysis - ALL DOCUMENTS
    drive_summary = "\nGOOGLE DRIVE DOCUMENTS:\n"
    
    # Get ALL types of documents
    results = drive_service.files().list(
        pageSize=30,
        fields="files(id, name, mimeType, modifiedTime, webViewLink)",
        orderBy="modifiedTime desc",
        q="trashed=false"
    ).execute()
    files = results.get("files", [])
    
    drive_summary += f"Found {len(files)} recent files:\n"
    
    # Analyze different types
    docs = [f for f in files if "document" in f.get("mimeType", "")]
    sheets = [f for f in files if "spreadsheet" in f.get("mimeType", "")]
    presentations = [f for f in files if "presentation" in f.get("mimeType", "")]
    folders = [f for f in files if "folder" in f.get("mimeType", "")]
    
    drive_summary += f"- {len(docs)} Google Docs\n"
    drive_summary += f"- {len(sheets)} Google Sheets\n"
    drive_summary += f"- {len(presentations)} Presentations\n"
    drive_summary += f"- {len(folders)} Folders\n\n"
    
    # List recent documents
    drive_summary += "Recent documents:\n"
    for file in files[:15]:
        drive_summary += f"- {file['name']} (modified {file['modifiedTime'][:10]})\n"
    
    # Try to read content from recent docs
    content_preview = "\nDOCUMENT CONTENT PREVIEWS:\n"
    for doc in docs[:3]:  # First 3 Google Docs
        try:
            # Export as plain text
            result = drive_service.files().export(
                fileId=doc["id"],
                mimeType="text/plain"
            ).execute()
            content = result.decode("utf-8")[:500]  # First 500 chars
            content_preview += f"\n📄 {doc['name']}:\n{content}...\n"
        except:
            content_preview += f"\n📄 {doc['name']}: (couldn't read content)\n"
    
    return calendar_summary + email_summary + drive_summary + content_preview

# Create the Chief of Staff agent
chief = Agent(
    name="AI Chief of Staff",
    model="o4-mini",
    instructions="""You are an elite AI Chief of Staff. You have access to:
    1. Calendar events
    2. Emails (important and unread)
    3. ALL Google Drive documents (Docs, Sheets, Presentations)
    4. Document content
    
    Analyze everything and provide strategic insights. Look for:
    - Urgent items needing attention
    - Patterns across documents and communications
    - Upcoming critical meetings and their context
    - Documents that relate to upcoming events
    - Action items hidden in docs or emails
    
    Be specific, reference actual documents and meetings, and provide actionable recommendations.""",
    tools=[analyze_everything]
)

# Run it
result = Runner.run_sync(
    chief,
    "Analyze ALL my data - calendar, emails, and especially my Google Drive documents. What should I focus on?"
)

print("\n🤖 Chief of Staff Analysis:")
print("=" * 50)
# Get the actual response from the result
if hasattr(result, 'response'):
    print(result.response.content)
elif hasattr(result, 'output'):
    print(result.output)
else:
    # Debug what we actually have
    print(f"Result type: {type(result)}")
    print(f"Result attributes: {dir(result)}")
    print(f"Result content: {result}")
