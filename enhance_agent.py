# Add this to your chief_of_staff_comprehensive.py
# This extracts specific actions from the insights

import re
import json

def extract_actionable_items(chief_output):
    """Extract specific actions that can be automated"""
    actions = []
    
    # Look for email actions
    email_patterns = [
        r'[Ee]mail\s+(\w+\s+\w+)',
        r'[Rr]eply\s+to\s+(\w+)',
        r'[Ss]end\s+.*?\s+to\s+(\w+)',
        r'[Ff]ollow[\s-]?up\s+with\s+(\w+)'
    ]
    
    # Look for document updates
    doc_patterns = [
        r'[Uu]pdate\s+(.*?)\s+doc',
        r'[Aa]dd\s+to\s+(.*?)\s+document',
        r'[Ff]inalize\s+(.*?)\s+slides'
    ]
    
    lines = chief_output.split('\n')
    for line in lines:
        # Check for email actions
        for pattern in email_patterns:
            match = re.search(pattern, line)
            if match:
                actions.append({
                    'type': 'email',
                    'recipient': match.group(1),
                    'context': line,
                    'raw_line': line
                })
        
        # Check for document actions
        for pattern in doc_patterns:
            match = re.search(pattern, line)
            if match:
                actions.append({
                    'type': 'document',
                    'target': match.group(1),
                    'context': line,
                    'raw_line': line
                })
    
    return actions

# Test it
test_output = """
Email Siji Soluade about FCA sandbox updates
Update AAI Feedback Tracker doc with latest metrics
Reply to Tim Walton regarding demo preparation
"""

actions = extract_actionable_items(test_output)
print(json.dumps(actions, indent=2))
