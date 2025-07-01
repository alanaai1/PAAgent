@app.route('/api/dashboard')
def get_dashboard_data():
    try:
        # For now, return dummy data that matches Lovable's expectations
        return jsonify({
            "drafts_ready": 3,
            "days_runway": 45,
            "actions_needed": 5,
            "insights": [
                {
                    "title": "Regulatory Sandbox Application",
                    "description": "Review outcome and schedule compliance review",
                    "priority": "urgent"
                },
                {
                    "title": "6 Back-to-back meetings tomorrow",
                    "description": "09:00-15:00 block requires prep",
                    "priority": "high"
                }
            ],
            "last_ship": "No recent activity",
            "competitors_shipping": "Competitors shipping weekly"
        })
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500
