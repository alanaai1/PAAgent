# Working example using Vertex AI gcloud auth
from vertex_claude_gcloud import VertexAIClaudeGCloud

client = VertexAIClaudeGCloud(
    project_id="aai-mobileapp",
    region="us-east5"
)

response = client.create_message(
    model="claude-3-7-sonnet",
    messages=[
        {"role": "user", "content": "Hello Claude!"}
    ],
    max_tokens=800,
    temperature=0.3
)

print(response)
