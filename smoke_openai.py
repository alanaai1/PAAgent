import openai, json, os, sys

MODEL = "o4-mini"        # change to gpt-4o-mini or gpt-3.5-turbo if needed
prompt = 'Return JSON {"ping": "pong"}'

try:
    out = openai.ChatCompletion.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    txt = out.choices[0].message.content.strip()
    print("✅ OpenAI returned:", txt)
    json.loads(txt)  # ensure valid JSON
    print("✅ JSON parse OK")
except Exception as e:
    print("❌ OpenAI test FAILED:", e)
    sys.exit(1)
