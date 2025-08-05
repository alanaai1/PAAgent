#!/usr/bin/env python3
"""
Setup script for Vertex AI with Claude Sonnet 4
"""
import os
from dotenv import load_dotenv
from anthropic import AnthropicVertex

def setup_vertex_ai():
    """Setup and test Vertex AI connection"""
    
    # Load environment variables
    load_dotenv()
    
    # Check required environment variables
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT_ID')
    region = os.getenv('VERTEX_AI_REGION', 'us-east5')
    
    if not project_id:
        print("❌ GOOGLE_CLOUD_PROJECT_ID not found in environment variables")
        print("Please set your Google Cloud Project ID:")
        print("export GOOGLE_CLOUD_PROJECT_ID='your-project-id'")
        return False
    
    print(f"✅ Project ID: {project_id}")
    print(f"✅ Region: {region}")
    
    try:
        # Initialize Vertex AI client
        client = AnthropicVertex(project_id=project_id, region=region)
        
        # Test the connection with a simple request
        print("🧪 Testing Vertex AI connection...")
        
        response = client.messages.create(
            model="claude-sonnet-4@20250514",
            max_tokens=50,
            messages=[{"role": "user", "content": "Hello! Please respond with 'Vertex AI is working!'"}],
            temperature=0.1
        )
        
        result = response.content[0].text.strip()
        print(f"✅ Vertex AI Response: {result}")
        
        if "Vertex AI is working" in result:
            print("🎉 Vertex AI setup successful!")
            return True
        else:
            print("⚠️  Unexpected response, but connection seems to work")
            return True
            
    except Exception as e:
        print(f"❌ Vertex AI setup failed: {e}")
        print("\nTroubleshooting steps:")
        print("1. Make sure you have enabled the Vertex AI API")
        print("2. Ensure you have access to Claude models in the Model Garden")
        print("3. Check that your Google Cloud credentials are properly configured")
        print("4. Verify your project has billing enabled")
        return False

def create_env_template():
    """Create a template .env file"""
    template = """# Vertex AI Configuration
GOOGLE_CLOUD_PROJECT_ID=your-project-id-here
VERTEX_AI_REGION=us-east5

# Google API Configuration (for Calendar, Gmail, Drive)
# Make sure you have the client_secret_*.json file in this directory

# Supabase Configuration (optional)
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key
"""
    
    with open('.env.template', 'w') as f:
        f.write(template)
    
    print("📝 Created .env.template file")
    print("Copy this to .env and fill in your actual values")

if __name__ == "__main__":
    print("🚀 Setting up Vertex AI with Claude Sonnet 4...")
    print("=" * 50)
    
    create_env_template()
    print()
    
    success = setup_vertex_ai()
    
    if success:
        print("\n🎉 Setup complete! You can now run your PAAgent with Vertex AI.")
        print("\nTo start the API server:")
        print("python api_server.py")
    else:
        print("\n❌ Setup failed. Please check the troubleshooting steps above.") 