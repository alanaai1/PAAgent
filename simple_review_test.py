import openai
import os

client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def test_insight_quality():
    test_insight = "Send VAT receipt update to Alan about bonus processing."
    
    prompt = f"""
    Rate this business insight on a scale of 1-10 for strategic value:
    
    "{test_insight}"
    
    Consider: Is this strategic? Does it move the business forward? Is it actionable for executives?
    
    Respond with just: SCORE: X/10 and one line of feedback.
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    
    print("Current insight quality:")
    print(f"Insight: {test_insight}")
    print(f"Rating: {response.choices[0].message.content}")

if __name__ == "__main__":
    test_insight_quality()
