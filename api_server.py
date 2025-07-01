from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import os
import subprocess
from datetime import datetime, timedelta
import openai

# Import real functions from calendar_assistant
from calendar_assistant import (
    get_next_event,
    get_calendar_service,
    generate_meeting_brief,
    fetch_recent_emails,
    get_gmail_service,
    search_google_docs,
    get_drive_service,
    ChiefOfStaffBrain
)

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = openai.OpenAI(api_key=OPENAI_API_KEY)

app = Flask(__name__)
CORS(app)

# --- Mocked/missing functions and objects ---
def search_supabase_notes(*args, **kwargs):
    return []
def run_assistant(*args, **kwargs):
    return None
# Mock Supabase
class MockSupabase:
    def table(self, *args, **kwargs):
        class Table:
            def select(self, *a, **k):
                class Result: data = []
                return Result()
            def eq(self, *a, **k):
                return self
            def execute(self):
                class Result: data = []
                return Result()
            def insert(self, *a, **k):
                return self
        return Table()
supabase = MockSupabase()

def get_dashboard_data():
    try:
        print("=== STARTING REAL ANALYSIS ===")
        
        # Initialize the brain
        brain = ChiefOfStaffBrain()
        
        # Get real services
        service = get_calendar_service()
        gmail_service = get_gmail_service()
        
        # Fetch REAL data
        events = service.events().list(
            calendarId='primary',
            timeMin=datetime.utcnow().isoformat() + 'Z',
            maxResults=20,
            singleEvents=True,
            orderBy='startTime'
        ).execute().get('items', [])
        
        emails = fetch_recent_emails(gmail_service, hours=168)
        
        print(f"Found {len(events)} events and {len(emails)} emails")
        
        # Run the REAL analysis
        all_insights = brain.analyze_everything(emails, events, [])
        
        print(f"Generated {len(all_insights)} insights")
        
        # Convert insights to opportunities
        opportunities = []
        for insight in all_insights[:10]:
            opportunities.append({
                "id": insight['id'],
                "company": insight['title'],
                "amount": insight.get('impact_score', 0) * 10000,
                "stage": insight['type'].replace('_', ' ').title(),
                "action_preview": insight['insight'][:150] + '...',
                "confidence": min(insight['impact_score'] / 10, 0.99),
                "artifact": insight.get('artifact', ''),
                "action_data": insight  # Pass the whole insight
            })
        
        return {
            "metrics": {
                "revenue_pipeline": len(opportunities) * 50000,
                "days_runway": 47,
                "actions_needed": len(opportunities)
            },
            "opportunities": opportunities,
            "time_allocation": {
                "revenue_percentage": 40,
                "target_percentage": 80
            }
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "metrics": {"revenue_pipeline": 0, "days_runway": 0, "actions_needed": 0},
            "opportunities": [],
            "time_allocation": {"revenue_percentage": 0, "target_percentage": 80}
        }

def get_pending_actions():
    return []

def execute_action(action_id):
    return {"status": "mock_executed", "id": action_id, "message": "Mock action executed!"}

@app.route('/api/dashboard', methods=['GET'])
def api_dashboard():
    return jsonify(get_dashboard_data())

@app.route('/api/actions/pending', methods=['GET'])
def api_actions_pending():
    return jsonify({"pending_actions": get_pending_actions()})

@app.route('/api/actions/execute', methods=['POST'])
def api_actions_execute():
    data = request.json
    action_id = data.get('id')
    action_type = data.get('type', 'email')
    # Log this action to track what was approved
    print(f"User approved action: {action_id} of type: {action_type}")
    # For now, just mark as "approved" in a list
    if not hasattr(app, 'approved_actions'):
        app.approved_actions = []
    app.approved_actions.append({
        'id': action_id,
        'type': action_type,
        'timestamp': datetime.now().isoformat(),
        'status': 'approved_for_manual_sending'
    })
    # Later, this is where you'd actually:
    # - Send the email via Gmail API
    # - Update calendar
    # - Post to Slack
    # But for now, just track approvals
    return jsonify({
        'status': 'success',
        'message': 'Draft approved! Open Gmail to send.',
        'action_id': action_id
    })

@app.route('/api/actions/approved', methods=['GET'])
def get_approved_actions():
    return jsonify(getattr(app, 'approved_actions', []))

@app.route('/api/actions/edit', methods=['POST'])
def api_actions_edit():
    data = request.json
    action_id = data.get('id')
    return jsonify({"status": "not_found", "id": action_id})

@app.route('/api/patterns/learn', methods=['POST'])
def learn_pattern():
    data = request.json
    # Mock learning
    return jsonify({"learned": True, "patterns_count": 0})

@app.route('/api/chat', methods=['POST'])
def chat_with_chief_of_staff():
    """Conversational AI endpoint"""
    try:
        user_message = request.json.get('message', '')
        # Get context
        service = get_calendar_service()
        next_event = get_next_event(service)
        # Simple response for now
        context_info = f"Your next meeting is {next_event.get('summary', 'No meetings')}. "
        # Use GPT-4 for intelligent response
        system_prompt = f"""You are an AI Chief of Staff. \
        Current context: {context_info}\n        Be helpful, proactive, and conversational."""
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        )
        return jsonify({
            "response": response.choices[0].message.content,
            "drafts": [],
            "context_used": {
                "meetings_analyzed": 1,
                "emails_reviewed": 0
            }
        })
    except Exception as e:
        return jsonify({
            "response": f"I'm having trouble connecting right now: {str(e)}",
            "drafts": [],
            "context_used": {}
        })

# --- Placeholder/mock implementations for helpers ---
def get_all_calendar_events():
    # TODO: Replace with real calendar event fetching
    return []
def extract_all_commitments():
    # TODO: Replace with real commitment extraction
    return []
def get_past_meeting_notes():
    # TODO: Replace with real meeting notes fetching
    return []
def analyze_user_intent(message):
    # TODO: Replace with real intent analysis
    return "general"
def generate_weekly_plan_response(context):
    return "Here's your weekly plan! (mock)"
def draft_all_weekly_work(context):
    return ["Draft: Weekly work summary (mock)"]
def generate_meeting_prep_response(context, user_message):
    return "Here's your meeting prep! (mock)"
def draft_meeting_materials(context, user_message):
    return ["Draft: Meeting materials (mock)"]
def draft_email_from_request(context, user_message):
    return "Draft: Email based on your request (mock)"
def analyze_priorities(context):
    return "Here's what you should focus on! (mock)"
def draft_priority_actions(context):
    return ["Draft: Priority actions (mock)"]
def extract_actionable_drafts(response, context):
    return ["Draft: Actionable from response (mock)"]

@app.route('/api/test-dashboard', methods=['GET'])
def test_dashboard():
    return jsonify({
        "test": "working",
        "function_exists": True,
        "direct_call": get_dashboard_data()
    })



@app.route('/api/actions/execute', methods=['POST'])
def execute_action():
    data = request.json
    action_id = data.get('id')
    action_type = data.get('type')
    
    # For now, just log the action
    print(f'Executing action: {action_id} of type {action_type}')
    
    # In the future, this could actually send emails, create calendar events, etc.
    return jsonify({
        'success': True,
        'message': f'Action {action_id} executed successfully',
        'action_type': action_type
    })


if __name__ == '__main__':
    app.run(port=5000, debug=True) 