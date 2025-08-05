#!/usr/bin/env python3
"""
Test Vertex AI integration in API server context
"""
from vertex_claude_gcloud import VertexAIClaudeGCloud
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_api_vertex_integration():
    """Test the Vertex AI client in API server context"""
    
    print("Testing Vertex AI integration for API server...")
    
    # Initialize client like in API server
    PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT_ID', 'aai-mobileapp')
    REGION = os.getenv('VERTEX_AI_REGION', 'us-east5')
    
    try:
        client = VertexAIClaudeGCloud(project_id=PROJECT_ID, region=REGION)
        
        # Test simple message
        response = client.create_message(
            model="claude-3-7-sonnet",
            messages=[{"role": "user", "content": "What is the capital of Nepal?"}],
            max_tokens=200,
            temperature=0.3
        )
        
        print("✅ SUCCESS!")
        print(f"Question: What is the capital of Nepal?")
        print(f"Response: {response}")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

if __name__ == "__main__":
    test_api_vertex_integration() 