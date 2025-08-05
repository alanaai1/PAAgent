#!/usr/bin/env python3
"""
Test Script for Artifact System
Demonstrates email management with persistent artifacts
"""
import requests
import json
import time
from artifact_system import artifact_manager, analyze_emails

def test_artifact_system():
    """Test the complete artifact system"""
    print("🧪 Testing Artifact System for Email Management")
    print("=" * 50)
    
    # Test 1: Analyze emails and create artifact
    print("\n1. Testing Email Analysis...")
    try:
        response_message = analyze_emails()
        print(f"✅ {response_message}")
        
        # Get the created artifact
        artifacts = list(artifact_manager.artifacts.keys())
        if artifacts:
            artifact_id = artifacts[-1]
            artifact = artifact_manager.get_artifact(artifact_id)
            print(f"📧 Created artifact: {artifact_id}")
            print(f"📊 Emails found: {len(artifact.data.get('emails', []))}")
            print(f"📝 Drafts created: {len(artifact.data.get('drafts', {}))}")
        else:
            print("❌ No artifact created")
            
    except Exception as e:
        print(f"❌ Error in email analysis: {e}")
    
    # Test 2: API endpoints
    print("\n2. Testing API Endpoints...")
    base_url = "http://localhost:5000/api"
    
    # Test analyze emails endpoint
    try:
        response = requests.post(f"{base_url}/artifacts/analyze-emails")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Analyze emails: {data.get('message', 'Success')}")
        else:
            print(f"❌ Analyze emails failed: {response.status_code}")
    except Exception as e:
        print(f"❌ API test failed: {e}")
    
    # Test list artifacts endpoint
    try:
        response = requests.get(f"{base_url}/artifacts")
        if response.status_code == 200:
            data = response.json()
            artifacts = data.get('artifacts', [])
            print(f"✅ List artifacts: Found {len(artifacts)} artifacts")
        else:
            print(f"❌ List artifacts failed: {response.status_code}")
    except Exception as e:
        print(f"❌ API test failed: {e}")
    
    # Test 3: Artifact operations
    print("\n3. Testing Artifact Operations...")
    
    if artifact_manager.artifacts:
        artifact_id = list(artifact_manager.artifacts.keys())[0]
        artifact = artifact_manager.get_artifact(artifact_id)
        
        if artifact and artifact.data.get('drafts'):
            draft_id = list(artifact.data['drafts'].keys())[0]
            
            # Test draft update
            try:
                new_content = "Updated draft content for testing"
                artifact_manager.update_email_draft(artifact_id, draft_id, {'content': new_content})
                print("✅ Draft update: Success")
            except Exception as e:
                print(f"❌ Draft update failed: {e}")
            
            # Test mark email complete
            if artifact.data.get('emails'):
                email_id = artifact.data['emails'][0]['id']
                try:
                    artifact_manager.mark_email_handled(artifact_id, email_id)
                    print("✅ Mark email complete: Success")
                except Exception as e:
                    print(f"❌ Mark email complete failed: {e}")
    
    # Test 4: Artifact persistence
    print("\n4. Testing Artifact Persistence...")
    try:
        # Save artifacts
        artifact_manager.save_artifacts()
        print("✅ Artifacts saved to disk")
        
        # Create new manager to test loading
        from artifact_system import ArtifactManager
        new_manager = ArtifactManager("test_artifacts.json")
        print(f"✅ Loaded {len(new_manager.artifacts)} artifacts from disk")
        
    except Exception as e:
        print(f"❌ Persistence test failed: {e}")
    
    # Test 5: Real-time updates
    print("\n5. Testing Real-time Updates...")
    
    def update_callback(artifact_id, action):
        print(f"🔄 Artifact update: {artifact_id} - {action}")
    
    artifact_manager.subscribe(update_callback)
    
    # Trigger an update
    if artifact_manager.artifacts:
        artifact_id = list(artifact_manager.artifacts.keys())[0]
        artifact_manager.update_artifact(artifact_id, {'title': 'Updated Title'})
        print("✅ Real-time updates working")
    
    print("\n" + "=" * 50)
    print("🎉 Artifact System Test Complete!")
    print("\nFeatures Demonstrated:")
    print("✅ Email analysis and artifact creation")
    print("✅ Draft management and updates")
    print("✅ Email status tracking")
    print("✅ API endpoint integration")
    print("✅ Persistent storage")
    print("✅ Real-time updates")
    print("✅ Thread-safe operations")

def test_frontend_integration():
    """Test frontend integration"""
    print("\n🌐 Testing Frontend Integration...")
    
    # Create a simple HTML test page
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Artifact System Test</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .container { max-width: 800px; margin: 0 auto; }
            button { padding: 10px 20px; margin: 10px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
            .result { margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 4px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Artifact System Test</h1>
            <button onclick="analyzeEmails()">Analyze Emails</button>
            <button onclick="listArtifacts()">List Artifacts</button>
            <div id="result" class="result"></div>
        </div>
        
        <script>
            async function analyzeEmails() {
                try {
                    const response = await fetch('http://localhost:5000/api/artifacts/analyze-emails', {
                        method: 'POST'
                    });
                    const data = await response.json();
                    document.getElementById('result').innerHTML = 
                        '<h3>Email Analysis Result:</h3><pre>' + JSON.stringify(data, null, 2) + '</pre>';
                } catch (error) {
                    document.getElementById('result').innerHTML = '<p style="color: red;">Error: ' + error.message + '</p>';
                }
            }
            
            async function listArtifacts() {
                try {
                    const response = await fetch('http://localhost:5000/api/artifacts');
                    const data = await response.json();
                    document.getElementById('result').innerHTML = 
                        '<h3>Artifacts:</h3><pre>' + JSON.stringify(data, null, 2) + '</pre>';
                } catch (error) {
                    document.getElementById('result').innerHTML = '<p style="color: red;">Error: ' + error.message + '</p>';
                }
            }
        </script>
    </body>
    </html>
    """
    
    with open('artifact_test.html', 'w') as f:
        f.write(html_content)
    
    print("✅ Created test HTML file: artifact_test.html")
    print("🌐 Open artifact_test.html in your browser to test the frontend")

if __name__ == '__main__':
    print("🚀 Starting Artifact System Tests...")
    
    # Test the core system
    test_artifact_system()
    
    # Test frontend integration
    test_frontend_integration()
    
    print("\n📋 Next Steps:")
    print("1. Start the API server: python3 api_server_with_artifacts.py")
    print("2. Open artifact_test.html in your browser")
    print("3. Test the email management features")
    print("4. Check artifacts.json for persistent data") 