#!/usr/bin/env python3
"""
Slack Bot Service for PAAgent
Integrates with existing API server to handle Slack messages
"""
import os
import json
import requests
import logging
from datetime import datetime
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Slack configuration
SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
SLACK_APP_TOKEN = os.getenv('SLACK_APP_TOKEN')
API_SERVER_URL = os.getenv('API_SERVER_URL', 'http://localhost:5000')

# Initialize Slack app
app = App(token=SLACK_BOT_TOKEN)

# Track conversation contexts
conversation_contexts = {}

def get_conversation_key(channel_id, thread_ts=None):
    """Generate a unique key for conversation tracking"""
    return f"{channel_id}:{thread_ts or 'main'}"

def forward_to_api_server(message, user_id, channel_id, thread_ts=None):
    """Forward message to API server and get response"""
    try:
        # Prepare the request payload
        payload = {
            "message": message,
            "slack_context": {
                "user_id": user_id,
                "channel_id": channel_id,
                "thread_ts": thread_ts,
                "timestamp": datetime.now().isoformat()
            }
        }
        
        # Send to API server
        response = requests.post(
            f"{API_SERVER_URL}/api/jarvis/chat",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get('message', 'Sorry, I received an empty response.')
        else:
            logger.error(f"API server error: {response.status_code} - {response.text}")
            return "Sorry, I'm having trouble processing your request right now."
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Request to API server failed: {e}")
        return "Sorry, I'm unable to connect to my processing system right now."
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return "Sorry, something went wrong while processing your request."

@app.event("message")
def handle_message_events(body, say, client):
    """Handle incoming message events"""
    try:
        event = body["event"]
        
        # Ignore bot messages to prevent loops
        if event.get("bot_id"):
            return
        
        # Get message details
        channel_id = event.get("channel")
        user_id = event.get("user")
        text = event.get("text", "").strip()
        thread_ts = event.get("thread_ts")
        ts = event.get("ts")
        
        # Ignore empty messages
        if not text:
            return
        
        # Check if this is a DM or allowed channel
        if not is_allowed_channel(channel_id):
            logger.info(f"Ignoring message from unauthorized channel: {channel_id}")
            return
        
        # Log the incoming message
        logger.info(f"Received message from {user_id} in {channel_id}: {text[:100]}...")
        
        # Get user info for context
        user_info = get_user_info(client, user_id)
        user_name = user_info.get("real_name", "Unknown User")
        
        # Add user context to message
        contextual_message = f"Message from {user_name}: {text}"
        
        # Forward to API server
        response_text = forward_to_api_server(
            contextual_message, 
            user_id, 
            channel_id, 
            thread_ts
        )
        
        # Send response back to Slack
        if thread_ts:
            # Reply in thread
            say(text=response_text, thread_ts=thread_ts)
        else:
            # Reply in channel
            say(text=response_text)
        
        logger.info(f"Sent response to {channel_id}")
        
    except Exception as e:
        logger.error(f"Error handling message event: {e}")
        say(text="Sorry, I encountered an error while processing your message.")

def is_allowed_channel(channel_id):
    """Check if the channel is allowed for bot interaction"""
    allowed_channels = os.getenv('SLACK_ALLOWED_CHANNELS', '').split(',')
    allowed_channels = [ch.strip() for ch in allowed_channels if ch.strip()]
    
    # If no specific channels are configured, allow all
    if not allowed_channels:
        return True
    
    return channel_id in allowed_channels

def get_user_info(client, user_id):
    """Get user information from Slack"""
    try:
        result = client.users_info(user=user_id)
        if result["ok"]:
            return result["user"]
    except Exception as e:
        logger.error(f"Error getting user info: {e}")
    
    return {"real_name": "Unknown User"}

@app.event("app_mention")
def handle_app_mention(body, say, client):
    """Handle when the bot is mentioned"""
    try:
        event = body["event"]
        
        # Get message details
        channel_id = event.get("channel")
        user_id = event.get("user")
        text = event.get("text", "").strip()
        thread_ts = event.get("thread_ts")
        
        # Remove bot mention from text
        bot_user_id = event.get("bot_id")
        if bot_user_id:
            # Remove the bot mention from the text
            text = text.replace(f"<@{bot_user_id}>", "").strip()
        
        if not text:
            text = "Hello! How can I help you today?"
        
        # Log the mention
        logger.info(f"Bot mentioned by {user_id} in {channel_id}: {text[:100]}...")
        
        # Get user info
        user_info = get_user_info(client, user_id)
        user_name = user_info.get("real_name", "Unknown User")
        
        # Add user context
        contextual_message = f"Direct mention from {user_name}: {text}"
        
        # Forward to API server
        response_text = forward_to_api_server(
            contextual_message, 
            user_id, 
            channel_id, 
            thread_ts
        )
        
        # Send response
        if thread_ts:
            say(text=response_text, thread_ts=thread_ts)
        else:
            say(text=response_text)
        
        logger.info(f"Sent response to mention in {channel_id}")
        
    except Exception as e:
        logger.error(f"Error handling app mention: {e}")
        say(text="Sorry, I encountered an error while processing your mention.")

@app.command("/jarvis")
def handle_slash_command(ack, command, say):
    """Handle slash command /jarvis"""
    try:
        # Acknowledge the command
        ack()
        
        # Get command details
        user_id = command["user_id"]
        channel_id = command["channel_id"]
        text = command["text"].strip()
        
        if not text:
            text = "Hello! How can I help you today?"
        
        # Log the command
        logger.info(f"Slash command from {user_id} in {channel_id}: {text[:100]}...")
        
        # Forward to API server
        response_text = forward_to_api_server(text, user_id, channel_id)
        
        # Send response
        say(text=response_text)
        
        logger.info(f"Sent response to slash command in {channel_id}")
        
    except Exception as e:
        logger.error(f"Error handling slash command: {e}")
        ack(text="Sorry, I encountered an error while processing your command.")

@app.event("reaction_added")
def handle_reaction(body, say, client):
    """Handle reaction events (optional)"""
    try:
        event = body["event"]
        reaction = event.get("reaction")
        user_id = event.get("user")
        channel_id = event.get("item", {}).get("channel")
        
        # Only respond to specific reactions (e.g., 👋 for hello)
        if reaction == "wave":
            logger.info(f"Wave reaction from {user_id} in {channel_id}")
            
            user_info = get_user_info(client, user_id)
            user_name = user_info.get("real_name", "Unknown User")
            
            response_text = forward_to_api_server(
                f"Wave reaction from {user_name}",
                user_id,
                channel_id
            )
            
            say(text=response_text)
            
    except Exception as e:
        logger.error(f"Error handling reaction: {e}")

def start_slack_bot():
    """Start the Slack bot service"""
    if not SLACK_BOT_TOKEN or not SLACK_APP_TOKEN:
        logger.error("Missing Slack tokens. Please set SLACK_BOT_TOKEN and SLACK_APP_TOKEN")
        return
    
    logger.info("Starting Slack bot service...")
    logger.info(f"API Server URL: {API_SERVER_URL}")
    
    # Start the app
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()

if __name__ == "__main__":
    start_slack_bot() 