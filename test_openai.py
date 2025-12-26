"""
Test OpenAI API connection
"""
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

print("Testing OpenAI API...")
print(f"API Key: {os.getenv('OPENAI_API_KEY')[:20]}...{os.getenv('OPENAI_API_KEY')[-4:]}")

try:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'Hello, OpenAI API is working!'"}
        ],
        max_tokens=20
    )

    print("\nSuccess!")
    print(f"Response: {response.choices[0].message.content}")

except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
