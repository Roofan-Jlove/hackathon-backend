import requests
import json

# Test the RAG chat endpoint
url = "http://localhost:8000/api/chat"

payload = {
    "question": "What is ROS?",
    "context": None
}

headers = {
    "Content-Type": "application/json"
}

print("Testing RAG API endpoint...")
print(f"URL: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")
print("\nSending request...")

try:
    response = requests.post(url, json=payload, headers=headers, timeout=30)

    print(f"\nStatus Code: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print("\n[SUCCESS] RAG API is working!")
        print(f"\nAnswer:\n{result.get('answer', 'No answer')}")
        print(f"\nSources: {len(result.get('sources', []))} sources returned")

        # Print first source if available
        if result.get('sources'):
            print(f"\nFirst source preview:")
            print(f"  - Score: {result['sources'][0].get('score')}")
            print(f"  - Content: {result['sources'][0].get('chunk', '')[:100]}...")
    else:
        print(f"\n[ERROR] Request failed")
        print(f"Response: {response.text}")

except Exception as e:
    print(f"\n[ERROR] {str(e)}")
