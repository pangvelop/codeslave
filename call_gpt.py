import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def call_gpt(prompt: str) -> str:
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )
    return response.choices[0].message["content"].strip()
