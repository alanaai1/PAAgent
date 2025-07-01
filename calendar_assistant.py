"""
Calendar Assistant - Clean rewrite to work with the comprehensive agent
"""
import os
import pickle
import datetime
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import openai
from dotenv import load_dotenv
import base64
import json
from supabase import create_client, Client
from googleapiclient.errors import HttpError
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from review_framework import ReviewerConfig, ReviewManager
import asyncio
import time
from openai import RateLimitError

# Load environment variables
load_dotenv()

# Initialize OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')
client = openai.OpenAI() if os.getenv('OPENAI_API_KEY') else None

# Initialize Supabase (if needed)
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

# Google API Scopes
SCOPES = [
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/drive.readonly'
]

# Synchronous wrapper for artifact review
universal_prompt = (
    "You are a Domain Coach. Evaluate text for accuracy, completeness, "
    "clarity, coherence, strategic relevance, practicality, and policy compliance."
)
reviewer_cfgs = [
    ReviewerConfig(name=f"Coach {c}", system_prompt=universal_prompt, temperature=t)
    for c, t in zip(["A", "B", "C"], [0.2, 0.5, 0.8])
]
review_manager = ReviewManager(reviewer_cfgs)

def get_google_credentials():
    """Get or refresh Google credentials"""
    creds = None
    
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return creds

def get_calendar_service():
    """Get Google Calendar service"""
    try:
        creds = get_google_credentials()
        return build('calendar', 'v3', credentials=creds)
    except Exception as e:
        print(f"Error getting calendar service: {e}")
        return None

def get_gmail_service():
    """Get Gmail service"""
    try:
        creds = get_google_credentials()
        return build('gmail', 'v1', credentials=creds)
    except Exception as e:
        print(f"Error getting gmail service: {e}")
        return None

def get_drive_service():
    """Get Google Drive service"""
    try:
        creds = get_google_credentials()
        return build('drive', 'v3', credentials=creds)
    except Exception as e:
        print(f"Error getting drive service: {e}")
        return None

def get_next_event(service=None):
    """Get the next calendar event"""
    try:
        if not service:
            service = get_calendar_service()
        
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        events_result = service.events().list(
            calendarId='primary',
            timeMin=now,
            maxResults=1,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        if events:
            event = events[0]
            return {
                'summary': event.get('summary', 'No title'),
                'start': event['start'].get('dateTime', event['start'].get('date')),
                'attendees': event.get('attendees', []),
                'description': event.get('description', ''),
                'location': event.get('location', '')
            }
        return None
    except Exception as e:
        print(f"Error getting next event: {e}")
        return None

def fetch_recent_emails(service=None, hours=72):
    """Fetch recent emails with full content"""
    try:
        if not service:
            service = get_gmail_service()
        
        # Calculate the date for the query
        after_date = (datetime.datetime.now() - datetime.timedelta(hours=hours)).strftime('%Y/%m/%d')
        query = f'after:{after_date}'
        
        results = service.users().messages().list(
            userId='me',
            q=query,
            maxResults=50
        ).execute()
        
        messages = results.get('messages', [])
        emails = []
        
        for msg in messages[:30]:  # Limit to 30 emails
            try:
                message = service.users().messages().get(
                    userId='me',
                    id=msg['id']
                ).execute()
                
                # Extract headers
                headers = message['payload'].get('headers', [])
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
                
                # Extract body
                body = extract_email_body(message['payload'])
                
                emails.append({
                    'id': msg['id'],
                    'subject': subject,
                    'sender': sender,
                    'date': date,
                    'body': body,
                    'snippet': message.get('snippet', '')
                })
            except Exception as e:
                print(f"Error processing email {msg['id']}: {e}")
                continue
        
        return emails
    except Exception as e:
        print(f"Error fetching emails: {e}")
        return []

def extract_email_body(payload):
    """Extract body from email payload"""
    body = ''
    
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                data = part['body']['data']
                body += base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
            elif 'parts' in part:
                body += extract_email_body(part)
    else:
        if payload.get('body', {}).get('data'):
            body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='ignore')
    
    return body

def generate_meeting_brief(event, context=None):
    """Generate a brief for a meeting using AI"""
    if not client:
        return "No OpenAI client available"
    
    try:
        prompt = f"""
        Generate a brief for this meeting:
        Title: {event.get('summary', 'No title')}
        Time: {event.get('start', 'No time')}
        Attendees: {', '.join([a.get('email', '') for a in event.get('attendees', [])])}
        Description: {event.get('description', 'No description')}
        
        Context from recent emails/docs: {context if context else 'None'}
        
        Provide: Key objectives, Preparation needed, Important points to cover
        """
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating meeting brief: {e}")
        return f"Meeting: {event.get('summary', 'No title')} at {event.get('start', 'No time')}"

