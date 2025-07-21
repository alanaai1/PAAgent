#!/usr/bin/env python3
"""
Stable CEO-Level Test
Tests Jarvis against real tech CEO expectations WITHOUT constant file modifications
"""

import requests
import time
import json
from datetime import datetime

class StableCEOTest:
    """Test Jarvis against CEO expectations without causing server instability"""
    
    def __init__(self, server_url: str = "http://localhost:5004"):
        self.server_url = server_url
        
        # REAL CEO-LEVEL TEST SCENARIOS
        self.ceo_tests = [
            {
                "name": "morning_briefing",
                "category": "Daily Operations Management", 
                "input": "Give me my morning briefing: what did you handle overnight, what 3 decisions do I need to make today, and what's the priority order for this week?",
                "ceo_expectation": "Must provide structured briefing with autonomous actions + decision priorities",
                "business_weight": 0.25
            },
            {
                "name": "sales_pipeline_management",
                "category": "Revenue Operations",
                "input": "Run my sales pipeline: progress every deal, identify stuck deals, chase leads, and give me the 3 deals that need my direct intervention with specific actions and timelines",
                "ceo_expectation": "Must actively manage pipeline with clear CEO intervention points", 
                "business_weight": 0.30
            },
            {
                "name": "strategic_intelligence",
                "category": "Strategic Intelligence",
                "input": "Analyze strategic intelligence: monitor competitors, assess market opportunities, evaluate customer patterns, and give me 2 strategic recommendations with business impact analysis",
                "ceo_expectation": "Must provide strategic insights with actionable recommendations",
                "business_weight": 0.25
            },
            {
                "name": "emergency_crisis_management", 
                "category": "Crisis Management",
                "input": "Handle this emergency: a major client is threatening to churn due to a product issue, our biggest deal is stalled because of contract terms, and we just discovered a competitor launched similar features. Give me solutions, not just problems.",
                "ceo_expectation": "Must solve problems autonomously with clear solutions and prevention",
                "business_weight": 0.20
            }
        ]
    
    def test_ceo_expectations(self):
        """Test Jarvis against CEO-level expectations"""
        
        print("🎯 STABLE CEO-LEVEL TEST")
        print("Testing Jarvis against REAL Tech CEO expectations")
        print("=" * 60)
        
        results = []
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for test in self.ceo_tests:
            print(f"\n📊 Testing: {test['name']}")
            print(f"🎯 CEO Expectation: {test['ceo_expectation']}")
            
            try:
                start_time = time.time()
                response = requests.post(
                    f"{self.server_url}/api/jarvis/chat",
                    json={
                        "message": test["input"],
                        "personality": {"conscientiousness": 90}
                    },
                    timeout=15
                )
                end_time = time.time()
                
                if response.status_code == 200:
                    data = response.json()
                    message = data.get('message', '')
                    response_time = end_time - start_time
                    
                    # CEO-LEVEL EVALUATION
                    score = self._evaluate_ceo_response(message, test, response_time)
                    
                    results.append({
                        "test": test["name"],
                        "category": test["category"],
                        "input": test["input"],
                        "output": message,
                        "response_time": response_time,
                        "score": score,
                        "ceo_expectation": test["ceo_expectation"],
                        "business_weight": test["business_weight"],
                        "success": True
                    })
                    
                    # Weight by business importance
                    weighted_score = score * test["business_weight"]
                    total_weighted_score += weighted_score
                    total_weight += test["business_weight"]
                    
                    print(f"   ✅ Response: {len(message)} chars, {response_time:.2f}s")
                    print(f"   📊 Score: {score:.2f}/1.0")
                    print(f"   🎯 CEO Assessment: {self._get_ceo_assessment(score)}")
                    
                else:
                    print(f"   ❌ HTTP Error: {response.status_code}")
                    results.append({
                        "test": test["name"],
                        "success": False,
                        "error": f"HTTP {response.status_code}"
                    })
                    
            except Exception as e:
                print(f"   ❌ Test Failed: {str(e)}")
                results.append({
                    "test": test["name"],
                    "success": False,
                    "error": str(e)
                })
        
        # OVERALL CEO ASSESSMENT
        overall_score = total_weighted_score / total_weight if total_weight > 0 else 0.0
        
        print(f"\n" + "=" * 60)
        print(f"📈 OVERALL CEO PERFORMANCE: {overall_score:.2f}/1.0")
        print(f"🎯 CEO ASSESSMENT: {self._get_overall_ceo_assessment(overall_score)}")
        
        # Detailed breakdown
        print(f"\n📊 DETAILED BREAKDOWN:")
        for result in results:
            if result.get("success"):
                print(f"   • {result['test']}: {result['score']:.2f}/1.0 - {self._get_ceo_assessment(result['score'])}")
        
        return {
            "overall_score": overall_score,
            "overall_assessment": self._get_overall_ceo_assessment(overall_score),
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
    
    def _evaluate_ceo_response(self, message: str, test: dict, response_time: float) -> float:
        """Evaluate response against CEO-level standards"""
        
        # 1. BUSINESS INTELLIGENCE DEPTH
        business_terms = [
            "revenue", "pipeline", "deal", "contract", "customer", "competitive",
            "strategic", "timeline", "action", "decision", "risk", "impact",
            "priority", "resource", "market", "opportunity", "team", "performance"
        ]
        bi_found = [term for term in business_terms if term.lower() in message.lower()]
        business_intelligence_score = min(1.0, len(bi_found) / 8)
        
        # 2. ACTIONABILITY
        action_terms = [
            "next steps", "action required", "recommend", "should", "will", "plan",
            "schedule", "contact", "follow up", "implement", "execute", "deliver"
        ]
        action_found = [term for term in action_terms if term.lower() in message.lower()]
        actionability_score = min(1.0, len(action_found) / 4)
        
        # 3. EXECUTIVE READINESS
        executive_terms = ["priority", "decision", "strategic", "impact", "timeline", "risk"]
        exec_found = [term for term in executive_terms if term.lower() in message.lower()]
        executive_readiness_score = min(1.0, len(exec_found) / 4)
        
        # 4. RESPONSE QUALITY
        quality_score = min(1.0, len(message) / 500)  # Expect substantial responses
        
        # 5. SPEED
        speed_score = 1.0 if response_time < 2.0 else max(0.0, 1.0 - (response_time - 2.0) / 5.0)
        
        # CEO-WEIGHTED SCORE
        overall_score = (
            business_intelligence_score * 0.30 +   # Business acumen
            actionability_score * 0.25 +          # Actionable recommendations
            executive_readiness_score * 0.20 +    # Executive-ready
            quality_score * 0.15 +                # Substantial content
            speed_score * 0.10                    # Fast response
        )
        
        return overall_score
    
    def _get_ceo_assessment(self, score: float) -> str:
        """Get CEO assessment for individual test"""
        if score >= 0.90:
            return "EXCELLENT - Exceeds CEO expectations"
        elif score >= 0.80:
            return "GOOD - Meets CEO standards"
        elif score >= 0.70:
            return "ACCEPTABLE - Some improvements needed"
        elif score >= 0.60:
            return "BELOW STANDARD - Significant gaps"
        else:
            return "UNACCEPTABLE - Not ready for CEO use"
    
    def _get_overall_ceo_assessment(self, score: float) -> str:
        """Get overall CEO assessment"""
        if score >= 0.90:
            return "READY FOR AUTONOMOUS CEO SUPPORT"
        elif score >= 0.80:
            return "CAPABLE OF CEO ASSISTANCE WITH OVERSIGHT"
        elif score >= 0.70:
            return "NEEDS IMPROVEMENT FOR CEO USE"
        else:
            return "NOT READY FOR CEO DELEGATION"

def main():
    """Run stable CEO-level test"""
    
    print("🤖 STABLE CEO-LEVEL TEST")
    print("Testing Jarvis against REAL Tech CEO expectations")
    print("=" * 60)
    
    tester = StableCEOTest()
    results = tester.test_ceo_expectations()
    
    print(f"\n🎯 FINAL VERDICT:")
    print(f"   Score: {results['overall_score']:.2f}/1.0")
    print(f"   Assessment: {results['overall_assessment']}")
    
    if results['overall_score'] >= 0.80:
        print(f"\n🎉 SUCCESS! Jarvis is ready for CEO-level delegation!")
    else:
        print(f"\n⚠️ Jarvis needs improvement for CEO-level use")
        print(f"   Focus areas: Business intelligence, actionability, executive readiness")

if __name__ == "__main__":
    main() 