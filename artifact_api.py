#!/usr/bin/env python3
"""
API endpoints for the Artifact System
Provides REST API for email management artifacts
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from artifact_system import artifact_manager, analyze_emails, get_artifact_data, update_draft, send_draft, mark_email_complete
import json

app = Flask(__name__)
CORS(app)

@app.route('/api/artifacts/analyze-emails', methods=['POST'])
def analyze_emails_endpoint():
    """Analyze emails and create artifact"""
    try:
        response_message = analyze_emails()
        return jsonify({
            'success': True,
            'message': response_message,
            'artifact_id': artifact_manager.artifacts.get(list(artifact_manager.artifacts.keys())[-1]).id if artifact_manager.artifacts else None
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/artifacts/<artifact_id>', methods=['GET'])
def get_artifact_endpoint(artifact_id):
    """Get artifact data"""
    try:
        artifact_data = get_artifact_data(artifact_id)
        if artifact_data:
            return jsonify({
                'success': True,
                'artifact': artifact_data
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Artifact not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/artifacts/<artifact_id>/summary', methods=['GET'])
def get_artifact_summary_endpoint(artifact_id):
    """Get artifact summary"""
    try:
        summary = artifact_manager.get_artifact_summary(artifact_id)
        if summary:
            return jsonify({
                'success': True,
                'summary': summary
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Artifact not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/artifacts/<artifact_id>/drafts/<draft_id>', methods=['PUT'])
def update_draft_endpoint(artifact_id, draft_id):
    """Update a draft"""
    try:
        data = request.get_json()
        content = data.get('content')
        
        if not content:
            return jsonify({
                'success': False,
                'error': 'Content is required'
            }), 400
        
        update_draft(artifact_id, draft_id, content)
        
        return jsonify({
            'success': True,
            'message': 'Draft updated successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/artifacts/<artifact_id>/drafts/<draft_id>/send', methods=['POST'])
def send_draft_endpoint(artifact_id, draft_id):
    """Send a draft email"""
    try:
        success = send_draft(artifact_id, draft_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Email sent successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to send email'
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/artifacts/<artifact_id>/emails/<email_id>/complete', methods=['POST'])
def mark_email_complete_endpoint(artifact_id, email_id):
    """Mark an email as handled"""
    try:
        mark_email_complete(artifact_id, email_id)
        
        return jsonify({
            'success': True,
            'message': 'Email marked as handled'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/artifacts', methods=['GET'])
def list_artifacts_endpoint():
    """List all artifacts"""
    try:
        artifacts = []
        for artifact_id, artifact in artifact_manager.artifacts.items():
            summary = artifact_manager.get_artifact_summary(artifact_id)
            if summary:
                artifacts.append(summary)
        
        return jsonify({
            'success': True,
            'artifacts': artifacts
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/artifacts/<artifact_id>', methods=['DELETE'])
def delete_artifact_endpoint(artifact_id):
    """Delete an artifact"""
    try:
        if artifact_id in artifact_manager.artifacts:
            del artifact_manager.artifacts[artifact_id]
            return jsonify({
                'success': True,
                'message': 'Artifact deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Artifact not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/artifacts/<artifact_id>/drafts', methods=['POST'])
def create_draft_endpoint(artifact_id):
    """Create a new draft"""
    try:
        data = request.get_json()
        email_id = data.get('email_id')
        to = data.get('to')
        subject = data.get('subject')
        content = data.get('content')
        
        if not all([email_id, to, subject, content]):
            return jsonify({
                'success': False,
                'error': 'email_id, to, subject, and content are required'
            }), 400
        
        draft_id = artifact_manager.create_email_draft(artifact_id, email_id, to, subject, content)
        
        if draft_id:
            return jsonify({
                'success': True,
                'draft_id': draft_id,
                'message': 'Draft created successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to create draft'
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001) 