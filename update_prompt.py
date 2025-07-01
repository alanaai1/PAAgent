import re

# Read the current file
with open('clean_two_layer_api.py', 'r') as f:
    content = f.read()

# New prompt that forces concrete output
new_prompt = '''identification_prompt = f"""
Analyze these insights and create ACTUAL DELIVERABLES (not suggestions):

{result.stdout}

For each actionable item, CREATE THE ACTUAL WORK PRODUCT:
- If email needed: Write the complete email (subject, body, recipient)
- If document needed: Write the full document with all content
- If meeting prep needed: Create the complete brief with questions and answers
- If schedule needed: Write the calendar invite with agenda

NO PLACEHOLDERS. NO "insert here". NO meta-advice.
ACTUAL DELIVERABLES ONLY.

Return JSON:
{{
    "actions": [
        {{
            "id": "unique-id",
            "type": "email|document|brief|schedule",
            "title": "What was created (max 60 chars)",
            "description": "Brief description of the deliverable",
            "context_snippet": "Why this matters strategically",
            "priority": 1-10,
            "deadline": "when needed",
            "deliverable": "THE ACTUAL COMPLETE WORK PRODUCT - full email/document/brief content"
        }}
    ]
}}
"""'''

# Replace the old prompt
content = re.sub(
    r'identification_prompt = f""".*?"""',
    new_prompt,
    content,
    flags=re.DOTALL
)

# Write back
with open('clean_two_layer_api.py', 'w') as f:
    f.write(content)

print("✅ Updated prompt to generate concrete deliverables")
