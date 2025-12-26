"""Quick test to verify auth implementation works"""
import sys
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token
from app.services.personalization_service import PersonalizationService
from app.models import UserProfile
from datetime import datetime
from uuid import uuid4

print("Testing Auth Implementation...")
print("=" * 60)

# Test 1: Password Hashing
print("\n[TEST 1] Password Hashing")
password = "Test1234"
hashed = hash_password(password)
print(f"  Password: {password}")
print(f"  Hashed: {hashed[:50]}...")
print(f"  Verification: {verify_password(password, hashed)}")
print(f"  Wrong password: {verify_password('WrongPass', hashed)}")
assert verify_password(password, hashed), "Password verification failed!"
assert not verify_password("WrongPass", hashed), "Wrong password should fail!"
print("  PASSED")

# Test 2: JWT Tokens
print("\n[TEST 2] JWT Token Generation")
user_id = str(uuid4())
token_data = {"sub": user_id}
token = create_access_token(token_data)
print(f"  User ID: {user_id}")
print(f"  Token: {token[:50]}...")
decoded = decode_access_token(token)
print(f"  Decoded sub: {decoded.get('sub')}")
assert decoded.get('sub') == user_id, "Token decode failed!"
print("  PASSED")

# Test 3: Invalid Token
print("\n[TEST 3] Invalid Token Handling")
invalid_token = "invalid.token.here"
decoded_invalid = decode_access_token(invalid_token)
print(f"  Invalid token result: {decoded_invalid}")
assert decoded_invalid is None, "Invalid token should return None!"
print("  PASSED")

# Test 4: Personalization Service
print("\n[TEST 4] Personalization Service")

# Create a beginner profile
beginner_profile = UserProfile(
    id=uuid4(),
    user_id=uuid4(),
    programming_experience='beginner',
    python_proficiency='basic',
    ros_experience='never_heard',
    ai_ml_experience='none',
    primary_interests=['autonomous_navigation'],
    created_at=datetime.utcnow(),
    updated_at=datetime.utcnow()
)

complexity = PersonalizationService.get_complexity_level(beginner_profile)
print(f"  Beginner complexity: {complexity}")
assert complexity == 'beginner', f"Expected beginner, got {complexity}"

context = PersonalizationService.get_personalization_context(beginner_profile)
print(f"  Context: {context}")
assert 'beginner' in context.lower(), "Context should mention beginner level"
print("  PASSED")

# Create an advanced profile
advanced_profile = UserProfile(
    id=uuid4(),
    user_id=uuid4(),
    programming_experience='expert',
    python_proficiency='advanced',
    ros_experience='advanced',
    ai_ml_experience='production',
    robotics_hardware_experience='research',
    primary_interests=['computer_vision', 'manipulation'],
    created_at=datetime.utcnow(),
    updated_at=datetime.utcnow()
)

complexity = PersonalizationService.get_complexity_level(advanced_profile)
print(f"  Advanced complexity: {complexity}")
assert complexity == 'advanced', f"Expected advanced, got {complexity}"

# Test 5: Anonymous User (no profile)
print("\n[TEST 5] Anonymous User Handling")
complexity = PersonalizationService.get_complexity_level(None)
print(f"  Anonymous complexity: {complexity}")
assert complexity == 'intermediate', "Anonymous should default to intermediate"
context = PersonalizationService.get_personalization_context(None)
print(f"  Anonymous context: {context}")
assert 'new to the topic' in context.lower(), "Should indicate user is new"
print("  PASSED")

print("\n" + "=" * 60)
print("ALL TESTS PASSED!")
print("=" * 60)
print("\nAuth implementation is working correctly!")
print("You can now start the server with: uvicorn app.main:app --reload")
