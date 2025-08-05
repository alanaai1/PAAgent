# Artifact System for Email Management

## Overview

The Artifact System provides persistent, interactive email management with real-time updates, draft creation, and status tracking. It integrates seamlessly with the existing Jarvis AI assistant to provide a comprehensive email workflow solution.

## Features

### ✅ Core Features
- **Persistent Artifacts**: Email analysis and drafts persist across sessions
- **Real-time Updates**: Live updates with subscriber notifications
- **Draft Management**: Create, edit, and send email drafts
- **Status Tracking**: Track which emails have been handled
- **Thread-safe Operations**: Concurrent access with proper locking
- **Auto-save**: Automatic persistence every 30 seconds

### ✅ Integration Features
- **Vertex AI Integration**: Uses Claude for intelligent email analysis
- **Gmail API**: Send emails and fetch important messages
- **Calendar Integration**: Context-aware email management
- **Slack Integration**: Artifact updates via Slack bot
- **REST API**: Full CRUD operations for artifacts

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Server    │    │  Artifact       │
│   (React/JS)    │◄──►│   (Flask)       │◄──►│  Manager        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │                        │
                              ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Vertex AI     │    │   JSON Storage  │
                       │   (Claude)      │    │   (artifacts.json)│
                       └─────────────────┘    └─────────────────┘
```

## Data Models

### Email
```python
@dataclass
class Email:
    id: str
    sender: str
    subject: str
    content: str
    date: str
    status: EmailStatus  # unread, read, drafted, sent, archived
    priority: int = 0
    tags: List[str] = None
    thread_id: Optional[str] = None
```

### EmailDraft
```python
@dataclass
class EmailDraft:
    id: str
    email_id: str
    to: str
    subject: str
    content: str
    created_at: str
    updated_at: str
    status: str = "draft"  # draft, ready, sent
```

### Artifact
```python
@dataclass
class Artifact:
    id: str
    type: ArtifactType  # email-list, email-draft, calendar-events, etc.
    title: str
    data: Dict[str, Any]
    created_at: str
    updated_at: str
    visible: bool = True
    metadata: Dict[str, Any] = None
```

## API Endpoints

### Email Management
- `POST /api/artifacts/analyze-emails` - Analyze emails and create artifact
- `GET /api/artifacts/<artifact_id>` - Get artifact data
- `GET /api/artifacts/<artifact_id>/summary` - Get artifact summary
- `PUT /api/artifacts/<artifact_id>/drafts/<draft_id>` - Update draft
- `POST /api/artifacts/<artifact_id>/drafts/<draft_id>/send` - Send draft
- `POST /api/artifacts/<artifact_id>/emails/<email_id>/complete` - Mark email handled
- `GET /api/artifacts` - List all artifacts
- `DELETE /api/artifacts/<artifact_id>` - Delete artifact
- `POST /api/artifacts/<artifact_id>/drafts` - Create new draft

### Chat Integration
- `POST /jarvis_chat` - Main chat endpoint with artifact integration

## Usage Examples

### 1. Analyze Emails
```python
from artifact_system import analyze_emails

# Analyze emails and create artifact
response = analyze_emails()
print(response)  # "I've found 10 important emails and created 5 drafts. See them on the right →"
```

### 2. Update Draft
```python
from artifact_system import update_draft

# Update draft content
update_draft(artifact_id, draft_id, "New draft content")
```

### 3. Send Draft
```python
from artifact_system import send_draft

# Send a draft email
success = send_draft(artifact_id, draft_id)
if success:
    print("Email sent successfully")
```

### 4. Mark Email Complete
```python
from artifact_system import mark_email_complete

# Mark email as handled
mark_email_complete(artifact_id, email_id)
```

### 5. API Integration
```javascript
// Frontend JavaScript
async function analyzeEmails() {
    const response = await fetch('/api/artifacts/analyze-emails', {
        method: 'POST'
    });
    const data = await response.json();
    console.log(data.message);
}

