from flask import Flask, jsonify
from flask_cors import CORS
import subprocess
import re

app = Flask(__name__)
CORS(app)

@app.route('/api/dashboard')
def get_dashboard_data():
    # Run comprehensive agent
    result = subprocess.run(['python3', 'chief_of_staff_comprehensive.py'], 
                          capture_output=True, text=True, timeout=120)
    
    output = result.stdout
    print("=== FULL OUTPUT ===")
    print(output)
    print("=== END OUTPUT ===")
    
    insights = []
    
    if 'Final output (str):' in output:
        # Extract the actual content
        start = output.find('Final output (str):')
        end = output.find('- 4 new item(s)')
        if start != -1 and end != -1:
            content = output[start + len('Final output (str):'):end].strip()
            
            print("=== EXTRACTED CONTENT ===")
            print(content)
            print("=== END CONTENT ===")
            
            # Extract actual insights from the numbered list
            # Look for patterns like "1. Today (June 11)" or "a. FCA Pitch"
            lines = content.split('\n')
            current_insight = []
            
            for line in lines:
                # Check if this is a new numbered/lettered item
                if re.match(r'^\s*\d+\.|^\s*[a-z]\.|^\s*•', line):
                    # Save previous insight if exists
                    if current_insight:
                        full_text = ' '.join(current_insight)
                        if len(full_text) > 20:  # Only real insights
                            insights.append({
                                'id': f'insight-{len(insights)}',
                                'company': full_text[:60] + '...',
                                'amount': 100000 - (len(insights) * 10000),
                                'stage': 'Action Required',
                                'action_preview': full_text[:200] + '...',
                                'confidence': 0.85,
                                'action_data': {
                                    'full_content': full_text,
                                    'category': 'insight'
                                }
                            })
                    # Start new insight
                    current_insight = [line.strip()]
                elif line.strip() and current_insight:
                    # Continue current insight
                    current_insight.append(line.strip())
            
            # Don't forget last insight
            if current_insight:
                full_text = ' '.join(current_insight)
                if len(full_text) > 20:
                    insights.append({
                        'id': f'insight-{len(insights)}',
                        'company': full_text[:60] + '...',
                        'amount': 100000 - (len(insights) * 10000),
                        'stage': 'Action Required',
                        'action_preview': full_text[:200] + '...',
                        'confidence': 0.85,
                        'action_data': {
                            'full_content': full_text,
                            'category': 'insight'
                        }
                    })
    
    print(f"=== FOUND {len(insights)} INSIGHTS ===")
    for i, insight in enumerate(insights):
        print(f"{i}: {insight['action_preview'][:100]}...")
    
    # If no insights found, add the raw output as one insight
    if not insights and output:
        insights.append({
            'id': 'full-output',
            'company': 'Chief of Staff Analysis',
            'amount': 100000,
            'stage': 'Full Report',
            'action_preview': output[:300] + '...',
            'confidence': 0.90,
            'action_data': {
                'full_content': output,
                'category': 'report'
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
