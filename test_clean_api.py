#!/usr/bin/env python3

from jarvis_api import analyze_with_ai, generate_response, _create_fallback_analysis

# Mock data for testing
mock_emails = [
    {
        'sender': 'GitHub',
        'subject': '[GitHub] Please review this sign in',
        'snippet': 'Your GitHub account was successfully signed in to but we did not recognize the location'
    },
    {
        'sender': 'OpenAI',
        'subject': 'Your API usage limits have increased',
        'snippet': 'We have automatically moved your organization from Usage Tier 1 to Usage Tier 2'
    }
]

mock_events = [
    {
        'summary': 'Sales overview',
        'start': {'dateTime': '2025-07-21T10:00:00Z'},
        'attendees': [
            {'email': 'shashank@advisoryai.com'},
            {'email': 'alan@advisoryai.com'},
            {'email': 'josh@advisoryai.com'}
        ]
    }
]

def test_analysis():
    """Test the AI analysis with mock data"""
    print("=== TESTING AI ANALYSIS ===")
    
    # Test with fallback (simulates AI failure)
    fallback = _create_fallback_analysis()
    print("Fallback structure:", fallback)
    
    print("\n=== TESTING RESPONSE GENERATION ===")
    
    # Create mock analysis
    mock_analysis = {
        "urgent_priorities": [
            {"sender": "GitHub", "subject": "[GitHub] Please review this sign in", "content": "Unrecognized sign-in location", "deadline": ""},
            {"sender": "Reminder", "subject": "Invoice due", "content": "Payment required", "deadline": "2025-08-14"}
        ],
        "opportunities": [
            {"company": "OpenAI", "value": "Usage Tier 2", "content": "API limits increased"}
        ],
        "business_status": "Active business operations with security alerts",
        "specific_emails": [
            {"sender": "GitHub", "subject": "[GitHub] Please review this sign in", "content": "Security alert"}
        ],
        "specific_meetings": [
            {"title": "Sales overview", "attendees": ["shashank@advisoryai.com"], "purpose": "Review sales metrics"}
        ]
    }
    
    # Test different message types including new actionable ones
    test_messages = [
        "What's urgent today?",
        "Can you help me with urgent items?",
        "Great, can you read and give me the rundown?", 
        "Help me secure GitHub",
        "What should I prioritize today?",
        "Show me my emails",
        "How is my business doing?"
    ]
    
    personality = {'formality': 40}
    
    for message in test_messages:
        print(f"\n🧪 TESTING: '{message}'")
        print("-" * 50)
        response = generate_response(message, mock_analysis, personality)
        print(response)
        print("\n" + "="*60)

if __name__ == "__main__":
    test_analysis() 