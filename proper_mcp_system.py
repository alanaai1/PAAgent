#!/usr/bin/env python3
"""
Proper MCP System - CEO Review & Self-Improvement
Runs Jarvis, reviews output as CEO, provides feedback to Cursor
"""

import asyncio
import json
import subprocess
import time
from datetime import datetime
import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CEOMCPReviewer:
    """CEO that reviews Jarvis output and provides improvement feedback"""
    
    def __init__(self):
        self.jarvis_server_url = "http://localhost:5000"
        self.cursor_feedback_file = "ceo_feedback.md"
        self.review_history = []
        self.performance_metrics = {
            "response_quality": 0.0,
            "business_relevance": 0.0,
            "action_effectiveness": 0.0,
            "overall_score": 0.0
        }
        
    async def run_jarvis_and_review(self, test_message: str = "What's urgent today?"):
        """Run Jarvis and review output as CEO"""
        logger.info("🎯 CEO MCP: Starting Jarvis review cycle")
        
        try:
            # Step 1: Run Jarvis
            jarvis_response = await self._run_jarvis(test_message)
            
            # Step 2: CEO Review
            ceo_review = await self._perform_ceo_review(jarvis_response)
            
            # Step 3: Generate Improvement Feedback
            feedback = await self._generate_cursor_feedback(ceo_review)
            
            # Step 4: Save feedback for Cursor
            await self._save_feedback_for_cursor(feedback)
            
            return {
                "jarvis_response": jarvis_response,
                "ceo_review": ceo_review,
                "cursor_feedback": feedback,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"CEO MCP Review failed: {e}")
            return {"error": str(e)}
    
    async def _run_jarvis(self, message: str) -> dict:
        """Run Jarvis API and get response"""
        try:
            response = requests.post(
                f"{self.jarvis_server_url}/api/jarvis/chat",
                json={
                    "message": message,
                    "personality": {"conscientiousness": 80}
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Jarvis API failed: {response.status_code}"}
                
        except Exception as e:
            return {"error": f"Failed to run Jarvis: {e}"}
    
    async def _perform_ceo_review(self, jarvis_response: dict) -> dict:
        """Perform CEO review of Jarvis output"""
        
        # Extract response text
        response_text = jarvis_response.get("message", "No response")
        
        # CEO Review Criteria
        review_criteria = {
            "business_focus": {
                "score": 0.0,
                "comments": [],
                "weight": 0.3
            },
            "action_orientation": {
                "score": 0.0,
                "comments": [],
                "weight": 0.25
            },
            "clarity": {
                "score": 0.0,
                "comments": [],
                "weight": 0.2
            },
            "urgency_handling": {
                "score": 0.0,
                "comments": [],
                "weight": 0.25
            }
        }
        
        # Review Business Focus
        business_keywords = ["revenue", "pipeline", "deals", "customers", "growth", "strategy"]
        business_count = sum(1 for keyword in business_keywords if keyword.lower() in response_text.lower())
        review_criteria["business_focus"]["score"] = min(business_count / 3, 1.0)
        review_criteria["business_focus"]["comments"].append(
            f"Business focus: {business_count} business keywords detected"
        )
        
        # Review Action Orientation
        action_keywords = ["do", "execute", "implement", "start", "begin", "take action"]
        action_count = sum(1 for keyword in action_keywords if keyword.lower() in response_text.lower())
        review_criteria["action_orientation"]["score"] = min(action_count / 2, 1.0)
        review_criteria["action_orientation"]["comments"].append(
            f"Action orientation: {action_count} action keywords detected"
        )
        
        # Review Clarity
        sentences = response_text.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
        clarity_score = 1.0 if 5 <= avg_sentence_length <= 15 else 0.5
        review_criteria["clarity"]["score"] = clarity_score
        review_criteria["clarity"]["comments"].append(
            f"Clarity: Average sentence length {avg_sentence_length:.1f} words"
        )
        
        # Review Urgency Handling
        urgency_keywords = ["urgent", "critical", "immediate", "asap", "priority"]
        urgency_count = sum(1 for keyword in urgency_keywords if keyword.lower() in response_text.lower())
        review_criteria["urgency_handling"]["score"] = min(urgency_count / 2, 1.0)
        review_criteria["urgency_handling"]["comments"].append(
            f"Urgency handling: {urgency_count} urgency indicators"
        )
        
        # Calculate overall score
        overall_score = sum(
            criteria["score"] * criteria["weight"] 
            for criteria in review_criteria.values()
        )
        
        return {
            "overall_score": overall_score,
            "criteria": review_criteria,
            "response_text": response_text,
            "ceo_verdict": self._get_ceo_verdict(overall_score)
        }
    
    def _get_ceo_verdict(self, score: float) -> str:
        """Get CEO verdict based on score"""
        if score >= 0.8:
            return "EXCELLENT - This response demonstrates strong business acumen and actionable insights"
        elif score >= 0.6:
            return "GOOD - Solid business focus with room for improvement in action orientation"
        elif score >= 0.4:
            return "NEEDS IMPROVEMENT - Lacks sufficient business focus and actionable guidance"
        else:
            return "POOR - Missing critical business elements and actionable direction"
    
    async def _generate_cursor_feedback(self, ceo_review: dict) -> dict:
        """Generate specific feedback for Cursor to improve Jarvis"""
        
        score = ceo_review["overall_score"]
        criteria = ceo_review["criteria"]
        
        # Identify specific improvement areas
        improvement_areas = []
        
        if criteria["business_focus"]["score"] < 0.7:
            improvement_areas.append({
                "area": "business_focus",
                "priority": "HIGH",
                "suggestion": "Enhance business vocabulary and revenue-focused language",
                "code_improvement": '''
# Business Focus Enhancement
def enhance_business_response(self, message):
    business_keywords = ["revenue", "pipeline", "growth", "customers", "deals"]
    # Add business context to all responses
    return self.add_business_context(response)
'''
            })
        
        if criteria["action_orientation"]["score"] < 0.6:
            improvement_areas.append({
                "area": "action_orientation", 
                "priority": "HIGH",
                "suggestion": "Include specific actionable steps and next actions",
                "code_improvement": '''
# Action Orientation Enhancement
def add_action_items(self, response):
    action_items = [
        "Immediate next steps:",
        "1. [Specific action]",
        "2. [Timeline]",
        "3. [Expected outcome]"
    ]
    return response + "\\n\\n" + "\\n".join(action_items)
'''
            })
        
        if criteria["clarity"]["score"] < 0.7:
            improvement_areas.append({
                "area": "clarity",
                "priority": "MEDIUM", 
                "suggestion": "Improve sentence structure and readability",
                "code_improvement": '''
# Clarity Enhancement
def improve_clarity(self, response):
    # Break long sentences into shorter, clearer ones
    sentences = response.split('.')
    improved_sentences = []
    for sentence in sentences:
        if len(sentence.split()) > 15:
            # Split long sentences
            improved_sentences.extend(self.split_long_sentence(sentence))
        else:
            improved_sentences.append(sentence)
    return '. '.join(improved_sentences)
'''
            })
        
        return {
            "overall_score": score,
            "ceo_verdict": ceo_review["ceo_verdict"],
            "improvement_areas": improvement_areas,
            "priority_actions": [
                "Enhance business vocabulary in response generation",
                "Add specific actionable steps to all responses", 
                "Improve sentence structure for better clarity",
                "Include urgency indicators for critical items"
            ]
        }
    
    async def _save_feedback_for_cursor(self, feedback: dict):
        """Save feedback in format Cursor can use for improvements"""
        
        feedback_content = f"""# CEO Review Feedback - {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Overall Score: {feedback['overall_score']:.2f}/1.0

## CEO Verdict
{feedback['ceo_verdict']}

## Improvement Areas

"""
        
        for area in feedback.get('improvement_areas', []):
            feedback_content += f"""### {area['area'].replace('_', ' ').title()} - {area['priority']} Priority
**Suggestion:** {area['suggestion']}

**Code Improvement:**
```python
{area['code_improvement']}
```

"""
        
        feedback_content += f"""
## Priority Actions for Cursor
{chr(10).join([f"- {action}" for action in feedback.get('priority_actions', [])])}

## Next Steps
1. Review this feedback in Cursor
2. Implement the suggested code improvements
3. Re-run Jarvis to test improvements
4. Repeat CEO review cycle

---
*Generated by CEO MCP Review System*
"""
        
        # Save to file
        with open(self.cursor_feedback_file, 'w') as f:
            f.write(feedback_content)
        
        logger.info(f"💼 CEO feedback saved to {self.cursor_feedback_file}")

# Flask app for MCP system
app = Flask(__name__)
CORS(app)

# Global CEO reviewer
ceo_reviewer = CEOMCPReviewer()

@app.route('/api/mcp/run-review', methods=['POST'])
def run_ceo_review():
    """Run CEO review cycle"""
    try:
        data = request.get_json()
        test_message = data.get('message', "What's urgent today?")
        
        # Run review in background
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                ceo_reviewer.run_jarvis_and_review(test_message)
            )
        finally:
            loop.close()
        
        return jsonify({
            "status": "success",
            "result": result
        })
        
    except Exception as e:
        return jsonify({
            "status": "error", 
            "message": str(e)
        })

@app.route('/api/mcp/status', methods=['GET'])
def get_mcp_status():
    """Get MCP system status"""
    return jsonify({
        "system": "CEO MCP Review System",
        "status": "operational",
        "last_review": ceo_reviewer.review_history[-1] if ceo_reviewer.review_history else None,
        "performance_metrics": ceo_reviewer.performance_metrics,
        "feedback_file": ceo_reviewer.cursor_feedback_file
    })

if __name__ == '__main__':
    print("🎯 CEO MCP Review System")
    print("=" * 50)
    print("🚀 Capabilities:")
    print("• Runs Jarvis and reviews output")
    print("• Provides CEO-level feedback")
    print("• Generates improvement suggestions for Cursor")
    print("• Tracks performance metrics")
    print("=" * 50)
    
    app.run(port=5003, debug=True) 