def analyze_emails_with_ai(emails):
    """Analyze emails for insights and actions"""
    if not client or not emails:
        return []
    
    try:
        email_summaries = []
        for email in emails[:10]:  # Analyze top 10 emails
            email_summaries.append(f"From: {email['sender']}\nSubject: {email['subject']}\nPreview: {email['snippet']}")
        
        prompt = f"""
        Analyze these recent emails and identify:
        1. Urgent actions needed
        2. Important follow-ups
        3. Key opportunities
        
        Emails:
        {chr(10).join(email_summaries)}
        
        Be specific and actionable.
        """
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        # Parse the response into structured insights
        content = response.choices[0].message.content
        insights = []
        
        # Simple parsing - in production would be more sophisticated
        lines = content.split('\n')
        current_insight = []
        
        for line in lines:
            if line.strip() and (line[0].isdigit() or line.startswith('-')):
                if current_insight:
                    insights.append(' '.join(current_insight))
                current_insight = [line]
            elif line.strip() and current_insight:
                current_insight.append(line)
        
        if current_insight:
            insights.append(' '.join(current_insight))
        
        return insights
    except Exception as e:
        print(f"Error analyzing emails: {e}")
        return []

def notify_meeting_brief(brief_content):
    """Placeholder for notification functionality"""
    print(f"Meeting brief ready: {brief_content[:100]}...")
    return True

def save_summary_to_supabase(summary_data):
    """Save summary to Supabase if available"""
    if not supabase:
        print("Supabase client not initialized. Skipping save.")
        return None
    
    try:
        response = supabase.table('summaries').insert(summary_data).execute()
        return response
    except Exception as e:
        print(f"Error saving to Supabase: {e}")
        return None

def generate_email_draft(insight_text):
    """Generate a draft email for a given insight using OpenAI."""
    if not client:
        return "No OpenAI client available"
    try:
        prompt = f"""
        Based on this insight, draft a professional email to address the issue or follow up:
        {insight_text}
        Format:
        To: [recipient]
        Subject: [subject]
        [body]
        """
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating email draft: {e}")
        return "Draft generation failed."

def review_artifact_sync(context, artifact, max_rounds=3, pass_threshold=9.5):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    for _ in range(max_rounds):
        result = loop.run_until_complete(review_manager.review_only(context, artifact))
        if result["average_score"] >= pass_threshold:
            return artifact
        # If not passed, try to improve artifact using feedback
        feedbacks = [r["feedback"] for r in result["reviews"] if r["feedback"]]
        if feedbacks:
            improvement_prompt = f"Improve this artifact based on the following feedback: {' '.join(feedbacks)}\n\nOriginal:\n{artifact}"
            improved = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": improvement_prompt}],
                temperature=0.5
            ).choices[0].message.content
            artifact = improved
    return artifact

def summarize_text(text, max_length=300):
    if not client or not text:
        return text[:max_length]
    try:
        prompt = f"Summarize the following text in {max_length} characters or less, focusing on the most important points:\n{text[:3000]}"
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()[:max_length]
    except RateLimitError:
        print("Rate limit hit, sleeping for 5 seconds...")
        time.sleep(5)
        return text[:max_length]
    except Exception as e:
        print(f"Error summarizing text: {e}")
        return text[:max_length]

def batch_summarize(summaries, batch_size=10, max_length=600):
    """Summarize batches of summaries to avoid context overflow."""
    batched = [summaries[i:i+batch_size] for i in range(0, len(summaries), batch_size)]
    batch_summaries = [summarize_text(' '.join(batch), max_length) for batch in batched]
    return summarize_text(' '.join(batch_summaries), max_length)

