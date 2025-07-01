#!/usr/bin/env python3
from flask import Flask, jsonify, request
from flask_cors import CORS
import subprocess
import json
import re

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({'status': 'AI Chief of Staff API Running'})


@app.route('/api/dashboard')
def get_dashboard_data():
    try:
        print("Running comprehensive agent...")

        # Try to load cached results first
        cached_insights = None
        if os.path.exists('agent_cache.json'):
            try:
                with open('agent_cache.json', 'r') as f:
                    cache = json.load(f)
                    # Use cache if less than 5 minutes old
                    if time.time() - cache.get('timestamp', 0) < 300:
                        cached_insights = cache.get('insights', [])
                        print("Using cached insights while agent runs...")
            except:
                pass
        
        # If we have cache, return it immediately
        if cached_insights:
            return jsonify({
                'metrics': {
                    'revenue_pipeline': len(cached_insights) * 50000,
                    'days_runway': 47,
                    'actions_needed': len(cached_insights)
                },
                'opportunities': cached_insights,
                'time_allocation': {
                    'revenue_percentage': 65,
                    'target_percentage': 80
                }
            })
        

        
        # Run your WORKING comprehensive agent
        result = subprocess.run(
            ['python3', 'chief_of_staff_comprehensive.py'], 
            capture_output=True, 
            text=True,
            timeout=60
        )
        
        output = result.stdout
        insights = []
        
        # Extract the Final output section
        if 'Final output (str):' in output:
            start = output.find('Final output (str):') + len('Final output (str):')
            end = output.find('- 5 new item(s)')
            if end == -1:
                end = output.find('(See ')
            
            if end != -1:
                final_text = output[start:end].strip()
                
                # Parse numbered items (like 1. FCA Pitch, 2. Product Demo, etc)
                import re
                items = re.split(r'\n\s*\d+\.\s+', final_text)
                
                for i, item in enumerate(items[1:], 1):  # Skip first empty split
                    if item.strip():
                        title = item.split(':')[0].strip() if ':' in item else item[:50]
                        insights.append({
                            'id': f'priority-{i}',
                            'company': title,
                            'amount': 100000 - (i * 10000),
                            'stage': 'Action Required',
                            'action_preview': item[:200] + '...' if len(item) > 200 else item,
                            'confidence': 0.95,
                            'action_data': {
                                'type': 'insight',
                                'full_content': item
                            }
                        })
        
        # If no insights parsed, show the full output
        if not insights:
            preview = output[:300].replace('\n', ' ')
            insights.append({
                'id': 'analysis',
                'company': 'Chief of Staff Analysis',
                'amount': 100000,
                'stage': 'Complete',
                'action_preview': preview,
                'confidence': 0.90,
                'action_data': {'type': 'full', 'full_content': output}
            })
        
        return jsonify({
            'metrics': {
                'revenue_pipeline': len(insights) * 50000,
                'days_runway': 47,
                'actions_needed': len(insights)
            },
            'opportunities': insights,
            'time_allocation': {
                'revenue_percentage': 40,
                'target_percentage': 80
            }
        })
        
    except Exception as e:
        print(f'Error: {e}')
        return jsonify({
            'error': str(e),
            'metrics': {'revenue_pipeline': 0, 'days_runway': 0, 'actions_needed': 0},
            'opportunities': [],
            'time_allocation': {'revenue_percentage': 0, 'target_percentage': 80}
        })
@app.route('/api/actions/execute', methods=['POST'])
def execute_action():
    data = request.json
    action_id = data.get('id')
    action_type = data.get('type')
    
    print(f'Executing action: {action_id} of type {action_type}')
    
    return jsonify({
        'success': True,
        'message': f'Action {action_id} executed successfully',
        'action_type': action_type
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')
    
    # For now, just echo back
    return jsonify({
        'response': f'Received: {user_message}. (Chat integration coming soon)'
    })

if __name__ == '__main__':
    print("Starting AI Chief of Staff API Server...")
    print("Dashboard endpoint: http://localhost:5000/api/dashboard")
    app.run(debug=True, port=5000)
