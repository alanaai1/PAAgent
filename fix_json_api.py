@app.route('/api/dashboard')
def get_dashboard_data():
    # Run comprehensive agent
    result = subprocess.run(['python3', 'chief_of_staff_comprehensive.py'],
                          capture_output=True, text=True, timeout=300)
    
    # Use OpenAI to structure the output AS JSON
    response = client.chat.completions.create(
        model="gpt-4o",  # or gpt-4
        messages=[{
            "role": "system",
            "content": "You are a JSON formatter. Always return valid JSON only."
        }, {
            "role": "user",
            "content": f"""
            Convert this chief of staff analysis into JSON:
            {result.stdout}
            
            Return ONLY valid JSON in this exact format:
            {{
                "drafts_ready": <number>,
                "days_runway": <number>,
                "actions_needed": <number>,
                "insights": [
                    {{
                        "title": "<short title>",
                        "description": "<full description>",
                        "priority": "urgent|high|medium|low"
                    }}
                ],
                "key_opportunities": [
                    {{
                        "company": "<name>",
                        "action": "<what to do>",
                        "value": <estimated value>
                    }}
                ]
            }}
            """
        }],
        response_format={"type": "json_object"},  # FORCES valid JSON
        temperature=0.3
    )
    
    try:
        data = json.loads(response.choices[0].message.content)
        
        # Transform for Lovable's expected format
        opportunities = []
        for i, opp in enumerate(data.get('key_opportunities', [])):
            opportunities.append({
                "id": f"opp-{i}",
                "company": opp['company'],
                "amount": opp.get('value', 50000),
                "stage": "active",
                "action_preview": opp['action'],
                "confidence": 0.9
            })
        
        return jsonify({
            "drafts_ready": data.get('drafts_ready', 0),
            "days_runway": data.get('days_runway', 45),
            "actions_needed": data.get('actions_needed', 0),
            "insights": data.get('insights', []),
            "opportunities": opportunities,
            "last_ship": "No recent activity",
            "competitors_shipping": "Weekly"
        })
        
    except Exception as e:
        print(f"JSON Parse Error: {e}")
        # Fallback to dummy data if parsing fails
        return jsonify({
            "drafts_ready": 0,
            "days_runway": 45,
            "actions_needed": 1,
            "insights": [{
                "title": "Error parsing AI output",
                "description": str(e),
                "priority": "high"
            }]
        })