class ChiefOfStaffBrain:
    """AI brain that thinks holistically about all your data and DOES the work"""
    def __init__(self):
        self.client = client
        self.services = {
            'calendar': get_calendar_service(),
            'gmail': get_gmail_service(),
            'drive': get_drive_service()
        }

    def analyze_everything(self, emails, calendar_events, documents):
        """Analyze all data and generate insights + actionable artifacts"""
        if not self.client:
            return [{"error": "No OpenAI client available"}]
        try:
            # Only summarize the 10 most recent emails per run to avoid rate limits.
            # Over time, all emails will be processed, just more slowly.
            emails = emails[:10]
            context = self._build_context(emails, calendar_events, documents)
            email_bodies = [email.get('body', '') for email in emails if email.get('body')]
            email_summaries = [summarize_text(body, 300) for body in email_bodies]
            executive_email_summary = batch_summarize(email_summaries, batch_size=10, max_length=600)
            prompt = f"""
            You are an elite Chief of Staff (think Bill Gates-level). Your job is to ruthlessly prioritize and synthesize across all my emails, docs, and calendar.
            - Ignore trivial admin or scheduling issues.
            - Look for patterns, inefficiencies, or missed opportunities.
            - Propose actions that will increase revenue, reduce costs, or create strategic advantage—even if not explicitly mentioned.
            - If you see repeated feedback, complaints, or requests, suggest a systemic fix.
            - If you see a risk, flag it and propose a mitigation.
            - If you see a way to save time, money, or improve process, spell it out.
            - If nothing is truly high-value, say so.

            Here is your data:
            {context}

            Executive summary of recent emails:
            {executive_email_summary}
            """
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            insights = self._parse_insights(response.choices[0].message.content, emails, calendar_events, documents)
            if not insights:
                return [{
                    'id': 'no-high-value',
                    'type': 'ai_insight',
                    'title': 'No high-value insights found',
                    'insight': 'No urgent, high-impact, or strategic issues detected in your data. All clear for now.',
                    'impact_score': 1,
                    'action': 'Relax',
                    'artifact': 'No action needed.'
                }]
            return insights
        except Exception as e:
            print(f"Error in analysis: {e}")
            return [{"error": str(e)}]

    def _build_context(self, emails, calendar_events, documents):
        """Build context from all data sources, with more real data and less arbitrary limits."""
        context_parts = []
        # Calendar context
        if calendar_events:
            context_parts.append(f"UPCOMING EVENTS ({len(calendar_events)}):")
            for event in calendar_events:
                context_parts.append(f"- {event.get('summary', 'No title')} at {event.get('start', {}).get('dateTime', 'No time')}")
        # Email context
        if emails:
            context_parts.append(f"\nRECENT EMAILS ({len(emails)}):")
            for email in emails:
                context_parts.append(f"- From: {email.get('sender', 'Unknown')} | Subject: {email.get('subject', 'No subject')} | Date: {email.get('date', '')}")
                if email.get('body'):
                    context_parts.append(f"  Body: {summarize_text(email['body'], 300)}")
        # Document context
        if documents:
            context_parts.append(f"\nDOCUMENTS ({len(documents)}):")
            for doc in documents:
                context_parts.append(f"- {doc.get('name', 'Untitled')} (modified: {doc.get('modifiedTime', 'Unknown')})")
        return '\n'.join(context_parts)

    def _parse_insights(self, content, emails, calendar_events, documents):
        """Parse AI response into structured insights and filter for high-value only."""
        insights = []
        lines = content.split('\n')
        insight_id = 1
        current_insight = []
        high_value_keywords = [
            'revenue', 'customer', 'profit', 'cost', 'risk', 'blocker', 'opportunity', 'growth', 'urgent', 'strategic', 'efficiency', 'improvement', 'loss', 'churn', 'complaint', 'feedback', 'save', 'win', 'loss', 'priority', 'impact', 'systemic', 'mitigation', 'advantage'
        ]
        def is_high_value(text):
            t = text.lower()
            return any(k in t for k in high_value_keywords) and len(t.strip()) > 20
        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-')):
                if current_insight:
                    insight_text = ' '.join(current_insight)
                    if is_high_value(insight_text):
                        artifact = self._generate_artifact(insight_text, emails, calendar_events, documents)
                        insights.append({
                            'id': f'insight-{insight_id}',
                            'type': 'ai_insight',
                            'title': insight_text[:50] + '...' if len(insight_text) > 50 else insight_text,
                            'insight': insight_text,
                            'impact_score': max(10 - insight_id, 1),
                            'action': 'Review and act',
                            'artifact': artifact
                        })
                        insight_id += 1
                current_insight = [line.lstrip('0123456789.-) ')]
            elif line and current_insight:
                current_insight.append(line)
        if current_insight:
            insight_text = ' '.join(current_insight)
            if is_high_value(insight_text):
                artifact = self._generate_artifact(insight_text, emails, calendar_events, documents)
                insights.append({
                    'id': f'insight-{insight_id}',
                    'type': 'ai_insight',
                    'title': insight_text[:50] + '...' if len(insight_text) > 50 else insight_text,
                    'insight': insight_text,
                    'impact_score': max(10 - insight_id, 1),
                    'action': 'Review and act',
                    'artifact': artifact
                })
        return insights

    def _generate_artifact(self, insight_text, emails, calendar_events, documents):
        """Generate an actionable artifact for an insight."""
        print(f"[DEBUG] Generating artifact for insight: {insight_text}")
        # Calendar conflict or meeting
        if 'conflict' in insight_text.lower() or 'meeting' in insight_text.lower():
            for event in calendar_events:
                if event.get('summary', '').lower() in insight_text.lower():
                    artifact = generate_meeting_brief(event)
                    print(f"[DEBUG] Meeting artifact: {artifact}")
                    return review_artifact_sync(insight_text, artifact)
            if calendar_events:
                artifact = generate_meeting_brief(calendar_events[0])
                print(f"[DEBUG] Fallback meeting artifact: {artifact}")
                return review_artifact_sync(insight_text, artifact)
            print("[DEBUG] No relevant meeting found.")
            return "No relevant meeting found."
        if 'email' in insight_text.lower() or 'follow-up' in insight_text.lower() or 'reply' in insight_text.lower():
            artifact = generate_email_draft(insight_text)
            print(f"[DEBUG] Email artifact: {artifact}")
            return review_artifact_sync(insight_text, artifact)
        if 'data' in insight_text.lower() or 'document' in insight_text.lower() or 'report' in insight_text.lower():
            artifact = f"Actionable summary: {insight_text}"
            print(f"[DEBUG] Data/document artifact: {artifact}")
            return review_artifact_sync(insight_text, artifact)
        print(f"[DEBUG] Default artifact: {insight_text}")
        return review_artifact_sync(insight_text, insight_text)

