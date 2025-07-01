# Update your comprehensive agent to output structured insights

def enhance_with_ai_categories(raw_insights):
    """Let AI decide what type of action each insight needs"""
    
    prompt = f"""
    For each of these insights, categorize what type of response would be most valuable:
    
    {raw_insights}
    
    Categories can include (but aren't limited to):
    - draft_email: AI should draft an email
    - strategic_analysis: AI should provide deeper strategic thinking
    - warning: AI is warning about wasted time/resources
    - opportunity: AI spotted an opportunity to explore
    - pattern_recognition: AI noticed a pattern worth highlighting
    - automation_candidate: This could be automated
    - delegation_suggestion: This should be delegated
    - stop_doing: AI suggests stopping this activity
    - immediate_action: Urgent, needs doing now
    - think_piece: Requires reflection, not action
    
    For each insight, provide:
    1. Category
    2. Why this category
    3. Suggested next step (could be draft, analysis, warning, etc.)
    
    Format as JSON array.
    """
    
    # This lets AI think freely about what each insight really needs
    return ai_response

# Example outputs:
# "Email Siji about FCA" → category: "draft_email"
# "You've met Bob 5 times with no outcomes" → category: "warning"  
# "Competitor raised $50M" → category: "strategic_analysis"
# "Three customers asked about same feature" → category: "pattern_recognition"
