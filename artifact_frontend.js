// Artifact System Frontend Component
// This simulates a React component for the email management artifact system

class ArtifactSystem {
    constructor() {
        this.state = {
            artifacts: [],
            currentArtifact: null,
            loading: false,
            error: null
        };
        
        this.apiBase = 'http://localhost:5001/api';
        this.subscribers = [];
    }
    
    // State management
    setState(newState) {
        this.state = { ...this.state, ...newState };
        this.notifySubscribers();
    }
    
    subscribe(callback) {
        this.subscribers.push(callback);
    }
    
    notifySubscribers() {
        this.subscribers.forEach(callback => callback(this.state));
    }
    
    // API calls
    async analyzeEmails() {
        this.setState({ loading: true, error: null });
        
        try {
            const response = await fetch(`${this.apiBase}/artifacts/analyze-emails`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Get the created artifact
                const artifactResponse = await fetch(`${this.apiBase}/artifacts/${data.artifact_id}`);
                const artifactData = await artifactResponse.json();
                
                if (artifactData.success) {
                    this.setState({
                        currentArtifact: artifactData.artifact,
                        loading: false
                    });
                }
                
                return data.message;
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            this.setState({ 
                loading: false, 
                error: error.message 
            });
            throw error;
        }
    }
    
    async getArtifact(artifactId) {
        try {
            const response = await fetch(`${this.apiBase}/artifacts/${artifactId}`);
            const data = await response.json();
            
            if (data.success) {
                this.setState({ currentArtifact: data.artifact });
                return data.artifact;
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            this.setState({ error: error.message });
            throw error;
        }
    }
    
    async updateDraft(artifactId, draftId, content) {
        try {
            const response = await fetch(`${this.apiBase}/artifacts/${artifactId}/drafts/${draftId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content })
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Refresh the artifact data
                await this.getArtifact(artifactId);
                return true;
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            this.setState({ error: error.message });
            throw error;
        }
    }
    
    async sendDraft(artifactId, draftId) {
        try {
            const response = await fetch(`${this.apiBase}/artifacts/${artifactId}/drafts/${draftId}/send`, {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Refresh the artifact data
                await this.getArtifact(artifactId);
                return true;
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            this.setState({ error: error.message });
            throw error;
        }
    }
    
    async markEmailComplete(artifactId, emailId) {
        try {
            const response = await fetch(`${this.apiBase}/artifacts/${artifactId}/emails/${emailId}/complete`, {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Refresh the artifact data
                await this.getArtifact(artifactId);
                return true;
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            this.setState({ error: error.message });
            throw error;
        }
    }
    
    async listArtifacts() {
        try {
            const response = await fetch(`${this.apiBase}/artifacts`);
            const data = await response.json();
            
            if (data.success) {
                this.setState({ artifacts: data.artifacts });
                return data.artifacts;
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            this.setState({ error: error.message });
            throw error;
        }
    }
}

// React-style component for email artifact
class EmailArtifactComponent {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.artifactSystem = new ArtifactSystem();
        this.currentArtifact = null;
        
        this.init();
    }
    
    init() {
        this.artifactSystem.subscribe((state) => {
            this.render(state);
        });
        
        this.render(this.artifactSystem.state);
    }
    
    async handleEmailAnalysis() {
        try {
            const message = await this.artifactSystem.analyzeEmails();
            console.log(message);
        } catch (error) {
            console.error('Error analyzing emails:', error);
        }
    }
    
    async handleDraftUpdate(artifactId, draftId, content) {
        try {
            await this.artifactSystem.updateDraft(artifactId, draftId, content);
        } catch (error) {
            console.error('Error updating draft:', error);
        }
    }
    
    async handleSendDraft(artifactId, draftId) {
        try {
            const success = await this.artifactSystem.sendDraft(artifactId, draftId);
            if (success) {
                console.log('Email sent successfully');
            }
        } catch (error) {
            console.error('Error sending draft:', error);
        }
    }
    
    async handleMarkComplete(artifactId, emailId) {
        try {
            await this.artifactSystem.markEmailComplete(artifactId, emailId);
        } catch (error) {
            console.error('Error marking email complete:', error);
        }
    }
    
    render(state) {
        const { currentArtifact, loading, error } = state;
        
        if (loading) {
            this.container.innerHTML = '<div class="loading">Analyzing emails...</div>';
            return;
        }
        
        if (error) {
            this.container.innerHTML = `<div class="error">Error: ${error}</div>`;
            return;
        }
        
        if (!currentArtifact) {
            this.container.innerHTML = `
                <div class="email-artifact">
                    <h3>Email Management</h3>
                    <button onclick="emailComponent.handleEmailAnalysis()">Analyze Emails</button>
                </div>
            `;
            return;
        }
        
        // Render email artifact
        const emails = currentArtifact.data.emails || [];
        const drafts = currentArtifact.data.drafts || {};
        const handledEmails = currentArtifact.data.handled_emails || [];
        
        this.container.innerHTML = `
            <div class="email-artifact">
                <div class="artifact-header">
                    <h3>${currentArtifact.title}</h3>
                    <div class="artifact-stats">
                        <span>${emails.length} emails</span>
                        <span>${Object.keys(drafts).length} drafts</span>
                        <span>${handledEmails.length} handled</span>
                    </div>
                </div>
                
                <div class="email-list">
                    ${emails.map(email => this.renderEmail(email, drafts, handledEmails)).join('')}
                </div>
                
                <div class="draft-list">
                    <h4>Drafts</h4>
                    ${Object.entries(drafts).map(([draftId, draft]) => this.renderDraft(draftId, draft)).join('')}
                </div>
            </div>
        `;
        
        // Add event listeners
        this.addEventListeners();
    }
    
    renderEmail(email, drafts, handledEmails) {
        const isHandled = handledEmails.includes(email.id);
        const hasDraft = Object.values(drafts).some(draft => draft.email_id === email.id);
        const draft = Object.values(drafts).find(draft => draft.email_id === email.id);
        
        return `
            <div class="email-item ${isHandled ? 'handled' : ''} ${hasDraft ? 'has-draft' : ''}">
                <div class="email-header">
                    <span class="sender">${email.sender}</span>
                    <span class="subject">${email.subject}</span>
                    <span class="priority priority-${email.priority}">P${email.priority}</span>
                    ${isHandled ? '<span class="status handled">✓ Handled</span>' : ''}
                </div>
                <div class="email-content">${email.content.substring(0, 100)}...</div>
                <div class="email-actions">
                    ${!isHandled ? `<button onclick="emailComponent.handleMarkComplete('${this.currentArtifact.id}', '${email.id}')">Mark Complete</button>` : ''}
                    ${!hasDraft ? `<button onclick="emailComponent.createDraft('${email.id}')">Create Draft</button>` : ''}
                </div>
            </div>
        `;
    }
    
    renderDraft(draftId, draft) {
        return `
            <div class="draft-item">
                <div class="draft-header">
                    <span class="to">To: ${draft.to}</span>
                    <span class="subject">${draft.subject}</span>
                    <span class="status ${draft.status}">${draft.status}</span>
                </div>
                <textarea 
                    class="draft-content" 
                    data-draft-id="${draftId}"
                    onchange="emailComponent.handleDraftUpdate('${this.currentArtifact.id}', '${draftId}', this.value)"
                >${draft.content}</textarea>
                <div class="draft-actions">
                    <button onclick="emailComponent.handleSendDraft('${this.currentArtifact.id}', '${draftId}')">Send</button>
                </div>
            </div>
        `;
    }
    
    addEventListeners() {
        // Add any additional event listeners here
    }
    
    createDraft(emailId) {
        // This would open a draft creation modal
        console.log('Create draft for email:', emailId);
    }
}

// CSS styles for the component
const styles = `
<style>
.email-artifact {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
}

.artifact-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 1px solid #eee;
}

.artifact-stats {
    display: flex;
    gap: 15px;
}

.artifact-stats span {
    background: #f5f5f5;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
}

.email-list {
    margin-bottom: 30px;
}

.email-item {
    border: 1px solid #eee;
    border-radius: 8px;
    padding: 15px;
    margin-bottom: 10px;
    background: white;
}

.email-item.handled {
    opacity: 0.6;
    background: #f9f9f9;
}

.email-item.has-draft {
    border-left: 4px solid #007bff;
}

.email-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}

.sender {
    font-weight: 600;
    color: #333;
}

.subject {
    flex: 1;
    margin: 0 10px;
    color: #666;
}

.priority {
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 11px;
    font-weight: bold;
}

.priority-9, .priority-8 {
    background: #dc3545;
    color: white;
}

.priority-7, .priority-6 {
    background: #ffc107;
    color: #333;
}

.priority-5, .priority-4 {
    background: #28a745;
    color: white;
}

.status.handled {
    color: #28a745;
    font-weight: 600;
}

.email-content {
    color: #666;
    font-size: 14px;
    line-height: 1.4;
    margin-bottom: 10px;
}

.email-actions {
    display: flex;
    gap: 10px;
}

.email-actions button {
    padding: 6px 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
    background: white;
    cursor: pointer;
    font-size: 12px;
}

.email-actions button:hover {
    background: #f5f5f5;
}

.draft-list {
    border-top: 2px solid #eee;
    padding-top: 20px;
}

.draft-item {
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 15px;
    margin-bottom: 15px;
    background: #f8f9fa;
}

.draft-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}

.draft-content {
    width: 100%;
    min-height: 100px;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-family: inherit;
    font-size: 14px;
    line-height: 1.4;
    resize: vertical;
}

.draft-actions {
    margin-top: 10px;
}

.draft-actions button {
    padding: 8px 16px;
    background: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

.draft-actions button:hover {
    background: #0056b3;
}

.loading {
    text-align: center;
    padding: 40px;
    color: #666;
}

.error {
    text-align: center;
    padding: 20px;
    color: #dc3545;
    background: #f8d7da;
    border: 1px solid #f5c6cb;
    border-radius: 4px;
}
</style>
`;

// Initialize the component
document.addEventListener('DOMContentLoaded', function() {
    // Add styles to head
    document.head.insertAdjacentHTML('beforeend', styles);
    
    // Create container if it doesn't exist
    if (!document.getElementById('email-artifact-container')) {
        const container = document.createElement('div');
        container.id = 'email-artifact-container';
        document.body.appendChild(container);
    }
    
    // Initialize component
    window.emailComponent = new EmailArtifactComponent('email-artifact-container');
}); 