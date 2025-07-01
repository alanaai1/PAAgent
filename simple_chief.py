#!/usr/bin/env python3
import os
from agents import Agent, Runner, function_tool
from googleapiclient.discovery import build
import pickle
from datetime import datetime

def get_creds():
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            return pickle.load(token)
    return None

@function_tool
def quick_analysis():
    """Quick analysis of your situation"""
    creds = get_creds()
    if not creds:
        return "No credentials"
    
    try:
        cal = build("calendar", "v3", credentials=creds)
        
        # Just get next event
        now = datetime.utcnow().isoformat() + 'Z'
        events = cal.events().list(
            calendarId='primary',
            timeMin=now,
            maxResults=3,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        items = events.get('items', [])
        if not items:
            return "No upcoming events"
        
        output = "Your next meetings:\n\n"
        for event in items:
            start = event['start'].get('dateTime', event['start'].get('date'))
            output += f"• {event.get('summary', 'No title')} at {start}\n"
        
        output += "\nRecommendation: Focus on preparing for your first meeting."
        
        return output
        
    except Exception as e:
        return f"Error: {str(e)}"

chief = Agent(
    name="Simple Chief",
    model="o4-mini",
    instructions="Analyze the calendar and provide insights.",
    tools=[quick_analysis]
)

result = Runner.run_sync(chief, "What should I focus on?")
print("\n📅 Analysis:")
print("=" * 40)
print(result.final_output)
