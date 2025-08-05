#!/usr/bin/env python3
"""
Simplified API server using Vertex AI Claude
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import os
from vertex_claude_gcloud import VertexAIClaudeGCloud
from datetime import datetime

# Load environment variables
load_dotenv()

# Initialize Vertex AI client
PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT_ID', 'aai-mobileapp')
REGION = os.getenv('VERTEX_AI_REGION', 'us-east5')

client = VertexAIClaudeGCloud(project_id=PROJECT_ID, region=REGION)

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def health_check():
    """Quick health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Jarvis API (Vertex AI)',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/jarvis/test', methods=['GET'])
def jarvis_test():
    """Quick test endpoint"""
    return jsonify({
        'message': 'Jarvis is working with Vertex AI!',
        'status': 'success',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/jarvis/chat', methods=['POST'])
def jarvis_chat():
    """Main Jarvis chat endpoint using Vertex AI"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        print(f"JARVIS: {message}")
        
        # Generate response using Vertex AI
        response = client.create_message(
            model="claude-3-7-sonnet",
            messages=[{"role": "user", "content": message}],
            max_tokens=800,
            temperature=0.7
        )
        
        return jsonify({
            'message': response.strip(),
            'timestamp': datetime.now().isoformat(),
            'type': 'response'
        })
        
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({
            'message': f"Sorry, I'm having trouble right now. Error: {str(e)}",
            'timestamp': datetime.now().isoformat(),
            'type': 'error'
        }), 500

if __name__ == '__main__':
    print("Starting Jarvis API server with Vertex AI...")
    app.run(debug=True, port=5000) 