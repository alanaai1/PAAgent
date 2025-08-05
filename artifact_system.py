#!/usr/bin/env python3
"""
Artifact System for Email Management
Provides persistent, interactive email handling with drafts and tracking
"""
import os
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import time

class ArtifactType(Enum):
    EMAIL_LIST = "email-list"
    EMAIL_DRAFT = "email-draft"
    CALENDAR_EVENTS = "calendar-events"
    TASK_LIST = "task-list"
    DOCUMENT = "document"

class EmailStatus(Enum):
    UNREAD = "unread"
    READ = "read"
    DRAFTED = "drafted"
    SENT = "sent"
    ARCHIVED = "archived"

@dataclass
class Email:
    id: str
    sender: str
    subject: str
    content: str
    date: str
    status: EmailStatus
    priority: int = 0
    tags: List[str] = None
    thread_id: Optional[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []

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
    
    def to_dict(self):
        return asdict(self)

@dataclass
class Artifact:
    id: str
    type: ArtifactType
    title: str
    data: Dict[str, Any]
    created_at: str
    updated_at: str
    visible: bool = True
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class ArtifactManager:
    """Manages persistent artifacts with real-time updates"""
    
    def __init__(self, storage_path: str = "artifacts.json"):
        self.storage_path = storage_path
        self.artifacts: Dict[str, Artifact] = {}
        self.lock = threading.Lock()
        self.subscribers: List[callable] = []
        
        # Load existing artifacts
        self.load_artifacts()
        
        # Start auto-save thread
        self.auto_save_thread = threading.Thread(target=self._auto_save_loop, daemon=True)
        self.auto_save_thread.start()
    
    def load_artifacts(self):
        """Load artifacts from storage"""
        try:
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    for artifact_id, artifact_data in data.items():
                        artifact_data['type'] = ArtifactType(artifact_data['type'])
                        self.artifacts[artifact_id] = Artifact(**artifact_data)
        except Exception as e:
            print(f"Error loading artifacts: {e}")
    
    def save_artifacts(self):
        """Save artifacts to storage"""
        try:
            with self.lock:
                data = {}
                for artifact_id, artifact in self.artifacts.items():
                    artifact_dict = asdict(artifact)
                    artifact_dict['type'] = artifact.type.value
                    data[artifact_id] = artifact_dict
                
                with open(self.storage_path, 'w') as f:
                    json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving artifacts: {e}")
    
    def _auto_save_loop(self):
        """Auto-save artifacts every 30 seconds"""
        while True:
            time.sleep(30)
            self.save_artifacts()
    
    def subscribe(self, callback: callable):
        """Subscribe to artifact updates"""
        self.subscribers.append(callback)
    
    def notify_subscribers(self, artifact_id: str, action: str):
        """Notify subscribers of artifact changes"""
        for callback in self.subscribers:
            try:
                callback(artifact_id, action)
            except Exception as e:
                print(f"Error in subscriber callback: {e}")
    
    def create_email_list_artifact(self, emails: List[Email], title: str = "Email Analysis") -> str:
        """Create an email list artifact"""
        artifact_id = str(uuid.uuid4())
        
        # Convert emails to dict format
        emails_data = []
        for email in emails:
            email_dict = asdict(email)
            email_dict['status'] = email.status.value
            emails_data.append(email_dict)
        
        artifact = Artifact(
            id=artifact_id,
            type=ArtifactType.EMAIL_LIST,
            title=title,
            data={
                'emails': emails_data,
                'drafts': {},
                'handled_emails': [],
                'filters': {
                    'status': [],
                    'priority': [],
                    'sender': []
                }
            },
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        with self.lock:
            self.artifacts[artifact_id] = artifact
        
        self.notify_subscribers(artifact_id, "created")
        return artifact_id
    
    def get_artifact(self, artifact_id: str) -> Optional[Artifact]:
        """Get an artifact by ID"""
        return self.artifacts.get(artifact_id)
    
    def update_artifact(self, artifact_id: str, updates: Dict[str, Any]):
        """Update an artifact"""
        if artifact_id in self.artifacts:
            with self.lock:
                artifact = self.artifacts[artifact_id]
                for key, value in updates.items():
                    if hasattr(artifact, key):
                        setattr(artifact, key, value)
                artifact.updated_at = datetime.now().isoformat()
            
            self.notify_subscribers(artifact_id, "updated")
    
    def create_email_draft(self, artifact_id: str, email_id: str, to: str, subject: str, content: str) -> str:
        """Create an email draft"""
        draft_id = str(uuid.uuid4())
        draft = EmailDraft(
            id=draft_id,
            email_id=email_id,
            to=to,
            subject=subject,
            content=content,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        artifact = self.get_artifact(artifact_id)
        if artifact and artifact.type == ArtifactType.EMAIL_LIST:
            with self.lock:
                artifact.data['drafts'][draft_id] = asdict(draft)
                artifact.updated_at = datetime.now().isoformat()
            
            self.notify_subscribers(artifact_id, "draft_created")
            return draft_id
        
        return None
    
    def update_email_draft(self, artifact_id: str, draft_id: str, updates: Dict[str, Any]):
        """Update an email draft"""
        artifact = self.get_artifact(artifact_id)
        if artifact and draft_id in artifact.data.get('drafts', {}):
            with self.lock:
                draft_data = artifact.data['drafts'][draft_id]
                draft_data.update(updates)
                draft_data['updated_at'] = datetime.now().isoformat()
                artifact.updated_at = datetime.now().isoformat()
            
            self.notify_subscribers(artifact_id, "draft_updated")
    
    def mark_email_handled(self, artifact_id: str, email_id: str):
        """Mark an email as handled"""
        artifact = self.get_artifact(artifact_id)
        if artifact:
            with self.lock:
                if email_id not in artifact.data.get('handled_emails', []):
                    artifact.data.setdefault('handled_emails', []).append(email_id)
                    artifact.updated_at = datetime.now().isoformat()
            
            self.notify_subscribers(artifact_id, "email_handled")
    
    def send_email_draft(self, artifact_id: str, draft_id: str, gmail_service=None):
        """Send an email draft"""
        artifact = self.get_artifact(artifact_id)
        if not artifact or draft_id not in artifact.data.get('drafts', {}):
            return False
        
        draft_data = artifact.data['drafts'][draft_id]
        
        try:
            if gmail_service:
                # Create the email message
                message = {
                    'to': draft_data['to'],
                    'subject': draft_data['subject'],
                    'body': draft_data['content']
                }
                
                # Send via Gmail API
                # This would integrate with your existing Gmail service
                # gmail_service.send_message(message)
                
                # Update draft status
                with self.lock:
                    draft_data['status'] = 'sent'
                    draft_data['updated_at'] = datetime.now().isoformat()
                    artifact.updated_at = datetime.now().isoformat()
                
                self.notify_subscribers(artifact_id, "email_sent")
                return True
            else:
                print("Gmail service not available")
                return False
                
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def get_important_emails(self, hours: int = 72) -> List[Email]:
        """Get important emails from the last N hours"""
        # This would integrate with your existing email fetching
        # For now, return mock data
        return [
            Email(
                id="email_1",
                sender="john@company.com",
                subject="Q4 Revenue Report",
                content="Please review the attached Q4 revenue report...",
                date=datetime.now().isoformat(),
                status=EmailStatus.UNREAD,
                priority=9
            ),
            Email(
                id="email_2", 
                sender="client@bigcorp.com",
                subject="Contract Renewal Discussion",
                content="We'd like to discuss renewing our contract...",
                date=datetime.now().isoformat(),
                status=EmailStatus.UNREAD,
                priority=8
            )
        ]
    
    def generate_drafts_for_emails(self, emails: List[Email]) -> Dict[str, EmailDraft]:
        """Generate draft responses for emails"""
        drafts = {}
        
        for email in emails:
            if email.priority >= 7:  # Only draft for high priority emails
                draft_id = str(uuid.uuid4())
                draft = EmailDraft(
                    id=draft_id,
                    email_id=email.id,
                    to=email.sender,
                    subject=f"Re: {email.subject}",
                    content=f"Thank you for your email regarding {email.subject}. I'll review this and get back to you shortly.",
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat()
                )
                drafts[draft_id] = draft
        
        return drafts
    
    def handle_email_analysis(self) -> str:
        """Main handler for email analysis - returns response message"""
        # Get important emails
        important_emails = self.get_important_emails()
        
        # Generate drafts
        drafts = self.generate_drafts_for_emails(important_emails)
        
        # Create artifact
        artifact_id = self.create_email_list_artifact(important_emails, "Important Email Analysis")
        
        # Add drafts to artifact
        artifact = self.get_artifact(artifact_id)
        if artifact:
            with self.lock:
                artifact.data['drafts'] = {k: asdict(v) for k, v in drafts.items()}
                artifact.updated_at = datetime.now().isoformat()
        
        self.notify_subscribers(artifact_id, "analysis_complete")
        
        return f"I've found {len(important_emails)} important emails and created {len(drafts)} drafts. See them on the right →"
    
    def get_artifact_summary(self, artifact_id: str) -> Dict[str, Any]:
        """Get a summary of an artifact for display"""
        artifact = self.get_artifact(artifact_id)
        if not artifact:
            return {}
        
        if artifact.type == ArtifactType.EMAIL_LIST:
            emails = artifact.data.get('emails', [])
            drafts = artifact.data.get('drafts', {})
            handled = artifact.data.get('handled_emails', [])
            
            return {
                'id': artifact_id,
                'type': 'email-list',
                'title': artifact.title,
                'email_count': len(emails),
                'draft_count': len(drafts),
                'handled_count': len(handled),
                'unhandled_count': len(emails) - len(handled),
                'created_at': artifact.created_at,
                'updated_at': artifact.updated_at
            }
        
        return {}

# Global artifact manager instance
artifact_manager = ArtifactManager()

# Example usage functions
def analyze_emails() -> str:
    """Analyze emails and create artifact"""
    return artifact_manager.handle_email_analysis()

def get_artifact_data(artifact_id: str) -> Dict[str, Any]:
    """Get artifact data for frontend"""
    artifact = artifact_manager.get_artifact(artifact_id)
    if artifact:
        return asdict(artifact)
    return {}

def update_draft(artifact_id: str, draft_id: str, content: str):
    """Update a draft's content"""
    artifact_manager.update_email_draft(artifact_id, draft_id, {'content': content})

def send_draft(artifact_id: str, draft_id: str) -> bool:
    """Send a draft email"""
    return artifact_manager.send_email_draft(artifact_id, draft_id)

def mark_email_complete(artifact_id: str, email_id: str):
    """Mark an email as handled"""
    artifact_manager.mark_email_handled(artifact_id, email_id) 