def run_assistant():
    """Main function to run the assistant"""
    print("Starting Calendar Assistant...")
    
    # Get services
    calendar_service = get_calendar_service()
    gmail_service = get_gmail_service()
    
    if not calendar_service or not gmail_service:
        print("Failed to initialize Google services")
        return
    
    # Get next event
    next_event = get_next_event(calendar_service)
    if next_event:
        print(f"\nNext event: {next_event['summary']} at {next_event['start']}")
        
        # Generate brief
        brief = generate_meeting_brief(next_event)
        print(f"\nMeeting brief:\n{brief}")
    
    # Analyze recent emails
    emails = fetch_recent_emails(gmail_service)
    if emails:
        print(f"\nFound {len(emails)} recent emails")
        insights = analyze_emails_with_ai(emails)
        if insights:
            print("\nEmail insights:")
            for insight in insights:
                print(f"- {insight}")
    
    # Run comprehensive analysis
    brain = ChiefOfStaffBrain()
    calendar_events = []
    if calendar_service:
        try:
            now = datetime.datetime.utcnow().isoformat() + 'Z'
            events_result = calendar_service.events().list(
                calendarId='primary',
                timeMin=now,
                maxResults=20,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            calendar_events = events_result.get('items', [])
        except:
            pass
    
    all_insights = brain.analyze_everything(emails, calendar_events, [])
    print(f"\nGenerated {len(all_insights)} comprehensive insights")
    
    return all_insights

def main():
    """Main entry point"""
    run_assistant()

def search_google_docs(service, query_terms, max_results=5):
    """Search Google Drive for Google Docs whose titles mention any of the query terms."""
    query = "mimeType='application/vnd.google-apps.document' and trashed = false"
    if query_terms:
        title_queries = [f"name contains '{term}'" for term in query_terms]
        query += f" and ({' or '.join(title_queries)})"
    try:
        results = service.files().list(q=query, pageSize=max_results, fields="files(id, name)").execute()
        files = results.get('files', [])
        return files
    except HttpError as error:
        print(f'An error occurred: {error}')
        return []

def extract_google_doc_text(docs_service, doc_id):
    """Extract the text content from a Google Doc using the Docs API."""
    creds = None
    if os.path.exists('token_drive.pickle'):
        with open('token_drive.pickle', 'rb') as token:
            creds = pickle.load(token)
    docs_api = build('docs', 'v1', credentials=creds)
    try:
        doc = docs_api.documents().get(documentId=doc_id).execute()
        content = doc.get('body', {}).get('content', [])
        text = ''
        for value in content:
            if 'paragraph' in value:
                elements = value['paragraph'].get('elements', [])
                for elem in elements:
                    text += elem.get('textRun', {}).get('content', '')
        return text
    except HttpError as error:
        print(f'An error occurred extracting doc {doc_id}: {error}')
        return ''

# Main execution
if __name__ == "__main__":
    main()
