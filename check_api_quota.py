import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("[ERROR] No API key found in .env file")
    exit(1)

print(f"[OK] API key found: {api_key[:20]}...")

try:
    client = OpenAI(api_key=api_key)

    # Test the API key with a minimal request
    print("\nTesting API key with a simple request...")
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hi"}],
        max_tokens=5
    )

    print("[SUCCESS] API key is valid and working!")
    print(f"[RESPONSE] {response.choices[0].message.content}")

    # Note: OpenAI doesn't provide direct quota API endpoints
    # You can check your usage at: https://platform.openai.com/usage
    print("\n[INFO] To check your quota and usage details:")
    print("   Visit: https://platform.openai.com/usage")
    print("   Or: https://platform.openai.com/account/billing/overview")

except Exception as e:
    print(f"[ERROR] {str(e)}")
    if "insufficient_quota" in str(e):
        print("\n[WARNING] Your API key has insufficient quota!")
        print("   Please add credits at: https://platform.openai.com/account/billing")
    elif "invalid" in str(e).lower():
        print("\n[WARNING] Your API key appears to be invalid!")
