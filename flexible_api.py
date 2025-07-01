from flask import Flask, jsonify
from flask_cors import CORS
import subprocess
import json
import openai
import os

app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv('OPENAI_API_KEY')
client = openai.OpenAI() if os.getenv('OPENAI_API_KEY') else None

def generate_insight_content(insight_text, category):
    """Generate appropriate content based on insight category"""
    if not client:
        return {"error": "No OpenAI client"}
    
    # Different prompts for different categories
    prompts = {
        'draft_email': f"Draft a professional email for: {insight_text}",
        'strategic_analysis': f"Provide strategic analysis on: {insight_text}\nConsider second-order effects and contrarian viewpoints.",
        'warning': f"Explain why this is a concern: {insight_text}\nBe specific about the cost (time/money/opportunity).",
        'opportunity': f"Expand on this opportunity: {insight_text}\nWhat's the upside? What are the risks?",
        'pattern_recognition': f"Analyze this pattern: {insight_text}\nWhat does it mean? What should be done about it?",
        'stop_doing': f"Make the case for stopping: {insight_text}\nWhat's the opportunity cost? What should replace it?",
        'think_piece': f"Provide thoughtful reflection on: {insight_text}\nConsider multiple perspectives."
    }
    
    prompt = prompts.get(category, f"Provide insights on: {insight_text}")
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8
        )
        return {
            "category": category,
            "content": response.choices[0].message.content,
            "original_insight": insight_text
        }
    except Exception as e:
        return {"error": str(e)}

def categorize_insights(insights_text):
    """Let AI categorize insights"""
    if not client:
        return []
    
    prompt = f"""
    Categorize each insight and suggest the most valuable response:
    
    {insights_text}
    
    Return JSON array with: category, reasoning, suggested_action
    
    Categories: draft_email, strategic_analysis, warning, opportunity, 
    pattern_recognition, stop_doing, delegation_suggestion, think_piece, etc.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return json.loads(response.choices[0].message.content)
    except:
        return []

@app.route('/api/dashboard')
def get_dashboard_data():
    # Run comprehensive agent
    result = subprocess.run(['python3', 'chief_of_staff_comprehensive.py'], 
                          capture_output=True, text=True, timeout=120)
    
    output = result.stdout
    insights = []
    
    if 'Final output (str):' in output:
        content = output.split('Final output (str):')[1].split('- 4 new item(s)')[0]
        
        # Get AI to categorize the insights
        categories = categorize_insights(content)
        
        # Process each categorized insight
        for i, cat in enumerate(categories[:10]):  # Top 10
            # Generate appropriate content based on category
            enhanced = generate_insight_content(
                cat.get('text', ''),
                cat.get('category', 'insight')
            )
            
            # Different stages based on category
            stage_map = {
                'draft_email': 'Draft Ready',
                'warning': '⚠️ Warning',
                'opportunity': '🚀 Opportunity',
                'strategic_analysis': '�� Strategy',
                'stop_doing': '🛑 Stop This',
                'pattern_recognition': '�� Pattern Detected'
            }
            
            insights.append({
                'id': f'insight-{i}',
                'company': cat.get('text', '')[:50] + '...',
                'amount': 100000 - (i * 10000),
                'stage': stage_map.get(cat.get('category'), 'Action Required'),
                'action_preview': enhanced.get('content', '')[:200] + '...',
                'confidence': 0.85,
                'action_data': {
                    'category': cat.get('category'),
                    'full_content': enhanced.get('content'),
                    'reasoning': cat.get('reasoning'),
                    'original_insight': cat.get('text')
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
