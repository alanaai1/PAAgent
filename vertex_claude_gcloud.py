#!/usr/bin/env python3
"""
Use Claude through Vertex AI REST API with gcloud authentication
This uses gcloud application default credentials
"""
import os
import requests
import json
from dotenv import load_dotenv
from google.auth import default
from google.auth.transport.requests import Request

# Load environment variables
load_dotenv()

class VertexAIClaudeGCloud:
    """Claude client using Vertex AI REST API with gcloud authentication"""
    
    def __init__(self, project_id=None, region="us-east5"):
        self.project_id = project_id or os.getenv('GOOGLE_CLOUD_PROJECT_ID', 'aai-mobileapp')
        self.region = region or os.getenv('VERTEX_AI_REGION', 'us-east5')
        
        # Set up credentials using gcloud
        try:
            self.credentials, _ = default()
            if not self.credentials.valid:
                self.credentials.refresh(Request())
        except Exception as e:
            print(f"❌ Failed to get gcloud credentials: {e}")
            print("Please run: gcloud auth application-default login")
            raise
        
        # Base URL for Vertex AI API
        self.base_url = f"https://us-east5-aiplatform.googleapis.com/v1"
        
        print(f"✅ Initialized with:")
        print(f"   Project: {self.project_id}")
        print(f"   Region: {self.region}")
        print(f"   Using gcloud authentication")
    
    def create_message(self, model, messages, max_tokens=1024, temperature=0.3):
        """Send a message to Claude via Vertex AI REST API"""
        
        # Get access token
        if not self.credentials.valid:
            self.credentials.refresh(Request())
        
        access_token = self.credentials.token
        
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
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        
        try:
            response = requests.post(
                endpoint,
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

def test_vertex_gcloud():
    """Test Claude access with Vertex AI gcloud authentication"""
    
    print("=" * 60)
    print("TESTING CLAUDE VIA VERTEX AI GCLOUD AUTH")
    print("=" * 60)
    
    # Configuration
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT_ID', 'aai-mobileapp')
    region = os.getenv('VERTEX_AI_REGION', 'us-east5')
    
    print(f"\n📋 Configuration:")
    print(f"   Project: {project_id}")
    print(f"   Region: {region}")
    print(f"   Using gcloud authentication")
    
    # Initialize client
    try:
        client = VertexAIClaudeGCloud(
            project_id=project_id,
            region=region
        )
    except Exception as e:
        print(f"❌ Failed to initialize client: {e}")
        print("\n🔧 To fix:")
        print("1. Install gcloud CLI: https://cloud.google.com/sdk/docs/install")
        print("2. Run: gcloud auth application-default login")
        print("3. Set your project: gcloud config set project aai-mobileapp")
        return False
    
    # Test different Claude models
    models_to_test = [
        "claude-3-7-sonnet",
        "claude-3-5-sonnet@20240620",
        "claude-3-5-sonnet-v2@20241022",
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
        example_code = f'''# Working example using Vertex AI gcloud auth
from vertex_claude_gcloud import VertexAIClaudeGCloud

client = VertexAIClaudeGCloud(
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
        
        with open('working_gcloud_example.py', 'w') as f:
            f.write(example_code)
        
        print(f"\n📄 Created 'working_gcloud_example.py' with a working example")
        return True
    else:
        print("\n❌ No Claude models are accessible with gcloud authentication")
        print("\nPossible issues:")
        print("1. Claude models not enabled in Model Garden")
        print("2. gcloud account doesn't have necessary permissions")
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

if __name__ == "__main__":
    # Test the gcloud approach
    success = test_vertex_gcloud()
    
    if success:
        print("\n🎉 SUCCESS! You can use Claude with gcloud authentication!")
        print("\nNext steps:")
        print("1. Check 'working_gcloud_example.py' for a simple example")
        print("2. Update your code to use the VertexAIClaudeGCloud class")
    else:
        print("\n⚠️  Testing complete. Please check the troubleshooting steps above.") 