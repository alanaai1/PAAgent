#!/usr/bin/env python3
"""
Setup script for Slack Bot integration
"""
import os
import requests
from dotenv import load_dotenv

def test_slack_configuration():
    """Test Slack bot configuration"""
    print("=" * 60)
    print("SLACK BOT CONFIGURATION TEST")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    # Check required environment variables
    slack_bot_token = os.getenv('SLACK_BOT_TOKEN')
    slack_app_token = os.getenv('SLACK_APP_TOKEN')
    api_server_url = os.getenv('API_SERVER_URL', 'http://localhost:5000')
    
    print(f"\n📋 Configuration Check:")
    print(f"   SLACK_BOT_TOKEN: {'✅ Set' if slack_bot_token else '❌ Missing'}")
    print(f"   SLACK_APP_TOKEN: {'✅ Set' if slack_app_token else '❌ Missing'}")
    print(f"   API_SERVER_URL: {api_server_url}")
    
    # Test API server connection
    print(f"\n🧪 Testing API Server Connection:")
    try:
        response = requests.get(f"{api_server_url}/", timeout=5)
        if response.status_code == 200:
            print(f"✅ API Server is running at {api_server_url}")
        else:
            print(f"❌ API Server returned status {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to API Server: {e}")
        print(f"   Make sure api_server.py is running on {api_server_url}")
    
    # Test Slack tokens (if available)
    if slack_bot_token and slack_app_token:
        print(f"\n🧪 Testing Slack Tokens:")
        try:
            # Test bot token
            headers = {"Authorization": f"Bearer {slack_bot_token}"}
            response = requests.get("https://slack.com/api/auth.test", headers=headers, timeout=5)
            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    print(f"✅ Bot token is valid")
                    print(f"   Bot User ID: {result.get('user_id')}")
                    print(f"   Team: {result.get('team')}")
                else:
                    print(f"❌ Bot token is invalid: {result.get('error')}")
            else:
                print(f"❌ Bot token test failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Error testing bot token: {e}")
    else:
        print(f"\n⚠️  Cannot test Slack tokens - missing environment variables")
    
    print(f"\n" + "=" * 60)
    print("SETUP INSTRUCTIONS")
    print("=" * 60)
    
    print(f"\n1. Create a Slack App:")
    print(f"   - Go to https://api.slack.com/apps")
    print(f"   - Click 'Create New App'")
    print(f"   - Choose 'From scratch'")
    print(f"   - Name: 'Jarvis AI Assistant'")
    print(f"   - Select your workspace")
    
    print(f"\n2. Configure Bot Token Scopes:")
    print(f"   - Go to 'OAuth & Permissions'")
    print(f"   - Add these Bot Token Scopes:")
    print(f"     • app_mentions:read")
    print(f"     • channels:history")
    print(f"     • channels:read")
    print(f"     • chat:write")
    print(f"     • commands")
    print(f"     • groups:history")
    print(f"     • groups:read")
    print(f"     • im:history")
    print(f"     • im:read")
    print(f"     • im:write")
    print(f"     • mpim:history")
    print(f"     • mpim:read")
    print(f"     • mpim:write")
    print(f"     • users:read")
    print(f"     • users:read.email")
    
    print(f"\n3. Install App to Workspace:")
    print(f"   - Go to 'Install App'")
    print(f"   - Click 'Install to Workspace'")
    print(f"   - Copy the 'Bot User OAuth Token' (starts with xoxb-)")
    
    print(f"\n4. Configure Socket Mode:")
    print(f"   - Go to 'Basic Information'")
    print(f"   - Under 'App-Level Tokens', click 'Generate Token and Scopes'")
    print(f"   - Add scope: 'connections:write'")
    print(f"   - Copy the 'App-Level Token' (starts with xapp-)")
    
    print(f"\n5. Configure Event Subscriptions:")
    print(f"   - Go to 'Event Subscriptions'")
    print(f"   - Enable Events")
    print(f"   - Add these Bot Events:")
    print(f"     • app_mention")
    print(f"     • message.channels")
    print(f"     • message.groups")
    print(f"     • message.im")
    print(f"     • message.mpim")
    print(f"     • reaction_added")
    
    print(f"\n6. Configure Slash Commands:")
    print(f"   - Go to 'Slash Commands'")
    print(f"   - Click 'Create New Command'")
    print(f"   - Command: /jarvis")
    print(f"   - Description: 'Ask Jarvis AI Assistant'")
    print(f"   - Usage Hint: 'your question or request'")
    
    print(f"\n7. Set Environment Variables:")
    print(f"   - Add to your .env file:")
    print(f"     SLACK_BOT_TOKEN=xoxb-your-bot-token-here")
    print(f"     SLACK_APP_TOKEN=xapp-your-app-token-here")
    print(f"     API_SERVER_URL=http://localhost:5000")
    
    print(f"\n8. Start the Services:")
    print(f"   - Start API server: python3 api_server.py")
    print(f"   - Start Slack bot: python3 slack_bot.py")
    
    print(f"\n9. Test the Integration:")
    print(f"   - Mention the bot: @Jarvis hello")
    print(f"   - Use slash command: /jarvis what's the weather?")
    print(f"   - Send DM to the bot")
    print(f"   - React with 👋 to trigger a response")

if __name__ == "__main__":
    test_slack_configuration() 