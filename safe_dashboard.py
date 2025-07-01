@app.route('/api/dashboard')
def get_dashboard_data():
    try:
        # Run comprehensive agent
        result = subprocess.run(['python3', 'chief_of_staff_comprehensive.py'],
                              capture_output=True, text=True, timeout=120)
        
        # Try to get JSON from GPT
        identification_prompt = f"""
        Extract actionable items from these insights and return ONLY valid JSON:
        {result.stdout}
        
        Return ONLY this JSON structure with no other text:
        {{
            "actions": [
                {{
                    "id": "unique-id",
                    "type": "email|deck|document|schedule",
                    "description": "what needs to be done",
                    "context_snippet": "relevant context from the insights",
                    "priority": 1,
                    "deadline": "when needed"
                }}
            ]
        }}
        """
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a JSON formatter. Return only valid JSON, no explanations."},
                {"role": "user", "content": identification_prompt}
            ],
            temperature=0.3
        )
        
        response_text = response.choices[0].message.content
        print(f"GPT Response: {response_text[:200]}...")  # Debug print
        
        try:
            actions = json.loads(response_text)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            actions = {"actions": []}
            print(f"JSON Parse failed, using fallback")
        
        # For now, return simplified data to test the pipeline
        return jsonify({
            "drafts_ready": len(actions.get("actions", [])),
            "days_runway": 45,
            "actions_needed": len(actions.get("actions", [])),
            "insights": [
                {
                    "title": action.get("description", "Action")[:60],
                    "description": action.get("context_snippet", ""),
                    "priority": "high" if action.get("priority", 5) <= 3 else "medium"
                }
                for action in actions.get("actions", [])[:3]
            ],
            "last_ship": "No recent activity",
            "competitors_shipping": "Weekly"
        })
        
    except Exception as e:
        print(f"Error in dashboard: {e}")
        # Return dummy data so UI still works
        return jsonify({
            "drafts_ready": 0,
            "days_runway": 45,
            "actions_needed": 0,
            "insights": [{
                "title": "Error loading insights",
                "description": str(e),
                "priority": "high"
            }],
            "last_ship": "Error",
            "competitors_shipping": "Error"
        })
