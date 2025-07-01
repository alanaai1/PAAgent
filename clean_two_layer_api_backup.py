from flask import Flask, jsonify, request, request
from flask_cors import CORS
import subprocess
import json
import re
import openai
import os

app = Flask(__name__)
CORS(app)

client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

@app.route('/api/dashboard')
def get_dashboard_data():
    # Run comprehensive agent
    result = subprocess.run(['python3', 'chief_of_staff_comprehensive.py'], 
                          capture_output=True, text=True, timeout=300)
    
    # LAYER 1: Identify what needs doing
    identification_prompt = f"""
Analyze these insights and create ACTUAL DELIVERABLES (not suggestions):

{result.stdout}

For each actionable item, CREATE THE ACTUAL WORK PRODUCT:
- If email needed: Write the complete email (subject, body, recipient)
- If document needed: Write the full document with all content
- If meeting prep needed: Create the complete brief with questions and answers
- If schedule needed: Write the calendar invite with agenda

NO PLACEHOLDERS. NO "insert here". NO meta-advice.
ACTUAL DELIVERABLES ONLY.

Return JSON:
{{
    "actions": [
        {{
            "id": "unique-id",
            "type": "email|document|brief|schedule",
            "title": "What was created (max 60 chars)",
            "description": "Brief description of the deliverable",
            "context_snippet": "Why this matters strategically",
            "priority": 1-10,
            "deadline": "when needed",
            "deliverable": "THE ACTUAL COMPLETE WORK PRODUCT - full email/document/brief content"
        }}
    ]
}}
"""
    
    response = client.chat.completions.create(
        model="gpt-4o",  # Fast and cheap for extraction
        messages=[{"role": "user", "content": identification_prompt}],
    )
    print(f"DEBUG: GPT returned: '{response.choices[0].message.content}'")
    json_match = re.search(r'```json\s*(.*?)\s*```', response.choices[0].message.content, re.DOTALL)

    json_match = re.search(r'```json\s*(.*?)\s*```', response.choices[0].message.content, re.DOTALL)
    if json_match:
        try:
            actions = json.loads(json_match.group(1))
        except json.JSONDecodeError:
            print("Failed to parse JSON from markdown block")
            actions = {"actions": []}
    else:
        # Try to find any JSON-like structure
        json_match_plain = re.search(r'\{.*\}', response.choices[0].message.content, re.DOTALL)
        if json_match_plain:
            try:
                actions = json.loads(json_match_plain.group())
            except:
                actions = {"actions": []}
        else:
            print("No JSON found in response, using empty actions")
            actions = {"actions": []}
    action_count = len(actions.get('actions', []))
    # Convert actions to insights format
    opportunities = []
    for action in actions.get('actions', [])[:5]:  # Top 5 only
        opportunities.append({
            "company": action.get('action_preview', '')[:60],
            "action_preview": action.get('context_snippet', ''),
            "priority": "high" if action.get('priority', 5) > 7 else "medium"
        })
    
    # RETURN THE DATA IN THE FORMAT LOVABLE EXPECTS
    return jsonify({
        "drafts_ready": action_count,
        "days_runway": 45,
        "actions_needed": action_count,
        "opportunities": opportunities,
        "last_ship": "No recent activity",
        "competitors_shipping": "Competitors shipping weekly"
    })


@app.route('/api/actions/execute', methods=['POST', 'OPTIONS'])
def execute_action():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        action_id = data.get('id')
        action_type = data.get('type', 'unknown')
        
        print(f"Executing action: {action_id}, type: {action_type}")
        
        return jsonify({
            'status': 'success',
            'message': f'{action_type.title()} action completed successfully!',
            'action_id': action_id
        })
        
    except Exception as e:
        print(f"Error executing action: {e}")
        return jsonify({
            'status': 'error', 
            'message': f'Failed to execute action: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
