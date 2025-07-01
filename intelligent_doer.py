#!/usr/bin/env python3
"""
Framework for converting any "you should do X" into "I did X for you"
"""
import os
from agents import Agent, Runner, function_tool
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import pickle
import openai
import json

def get_google_creds():
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            return pickle.load(token)
    return None

@function_tool
def convert_nagging_to_action(nagging_insight: str, full_context: dict):
    """
    Take ANY nagging suggestion and convert it to completed work
    No hardcoding - pure intelligence
    """
    
    # Use AI to understand what needs to be created
    prompt = f"""
    The AI assistant suggested: {nagging_insight}
    
    Context available:
    - Calendar events: {full_context.get('events', [])}
    - Recent emails: {full_context.get('emails', [])}
    - Documents: {full_context.get('documents', [])}
    
    Instead of telling the user to do this, CREATE what they need.
    
    Determine:
    1. What type of artifact would solve this (deck, email, document, analysis, etc.)
    2. What specific content it needs based on context
    3. Generate that artifact completely
    
    Output as JSON:
    {{
        "artifact_type": "deck|email|document|analysis|schedule|other",
        "title": "What you created",
        "content": "The full artifact",
        "metadata": {{
            "recipients": [],
            "deadline": "",
            "related_to": ""
        }}
    }}
    """
    
    # Let AI figure out what to create
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    
    return json.loads(response.choices[0].message.content)

@function_tool
def analyze_and_do():
    """
    Find all the nagging and convert it ALL to completed work
    """
    creds = get_google_creds()
    if not creds:
        return "No credentials"
    
    # Get all context
    services = {
        'calendar': build("calendar", "v3", credentials=creds),
        'gmail': build("gmail", "v1", credentials=creds),
        'drive': build("drive", "v3", credentials=creds)
    }
    
    # First, run the normal analysis to get the "nagging"
    context = gather_all_context(services)
    
    # Get the AI's normal suggestions (the nagging)
    nagging_insights = get_ai_suggestions(context)
    
    # Now convert EACH nagging item to completed work
    completed_work = []
    
    for nagging in nagging_insights:
        # This is the magic - convert ANY nagging to action
        artifact = convert_nagging_to_action(nagging, context)
        completed_work.append(artifact)
    
    return completed_work

def gather_all_context(services):
    """Gather all available context"""
    context = {'events': [], 'emails': [], 'documents': []}
    
    # Get calendar
    now = datetime.utcnow().isoformat() + "Z"
    events = services['calendar'].events().list(
        calendarId="primary",
        timeMin=now,
        maxResults=20,
        singleEvents=True,
        orderBy="startTime"
    ).execute()
    context['events'] = events.get('items', [])
    
    # Get emails
    messages = services['gmail'].users().messages().list(
        userId="me",
        maxResults=30
    ).execute()
    context['emails'] = messages.get('messages', [])
    
    # Get documents
    files = services['drive'].files().list(
        pageSize=20,
        orderBy="modifiedTime desc"
    ).execute()
    context['documents'] = files.get('files', [])
    
    return context

def get_ai_suggestions(context):
    """Get the normal 'nagging' suggestions"""
    prompt = f"""
    Based on this context:
    Events: {len(context['events'])} upcoming
    Emails: {len(context['emails'])} recent
    Documents: {len(context['documents'])} files
    
    What should the user do? List specific actions needed.
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    
    # Parse into list of suggestions
    suggestions = response.choices[0].message.content.split('\n')
    return [s.strip() for s in suggestions if s.strip()]

# The agent that converts nagging to doing
doer = Agent(
    name="Doer Not Nagger",
    model="gpt-4",
    instructions="""
    You take nagging suggestions and convert them to completed work.
    
    Pattern:
    - If you would say "draft an email to X" → Create the email
    - If you would say "prepare deck for Y" → Create the deck
    - If you would say "analyze Z" → Do the analysis
    
    Never tell someone to do something. Do it for them.
    Use the context to make intelligent artifacts.
    """,
    tools=[analyze_and_do, convert_nagging_to_action]
)

if __name__ == "__main__":
    runner = Runner(agent=doer)
    result = runner.run("Convert all my to-dos into completed work")
    print(result.final_output)
