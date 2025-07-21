#!/usr/bin/env python3

import json
from api_server import generate_ceo_response, generate_greeting

# Mock AI analysis data based on what we saw in the logs
mock_ai_analysis = {
    "urgent_priorities": [
        {
            "sender_name": "GitHub",
            "subject": "[GitHub] Please review this sign in",
            "content": "Your GitHub account was successfully signed in to but we did not recognize the location of the sign in."
        },
        {
            "sender_name": "Reminder",
            "subject": "Re: Here is your invoice UK-2025004318",
            "amount": "Not specified",
            "deadline": "14-Aug-2025",
            "content": "We've attached your invoice UK-2025004318 to this email as a PDF file."
        },
        {
            "sender_name": "Reminder",
            "subject": "Re: Fwd: Verify your identity for Companies House now",
            "content": "Please can you all go on and verify your identity."
        }
    ],
    "strategic_opportunities": [
        {
            "company_name": "OpenAI",
            "value": "Usage Tier 2",
            "subject": "Your API usage limits have increased",
            "content": "We're happy to share that we've automatically moved your organization from Usage Tier 1 to Usage Tier 2 based on your usage."
        },
        {
            "company_name": "Framer",
            "event": "Design Night: The AI Edition",
            "date": "Wednesday, July 23",
            "location": "Shack15, San Francisco, California",
            "subject": "Registration approved for Design Night: The AI Edition",
            "content": "You've got a spot at Design Night: The AI Edition."
        }
    ],
    "business_health": "The business appears engaged in continuous learning and networking (e.g., Design Night: The AI Edition), and is investing in AI technology (e.g., increased OpenAI API usage tier). The need to verify identity for Companies House and an upcoming invoice deadline indicate regular financial and legal management activities.",
    "recommended_actions": [
        {
            "action": "Review and verify the unrecognized GitHub sign-in attempt for security purposes.",
            "email_subject": "[GitHub] Please review this sign in"
        },
        {
            "action": "Prepare and process payment for the invoice UK-2025004318 before the due date of 14-Aug-2025.",
            "email_subject": "Re: Here is your invoice UK-2025004318"
        },
        {
            "action": "Ensure all relevant team members verify their identity with Companies House as requested.",
            "email_subject": "Re: Fwd: Verify your identity for Companies House now"
        }
    ],
    "executive_confidence": "High, based on the data's indication of active engagement in industry events, attention to security matters, and compliance with financial and legal obligations.",
    "specific_emails": [
        {
            "sender": "GitHub",
            "subject": "[GitHub] Please review this sign in",
            "key_content": "Your GitHub account was successfully signed in to but we did not recognize the location of the sign in."
        },
        {
            "sender": "OpenAI",
            "subject": "Your API usage limits have increased",
            "key_content": "We're happy to share that we've automatically moved your organization from Usage Tier 1 to Usage Tier 2 based on your usage."
        },
        {
            "sender": "Framer",
            "subject": "Registration approved for Design Night: The AI Edition",
            "key_content": "You've got a spot at Design Night: The AI Edition."
        }
    ],
    "specific_meetings": [
        {
            "title": "Sales overview",
            "attendees": ["shashank@advisoryai.com", "alan@advisoryai.com", "josh@advisoryai.com"],
            "purpose": "Discuss sales strategies and performance."
        },
        {
            "title": "Customer success overview",
            "attendees": ["shashank@advisoryai.com", "alan@advisoryai.com", "bradley@advisoryai.com"],
            "purpose": "Review customer success metrics and strategies."
        }
    ]
}

# Mock evaluation result
mock_evaluation_result = {
    'ai_analysis': mock_ai_analysis,
    'emails': [{'sender': 'test@example.com', 'subject': 'Test email'}],  # Mock email count
    'events': [{'summary': 'Test meeting'}],  # Mock event count
    'documents': []
}

# Test different user messages
test_messages = [
    "What is urgent today?",
    "draft my emails",
    "draft responses for those emails",
    "What meetings do I have today?",
    "Show me my strategic opportunities"
]

def test_responses():
    print("=== TESTING JARVIS RESPONSE GENERATION ===\n")
    
    personality = {'formality': 40, 'humor': 25, 'extraversion': 30}
    greeting = generate_greeting(personality)
    
    for message in test_messages:
        print(f"🧪 TESTING: '{message}'")
        print("-" * 50)
        
        try:
            response = generate_ceo_response(message, greeting, mock_evaluation_result, personality)
            print(response)
        except Exception as e:
            print(f"❌ ERROR: {e}")
        
        print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    test_responses() 