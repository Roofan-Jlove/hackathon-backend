import requests
import json

BASE_URL = "http://localhost:8000"

def test_signup():
    print("\n[TEST] Signup")
    print("="*60)
    url = f"{BASE_URL}/api/auth/signup"
    payload = {
        "email": "test@example.com",
        "password": "Test1234",
        "profile": {
            "programming_experience": "intermediate",
            "python_proficiency": "advanced",
            "ros_experience": "beginner",
            "ai_ml_experience": "pretrained",
            "robotics_hardware_experience": "hobbyist",
            "sensor_integration": "basic",
            "electronics_knowledge": "intermediate",
            "primary_interests": ["autonomous_navigation", "computer_vision"],
            "time_commitment": "regular"
        }
    }

    try:
        response = requests.post(url, json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 201:
            return response.json()["token"]
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_signin():
    print("\n[TEST] Signin")
    print("="*60)
    url = f"{BASE_URL}/api/auth/signin"
    payload = {
        "email": "test@example.com",
        "password": "Test1234"
    }

    try:
        response = requests.post(url, json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 200:
            return response.json()["token"]
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_get_me(token):
    print("\n[TEST] Get Current User")
    print("="*60)
    url = f"{BASE_URL}/api/auth/me"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.get(url, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

def test_get_profile(token):
    print("\n[TEST] Get Profile")
    print("="*60)
    url = f"{BASE_URL}/api/profile"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.get(url, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

def test_update_profile(token):
    print("\n[TEST] Update Profile")
    print("="*60)
    url = f"{BASE_URL}/api/profile"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "programming_experience": "advanced",
        "ros_experience": "intermediate"
    }

    try:
        response = requests.put(url, json=payload, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("="*60)
    print("Testing Authentication API")
    print("="*60)
    print("\nMake sure the backend server is running on http://localhost:8000")
    input("Press Enter to continue...")

    # Test signup
    token = test_signup()

    # If signup successful (or user already exists), test signin
    if not token:
        token = test_signin()

    # If we have a token, test other endpoints
    if token:
        test_get_me(token)
        test_get_profile(token)
        test_update_profile(token)

    print("\n" + "="*60)
    print("Tests complete!")
    print("="*60)
