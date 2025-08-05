#!/usr/bin/env python3
"""
Test script to ask Claude about Nepal's capital
"""
from vertex_claude_gcloud import VertexAIClaudeGCloud

# Initialize the client
client = VertexAIClaudeGCloud(
    project_id="aai-mobileapp",
    region="us-east5"
)

# Ask about Nepal's capital
response = client.create_message(
    model="claude-3-7-sonnet",
    messages=[
        {"role": "user", "content": "What is the capital of Nepal?"}
    ],
    max_tokens=200,
    temperature=0.3
)

print("Question: What is the capital of Nepal?")
print("Response:", response) 