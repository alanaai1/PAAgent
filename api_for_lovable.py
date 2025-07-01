from flask import Flask, jsonify
from flask_cors import CORS
import subprocess
import re

app = Flask(__name__)
CORS(app)

@app.route('/api/dashboard')
def get_dashboard_data():
    # Run your working agent
    result = subprocess.run(['python3', 'chief_of_staff_comprehensive.py'], 
                          capture_output=True, text=True, timeout=120)
    
    # Extract the Final output section
    output = result.stdout
    insights = []
    
    if 'Final output (str):' in output:
        content = output.split('Final output (str):')[1].split('- 4 new item(s)')[0]
        
        # Find all numbered items (1., 2., etc)
        items = re.findall(r'(\d+)\.\s+([^.]+(?:\.|:)[^0-9]+)', content)
        
        for i, (num, text) in enumerate(items[:5]):  # Top 5 items
            insights.append({
                'id': f'item-{num}',
                'company': text[:50] + '...',
                'amount': 100000 - (i * 20000),
                'stage': 'Today' if 'Today' in text else 'Action Required',
                'action_preview': text[:150] + '...',
                'confidence': 0.95,
                'action_data': {'full': text}
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
