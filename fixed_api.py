from flask import Flask, jsonify
from flask_cors import CORS
import subprocess
import re
from datetime import datetime

app = Flask(__name__)
CORS(app)

def calculate_priority(text):
    """Calculate priority based on content and timing"""
    text_lower = text.lower()
    
    # Time-based priority
    if any(word in text_lower for word in ['today', 'morning', 'now', 'urgent', 'asap']):
        return 'CRITICAL', 0.95
    elif any(word in text_lower for word in ['tomorrow', 'week']):
        return 'HIGH', 0.85
    elif any(word in text_lower for word in ['cob', 'eod', 'by close']):
        return 'HIGH', 0.90
    else:
        return 'MEDIUM', 0.75

def categorize_insight(text):
    """Categorize based on content"""
    text_lower = text.lower()
    
    if any(word in text_lower for word in ['email', 'respond', 'reply']):
        return 'email', '📧 Email'
    elif any(word in text_lower for word in ['meeting', 'pitch', 'demo']):
        return 'calendar', '⏰ Calendar'
    elif any(word in text_lower for word in ['document', 'doc', 'update']):
        return 'document', '📄 Document'
    elif any(word in text_lower for word in ['code', 'api', 'merge']):
        return 'technical', '💻 Technical'
    elif any(word in text_lower for word in ['pattern', 'trend']):
        return 'pattern', '📊 Pattern'
    else:
        return 'strategic', '💡 Strategic'

@app.route('/api/dashboard')
def get_dashboard_data():
    # Run comprehensive agent
    result = subprocess.run(['python3', 'chief_of_staff_comprehensive.py'], 
                          capture_output=True, text=True, timeout=120)
    
    output = result.stdout
    insights = []
    
    if 'Final output (str):' in output:
        start = output.find('Final output (str):')
        end = output.find('- 4 new item(s)')
        if start != -1 and end != -1:
            content = output[start + len('Final output (str):'):end].strip()
            
            # Parse numbered items more carefully
            # Split by number patterns but keep the content together
            items = re.split(r'\n(?=\d+\.|\s+[a-z]\.)', content)
            
            for item in items:
                if not item.strip():
                    continue
                
                # Extract the full item including sub-bullets
                lines = item.split('\n')
                main_line = lines[0]
                full_content = item.strip()
                
                # Skip if too short
                if len(full_content) < 20:
                    continue
                
                # Get priority and category
                priority, confidence = calculate_priority(full_content)
                category, category_label = categorize_insight(full_content)
                
                # Extract title (first 80 chars of main line)
                title = main_line.strip()
                if len(title) > 80:
                    title = title[:77] + '...'
                
                # Create insight with FULL content
                insights.append({
                    'id': f'{category}-{len(insights)}',
                    'company': title,
                    'amount': int(100000 * confidence),
                    'stage': priority,  # CRITICAL, HIGH, MEDIUM
                    'action_preview': full_content[:200] + '...' if len(full_content) > 200 else full_content,
                    'confidence': confidence,
                    'category': category_label,
                    'action_data': {
                        'type': category,
                        'full_content': full_content,  # FULL CONTENT HERE
                        'title': title,
                        'priority': priority,
                        'lines': lines  # All lines for UI formatting
                    }
                })
    
    # Sort by priority
    insights.sort(key=lambda x: x['confidence'], reverse=True)
    
    return jsonify({
        'metrics': {
            'revenue_pipeline': sum(i['amount'] for i in insights),
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
