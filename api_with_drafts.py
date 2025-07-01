from flask import Flask, jsonify
from flask_cors import CORS
import subprocess
import re
import openai
import os

app = Flask(__name__)
CORS(app)

# Initialize OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')
client = openai.OpenAI() if os.getenv('OPENAI_API_KEY') else None

def generate_email_draft(action_context):
    """Generate an email draft based on the action context"""
    if not client:
        return "Configure OpenAI API key"
    
    prompt = f"""
    Based on this action item: {action_context}
    
    Generate a professional email draft.
    Format:
    To: [email]
    Subject: [subject]
    
    [body]
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content
    except:
        return "Draft generation failed"

@app.route('/api/dashboard')
def get_dashboard_data():
    # Run your comprehensive agent
    result = subprocess.run(['python3', 'chief_of_staff_comprehensive.py'], 
                          capture_output=True, text=True, timeout=120)
    
    output = result.stdout
    insights = []
    
    if 'Final output (str):' in output:
        content = output.split('Final output (str):')[1].split('- 4 new item(s)')[0]
        
        # Extract items with email keywords
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in ['email', 'reply', 'send', 'follow-up']):
                # This is an email action - generate a draft
                draft = generate_email_draft(line)
                
                insights.append({
                    'id': f'email-{i}',
                    'company': line[:50] + '...',
                    'amount': 100000,
                    'stage': 'Draft Ready',
                    'action_preview': line[:150] + '...',
                    'confidence': 0.90,
                    'action_data': {
                        'type': 'email',
                        'full_context': line,
                        'draft': draft,
                        'executable': True
                    }
                })
            elif re.match(r'^\s*\d+\.', line) and len(line.strip()) > 10:
                # Regular insight
                insights.append({
                    'id': f'insight-{i}',
                    'company': line[:50] + '...',
                    'amount': 80000,
                    'stage': 'Action Required',
                    'action_preview': line[:150] + '...',
                    'confidence': 0.85,
                    'action_data': {
                        'type': 'insight',
                        'full_context': line,
                        'executable': False
                    }
                })
    
    return jsonify({
        'metrics': {
            'revenue_pipeline': 500000,
            'days_runway': 47,
            'actions_needed': len(insights)
        },
        'opportunities': insights,
        'time_allocation': {
            'revenue_percentage': 65,
            'target_percentage': 80
        }
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
