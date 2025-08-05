#!/usr/bin/env python3
"""
Use Claude through Vertex AI REST API with API Key
This works WITHOUT gcloud authentication!
"""
import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class VertexAIClaude:
    """Claude client using Vertex AI REST API with API key"""
    
    def __init__(self, api_key=None, project_id=None, region="us-east5"):
        self.api_key = api_key or os.getenv('VERTEX_AI_API_KEY')
        self.project_id = project_id or os.getenv('GOOGLE_CLOUD_PROJECT_ID', 'aai-mobileapp')
        self.region = region or os.getenv('VERTEX_AI_REGION', 'us-east5')
        
        if not self.api_key:
            raise ValueError("API key is required. Set VERTEX_AI_API_KEY in .env")
        if not self.project_id:
            raise ValueError("Project ID is required. Set GOOGLE_CLOUD_PROJECT_ID in .env")
        
        # Base URL for Vertex AI API
        self.base_url = f"https://us-east5-aiplatform.googleapis.com/v1"
        
        print(f"✅ Initialized with:")
        print(f"   Project: {self.project_id}")
        print(f"   Region: {self.region}")
        print(f"   API Key: {'*' * 20}{self.api_key[-4:]}")
    
    def create_message(self, model, messages, max_tokens=1024, temperature=0.3):
        """Send a message to Claude via Vertex AI REST API"""
        
        # Construct the endpoint URL
        endpoint = f"{self.base_url}/projects/{self.project_id}/locations/{self.region}/publishers/anthropic/models/{model}:streamRawPredict"
        
        # Prepare the request payload (Anthropic format)
        payload = {
            "anthropic_version": "vertex-2023-10-16",
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        # Make the API request
        headers = {
            "Content-Type": "application/json"
        }
        
        # Add API key to URL
        url_with_key = f"{endpoint}?key={self.api_key}"
        
        try:
            response = requests.post(
                url_with_key,
                headers=headers,
                json=payload,
                stream=True  # Enable streaming
            )
            
            if response.status_code == 200:
                # Parse streaming response
                full_response = ""
                for line in response.iter_lines():
                    if line:
                        try:
                            # Parse the JSON response
                            json_response = json.loads(line.decode('utf-8').replace('data: ', ''))
                            if 'content' in json_response:
                                for content in json_response['content']:
                                    if content.get('type') == 'text':
                                        full_response += content.get('text', '')
                        except json.JSONDecodeError:
                            continue
                
                return full_response if full_response else self._parse_non_streaming(response)
            else:
                error_msg = f"API request failed with status {response.status_code}: {response.text}"
                print(f"❌ {error_msg}")
                raise Exception(error_msg)
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            raise
    
    def _parse_non_streaming(self, response):
        """Parse non-streaming response as fallback"""
        try:
            result = response.json()
            if 'content' in result and len(result['content']) > 0:
                return result['content'][0].get('text', '')
            return str(result)
        except:
            return response.text

def test_vertex_api_key():
    """Test Claude access with Vertex AI API key"""
    
    print("=" * 60)
    print("TESTING CLAUDE VIA VERTEX AI REST API")
    print("=" * 60)
    
    # Your credentials
    api_key = os.getenv('VERTEX_AI_API_KEY', 'AIzaSyBr4UECvxKccqGPy2q8RTlCi7iHJC0srFU')
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT_ID', 'aai-mobileapp')
    region = os.getenv('VERTEX_AI_REGION', 'us-east5')
    
    print(f"\n📋 Configuration:")
    print(f"   Project: {project_id}")
    print(f"   Region: {region}")
    print(f"   API Key: ...{api_key[-8:]}")
    
    # Initialize client
    client = VertexAIClaude(
        api_key=api_key,
        project_id=project_id,
        region=region
    )
    
    # Test different Claude models
    models_to_test = [
        "claude-3-7-sonnet",
        "claude-3-5-sonnet@20240620",
        "claude-3-5-sonnet-v2@20241022",  # Newer version if available
        "claude-3-sonnet@20240229",
        "claude-3-opus@20240229",
        "claude-3-haiku@20240307",
    ]
    
    print("\n🧪 Testing Claude models:")
    print("-" * 40)
    
    working_models = []
    
    for model in models_to_test:
        print(f"\nTesting {model}...")
        try:
            response = client.create_message(
                model=model,
                messages=[{
                    "role": "user",
                    "content": "Reply with 'Hello from Claude!' in exactly those words."
                }],
                max_tokens=50,
                temperature=0
            )
            
            if response:
                print(f"✅ SUCCESS! Response: {response.strip()}")
                working_models.append(model)
            else:
                print(f"❌ No response received")
                
        except Exception as e:
            error_str = str(e)
            if "404" in error_str or "not found" in error_str.lower():
                print(f"❌ Model not available")
            elif "403" in error_str or "permission" in error_str.lower():
                print(f"❌ Permission denied - may need to enable model in Model Garden")
            elif "400" in error_str:
                print(f"❌ Bad request - model name might be incorrect")
            else:
                print(f"❌ Error: {error_str[:100]}...")
    
    # Summary
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    
    if working_models:
        print(f"\n✅ Found {len(working_models)} working model(s):")
        for model in working_models:
            print(f"   • {model}")
        
        print(f"\n📝 Recommended model for your code:")
        print(f'   model="{working_models[0]}"')
        
        # Generate working example
        example_code = f'''# Working example using Vertex AI API key
from vertex_claude_client import VertexAIClaude

client = VertexAIClaude(
    api_key="{api_key}",
    project_id="{project_id}",
    region="{region}"
)

response = client.create_message(
    model="{working_models[0]}",
    messages=[
        {{"role": "user", "content": "Hello Claude!"}}
    ],
    max_tokens=800,
    temperature=0.3
)

print(response)
'''
        
        with open('working_api_key_example.py', 'w') as f:
            f.write(example_code)
        
        print(f"\n📄 Created 'working_api_key_example.py' with a working example")
        return True
    else:
        print("\n❌ No Claude models are accessible with this API key")
        print("\nPossible issues:")
        print("1. Claude models not enabled in Model Garden")
        print("2. API key doesn't have necessary permissions")
        print("3. Vertex AI API not enabled for the project")
        print("4. Billing not enabled")
        
        print("\n🔧 To fix:")
        print("1. Go to: https://console.cloud.google.com/vertex-ai/model-garden")
        print(f"   (Make sure you're in project: {project_id})")
        print("2. Search for 'Claude' and click on a Claude model")
        print("3. Click 'Enable' or 'Deploy' if needed")
        print("4. Ensure Vertex AI API is enabled:")
        print("   https://console.cloud.google.com/apis/library/aiplatform.googleapis.com")
        
        return False

def create_flask_integration():
    """Create a Flask integration example"""
    
    integration_code = '''# Flask integration with Vertex AI Claude using API key
from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()

app = Flask(__name__)
CORS(app)

class VertexAIClaude:
    """Simplified Claude client for Flask"""
    
    def __init__(self):
        self.api_key = os.getenv('VERTEX_AI_API_KEY')
        self.project_id = os.getenv('GOOGLE_CLOUD_PROJECT_ID')
        self.region = os.getenv('VERTEX_AI_REGION', 'us-east5')
        self.model = "claude-3-7-sonnet"  # Update based on test results
        
    def chat(self, message, max_tokens=800):
        """Send message to Claude"""
        endpoint = f"https://us-east5-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/us-east5/publishers/anthropic/models/{self.model}:streamRawPredict"
        
        payload = {
            "anthropic_version": "vertex-2023-10-16",
            "messages": [{"role": "user", "content": message}],
            "max_tokens": max_tokens,
            "temperature": 0.3
        }
        
        response = requests.post(
            f"{endpoint}?key={self.api_key}",
            headers={"Content-Type": "application/json"},
            json=payload
        )
        
        if response.status_code == 200:
            # Parse the response
            result = response.json()
            if 'content' in result:
                return result['content'][0].get('text', '')
        
        raise Exception(f"API error: {response.status_code}")

# Initialize Claude client
claude = VertexAIClaude()

@app.route('/api/jarvis/chat', methods=['POST'])
def jarvis_chat():
    """Chat endpoint"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        # Get response from Claude
        response = claude.chat(message)
        
        return jsonify({
            'message': response,
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({
            'message': f"Error: {str(e)}",
            'status': 'error'
        }), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
'''
    
    with open('flask_vertex_claude.py', 'w') as f:
        f.write(integration_code)
    
    print("\n📄 Created 'flask_vertex_claude.py' with Flask integration")

if __name__ == "__main__":
    # Test the API key approach
    success = test_vertex_api_key()
    
    if success:
        create_flask_integration()
        print("\n🎉 SUCCESS! You can use Claude with your Vertex AI API key!")
        print("\nNext steps:")
        print("1. Check 'working_api_key_example.py' for a simple example")
        print("2. Check 'flask_vertex_claude.py' for Flask integration")
        print("3. Update your code to use the VertexAIClaude class")
    else:
        print("\n⚠️  Testing complete. Please check the troubleshooting steps above.") 