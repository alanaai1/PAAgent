#!/usr/bin/env python3
import os, pickle, pytz

import openai, json

import openai, json, traceback
def call_gpt(prompt, temperature=0.7, model="o4-mini"):
    try:
        resp = openai.ChatCompletion.create(
            model=model,
            messages=[{"role":"user","content":prompt}],
            temperature=temperature,
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        traceback.print_exc()
        raise
if __name__ == "__main__":
    res = Runner.run_sync(chief, "Run full analysis.")
    print("\n🧠 Final Output\n" + "="*30)
    print(res)

