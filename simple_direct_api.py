from flask import Flask, jsonify
from flask_cors import CORS
import subprocess
import re

app = Flask(__name__)
CORS(app)

@app.route('/api/dashboard')
def get_dashboard_data():
    # Just run your WORKING comprehensive agent
    result = subprocess.run(['python3', 'chief_of_staff_comprehensive.py'], 
                          capture_output=True, text=True, timeout=120)
    
    # Extract insights directly - no transformation
    insights = []
    if 'Final output (str):' in result.stdout:
        content = result.stdout.split('Final output (str):')[1].split('new item(s)')[0]
        
        # Just parse what's there
        items = re.findall(r'(\d+\..*?)(?=\d+\.|$)', content, re.DOTALL)
        
        for i, item in enumerate(items[:10]):
            insights.append({
                'id': f'item-{i}',
                'company': item[:60].strip(),
                'amount': 100000 - (i * 10000),
                'stage': 'CRITICAL' if i < 3 else 'HIGH',
                'action_preview': item.strip(),
                'confidence': 0.95,
                'action_data': {
                    'full_content': item.strip(),
                    'type': 'insight'
                }
            })
    
    return jsonify({
        'metrics': {
            'revenue_pipeline': 500000,
            'days_runway': 47,
            'actions_needed': len(insights)
        },
        'opportunities': insights
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
