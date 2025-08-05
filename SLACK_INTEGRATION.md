# Slack Integration for Jarvis AI System

This document describes how to set up and use the Slack integration for the Jarvis AI system.

## Overview

The Slack integration allows Jarvis to:
- Monitor messages in specified Slack channels and DMs
- Forward messages to the existing API server
- Send responses back to Slack
- Maintain proper threading and channel context
- Handle mentions, slash commands, and reactions

## Features

### Message Handling
- **Channel Messages**: Monitor all messages in configured channels
- **Direct Messages**: Handle private conversations with the bot
- **Threaded Replies**: Maintain conversation context in threads
- **Mentions**: Respond when mentioned with @Jarvis
- **Slash Commands**: Handle /jarvis commands

### Integration Points
- **API Server**: Forwards messages to existing `/api/jarvis/chat` endpoint
- **Gmail/Calendar**: Inherits existing email and calendar analysis
- **Vertex AI**: Uses the same Claude model for responses

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Create Slack App

1. Go to [Slack API Apps](https://api.slack.com/apps)
2. Click "Create New App" → "From scratch"
3. Name: "Jarvis AI Assistant"
4. Select your workspace

### 3. Configure Bot Token Scopes

Go to "OAuth & Permissions" and add these scopes:

**Required Scopes:**
- `app_mentions:read` - Read mentions
- `channels:history` - Read channel messages
- `channels:read` - View channels
- `chat:write` - Send messages
- `commands` - Use slash commands
- `groups:history` - Read private channel messages
- `groups:read` - View private channels
- `im:history` - Read DMs
- `im:read` - View DMs
- `im:write` - Send DMs
- `mpim:history` - Read group DMs
- `mpim:read` - View group DMs
- `mpim:write` - Send group DMs
- `users:read` - View users
- `users:read.email` - Read user emails

### 4. Install App to Workspace

1. Go to "Install App"
2. Click "Install to Workspace"
3. Copy the "Bot User OAuth Token" (starts with `xoxb-`)

### 5. Configure Socket Mode

1. Go to "Basic Information"
2. Under "App-Level Tokens", click "Generate Token and Scopes"
3. Add scope: `connections:write`
4. Copy the "App-Level Token" (starts with `xapp-`)

### 6. Configure Event Subscriptions

1. Go to "Event Subscriptions"
2. Enable Events
3. Add these Bot Events:
   - `app_mention`
   - `message.channels`
   - `message.groups`
   - `message.im`
   - `message.mpim`
   - `reaction_added`

### 7. Configure Slash Commands

1. Go to "Slash Commands"
2. Click "Create New Command"
3. Command: `/jarvis`
4. Description: "Ask Jarvis AI Assistant"
5. Usage Hint: "your question or request"

### 8. Set Environment Variables

Add to your `.env` file:

```env
# Slack Configuration
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_APP_TOKEN=xapp-your-app-token-here
API_SERVER_URL=http://localhost:5000

# Optional: Restrict to specific channels
SLACK_ALLOWED_CHANNELS=C1234567890,C0987654321
```

## Usage

### Starting the System

#### Option 1: Use the startup script
```bash
python3 start_jarvis_system.py
```

#### Option 2: Start components separately
```bash
# Terminal 1: Start API server
python3 api_server.py

# Terminal 2: Start Slack bot
python3 slack_bot.py
```

### Testing the Integration

1. **Mention the bot**: `@Jarvis hello`
2. **Use slash command**: `/jarvis what's the weather?`
3. **Send DM**: Direct message the bot
4. **React with 👋**: Wave reaction triggers response

### API Integration

The Slack bot forwards messages to the existing API server:

```json
POST /api/jarvis/chat
{
  "message": "User's message",
  "slack_context": {
    "user_id": "U1234567890",
    "channel_id": "C1234567890",
    "thread_ts": "1234567890.123456",
    "timestamp": "2025-08-05T22:30:00"
  }
}
```

## Configuration Options

### Channel Restrictions

Control which channels the bot monitors:

```env
# Allow all channels (default)
SLACK_ALLOWED_CHANNELS=

# Restrict to specific channels
SLACK_ALLOWED_CHANNELS=C1234567890,C0987654321
```

### API Server URL

Configure the API server location:

```env
# Local development
API_SERVER_URL=http://localhost:5000

# Production
API_SERVER_URL=https://your-api-server.com
```

## Troubleshooting

### Common Issues

1. **Bot not responding**
   - Check if API server is running
   - Verify Slack tokens are correct
   - Check bot permissions in workspace

2. **Missing scopes**
   - Ensure all required scopes are added
   - Reinstall app to workspace after adding scopes

3. **Socket mode connection failed**
   - Verify `SLACK_APP_TOKEN` starts with `xapp-`
   - Check app-level token has `connections:write` scope

4. **Messages not being processed**
   - Check if bot is invited to channels
   - Verify event subscriptions are enabled
   - Check channel restrictions in `SLACK_ALLOWED_CHANNELS`

### Debug Mode

Enable detailed logging:

```python
# In slack_bot.py
logging.basicConfig(level=logging.DEBUG)
```

### Testing Configuration

Run the setup test:

```bash
python3 setup_slack_bot.py
```

## Security Considerations

1. **Token Security**: Never commit tokens to version control
2. **Channel Access**: Use `SLACK_ALLOWED_CHANNELS` to restrict access
3. **Rate Limiting**: Be aware of Slack API rate limits
4. **Error Handling**: Bot gracefully handles API failures

## Architecture

```
Slack → slack_bot.py → api_server.py → Vertex AI → Response
```

The integration maintains the existing architecture while adding Slack as an input/output interface.

## Files

- `slack_bot.py` - Main Slack bot service
- `setup_slack_bot.py` - Configuration and testing
- `start_jarvis_system.py` - System startup script
- `slack_config_template.env` - Configuration template
- `SLACK_INTEGRATION.md` - This documentation 