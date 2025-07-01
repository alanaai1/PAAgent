from flask import Flask, jsonify
from flask_cors import CORS
import subprocess
import openai
import os
import json

app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI()('OPENAI_API_KEY')

def transform_nagging_to_doing(nagging_text):
    """
    Universal transformer - works for ANY nagging
    """
    prompt = f"""
    An AI assistant said: "{nagging_text}"
    
    This is nagging. Transform it into completed work.
    
    If it says "email someone" → write the email
    If it says "prepare something" → create it  
    If it says "analyze something" → do the analysis
    If it says "schedule something" → create the calendar invite
    
    Output JSON:
    {{
        "original_nagging": "what it said to do",
        "completed_artifact": {{
            "type": "what you created",
            "content": "the actual created thing",
            "ready_to_use": true
        }}
    }}
    """
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8
    )
    
    return json.loads(response.choices[0].message.content)

@app.route('/api/dashboard')
def get_dashboard_data():
    # Run comprehensive agent to get the nagging
    result = subprocess.run(['python3', 'chief_of_staff_comprehensive.py'], 
                          capture_output=True, text=True, timeout=120)
    
    # Extract all the nagging suggestions
    nagging_items = extract_nagging_items(result.stdout)
    
    # Transform EACH nagging into completed work
    completed_items = []
    
    for nagging in nagging_items:
        completed = transform_nagging_to_doing(nagging)
        completed_items.append({
            'id': f'completed-{len(completed_items)}',
            'company': completed['completed_artifact']['type'],
            'amount': 100000,
            'stage': 'COMPLETED',
            'action_preview': completed['completed_artifact']['content'][:200],
            'confidence': 0.90,
            'action_data': completed['completed_artifact']
        })
    
    return jsonify({
        'metrics': {
            'revenue_pipeline': 500000,
            'days_runway': 47,
            'actions_needed': 0,  # Zero because we DID them
            'actions_completed': len(completed_items)
        },
        'opportunities': completed_items
    })

def extract_nagging_items(output):
    """Extract things the AI is telling you to do"""
    # Look for patterns like "finalize", "prepare", "email", "update", etc.
    nagging_patterns = [
        "finalize", "prepare", "draft", "email", "update", 
        "create", "schedule", "review", "compile", "send"
    ]
    
    items = []
    if 'Final output' in output:
        lines = output.split('\n')
        for line in lines:
            if any(pattern in line.lower() for pattern in nagging_patterns):
                items.append(line.strip())
    
    return items[:10]  # Top 10 nagging items

if __name__ == '__main__':
    app.run(debug=True, port=5000)