async function updateDraft(artifactId, draftId, content) {
    await fetch(`/api/artifacts/${artifactId}/drafts/${draftId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content })
    });
}
```

## Frontend Integration

### React-style Component
The system includes a complete frontend component (`artifact_frontend.js`) that provides:

- **Real-time Updates**: Automatic refresh when artifacts change
- **Interactive UI**: Edit drafts, mark emails complete, send emails
- **Responsive Design**: Works on desktop and mobile
- **Error Handling**: Graceful error display and recovery

### HTML Test Page
A simple test page (`artifact_test.html`) demonstrates:
- Email analysis
- Artifact listing
- API integration

## Configuration

### Environment Variables
```bash
# API Server
API_SERVER_URL=http://localhost:5000

# Vertex AI (already configured)
GOOGLE_CLOUD_PROJECT_ID=aai-mobileapp

# Gmail Integration (if using)
GMAIL_CREDENTIALS_FILE=path/to/credentials.json
```

### Storage
- **Default**: `artifacts.json` in project root
- **Custom**: Specify path in `ArtifactManager(storage_path)`
- **Auto-save**: Every 30 seconds
- **Thread-safe**: Concurrent access supported

## Testing

### Run Tests
```bash
# Test the artifact system
python3 test_artifact_system.py

# Start the API server
python3 api_server_with_artifacts.py

# Open test page
open artifact_test.html
```

### Test Features
1. **Email Analysis**: Creates artifacts with drafts
2. **Draft Management**: Update and send drafts
3. **Status Tracking**: Mark emails as handled
4. **Persistence**: Save/load artifacts from disk
5. **Real-time Updates**: Subscriber notifications
6. **API Integration**: REST endpoint testing

## Integration with Existing Systems

### Slack Bot Integration
```python
# In slack_bot.py
from artifact_system import analyze_emails

@app.event("message")
def handle_message_events(body, say, client):
    if "analyze emails" in message.lower():
        response = analyze_emails()
        say(text=response)
```

### Calendar Integration
```python
# In api_server_with_artifacts.py
def handle_email_request(user_message, slack_context):
    # Check for calendar-related emails
    if 'meeting' in user_message.lower():
        events = get_calendar_events()
        # Create artifact with calendar context
```

### Vertex AI Integration
```python
# In artifact_system.py
def generate_drafts_for_emails(self, emails: List[Email]) -> Dict[str, EmailDraft]:
    # Use Vertex AI to generate intelligent draft responses
    for email in emails:
        if email.priority >= 7:
            # Generate draft using Claude
            draft_content = self.ai_client.create_message(...)
```

## Performance Considerations

### Memory Usage
- **Artifacts**: Loaded in memory for fast access
- **Auto-save**: Prevents data loss
- **Cleanup**: Old artifacts can be archived

### Scalability
- **Thread-safe**: Supports concurrent users
- **JSON Storage**: Simple, portable format
- **API Design**: RESTful, stateless endpoints

### Monitoring
- **Logging**: Comprehensive error logging
- **Metrics**: Artifact creation, updates, sends
- **Health Checks**: API endpoint monitoring

## Security

### Data Protection
- **Local Storage**: Artifacts stored locally
- **No Sensitive Data**: Email content not logged
- **Access Control**: API endpoint protection

### Best Practices
- **Input Validation**: All API inputs validated
- **Error Handling**: Graceful error responses
- **Rate Limiting**: Prevent abuse (future enhancement)

## Future Enhancements

### Planned Features
- **Email Templates**: Reusable draft templates
- **Advanced Filtering**: Filter by sender, date, priority
- **Bulk Operations**: Handle multiple emails at once
- **Email Scheduling**: Send emails at specific times
- **Analytics Dashboard**: Usage metrics and insights

### Technical Improvements
- **Database Storage**: Replace JSON with proper database
- **WebSocket Updates**: Real-time frontend updates
- **Caching Layer**: Redis for performance
- **Microservices**: Split into separate services

## Troubleshooting

### Common Issues

1. **Artifact Not Created**
   - Check Vertex AI credentials
   - Verify Gmail API access
   - Check logs for errors

2. **Drafts Not Saving**
   - Verify file permissions
   - Check disk space
   - Review error logs

3. **API Connection Issues**
   - Ensure server is running
   - Check CORS configuration
   - Verify endpoint URLs

### Debug Commands
```bash
# Check artifact storage
cat artifacts.json

# Test API endpoints
curl http://localhost:5000/api/artifacts

# Monitor logs
tail -f api_server.log
```

## Contributing

### Development Setup
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Configure environment variables
4. Run tests: `python3 test_artifact_system.py`
5. Start server: `python3 api_server_with_artifacts.py`

### Code Style
- Follow PEP 8 for Python
- Use type hints
- Add docstrings
- Write tests for new features

---

**The Artifact System provides a robust foundation for email management with persistent storage, real-time updates, and seamless integration with existing AI assistant capabilities.** 