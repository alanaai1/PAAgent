import openai
import os

client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def test_concrete_output():
    # Test current output vs concrete output
    basic_insight = "Send VAT receipt update to Alan about bonus processing."
    
    concrete_insight = """
Subject: Q2 VAT Documentation - Action Required for Bonus Processing

Hi Alan,

Our Q2 bonus payments ($47K total) are blocked pending VAT receipt collection. 

Current status:
- 3 receipts outstanding from vendors
- Finance close deadline: June 15
- Bonus payment scheduled: June 18

Action needed: Can you chase the missing receipts today? I've attached the vendor contact list with amounts outstanding.

This unblocks both our Q2 close and team bonus payments.

Thanks,
[Your name]
"""
    
    for label, insight in [("Basic", basic_insight), ("Concrete", concrete_insight)]:
        prompt = f"""
        Rate this business insight on a scale of 1-10 for concrete value:
        
        "{insight}"
        
        Criteria: Does this deliver actual work product? Can someone use this immediately without additional work?
        
        Respond with: SCORE: X/10 and brief reasoning.
        """
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        print(f"\n{label} insight:")
        print(f"Rating: {response.choices[0].message.content}")

if __name__ == "__main__":
    test_concrete_output()
