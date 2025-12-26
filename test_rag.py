"""
Diagnostic script to test RAG pipeline
"""
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 60)
print("RAG Pipeline Diagnostic Test")
print("=" * 60)

# Test 1: Check environment variables
print("\n1. Checking environment variables...")
required_vars = ["OPENAI_API_KEY", "QDRANT_URL", "QDRANT_API_KEY"]
for var in required_vars:
    value = os.getenv(var)
    if value:
        print(f"   [OK] {var}: {value[:20]}...")
    else:
        print(f"   [ERROR] {var}: NOT SET")

# Test 2: Import RAG service
print("\n2. Importing RAG service...")
try:
    from app.services.rag_service import rag_service
    print("   [OK] RAG service imported successfully")
except Exception as e:
    print(f"   [ERROR] Error importing RAG service: {e}")
    exit(1)

# Test 3: Check Qdrant connection
print("\n3. Checking Qdrant connection...")
try:
    collections = rag_service.qdrant_client.get_collections()
    print(f"   [OK] Connected to Qdrant")
    print(f"   Collections: {[c.name for c in collections.collections]}")
except Exception as e:
    print(f"   [ERROR] Qdrant connection failed: {e}")
    exit(1)

# Test 4: Check if book_content collection exists
print("\n4. Checking book_content collection...")
try:
    collection_info = rag_service.qdrant_client.get_collection("book_content")
    print(f"   [OK] Collection exists")
    print(f"   Points count: {collection_info.points_count}")
    print(f"   Vector size: {collection_info.config.params.vectors.size}")
except Exception as e:
    print(f"   [ERROR] Collection check failed: {e}")

# Test 5: Test embedding generation
print("\n5. Testing embedding generation...")
try:
    test_text = "What is ROS?"
    embedding = rag_service.embeddings_model.embed_query(test_text)
    print(f"   [OK] Embedding generated")
    print(f"   Embedding dimension: {len(embedding)}")
except Exception as e:
    print(f"   [ERROR] Embedding generation failed: {e}")
    exit(1)

# Test 6: Test Qdrant search
print("\n6. Testing Qdrant search...")
try:
    query_vector = rag_service.embeddings_model.embed_query("What is ROS?")
    search_results = rag_service.qdrant_client.query_points(
        collection_name="book_content",
        query=query_vector,
        limit=3,
        with_payload=True,
        with_vectors=False
    )
    print(f"   [OK] Search executed")
    print(f"   Results found: {len(search_results.points) if hasattr(search_results, 'points') else len(search_results)}")

    # Print first result if available
    if hasattr(search_results, 'points') and search_results.points:
        first = search_results.points[0]
        print(f"   First result score: {first.score}")
        print(f"   First result text: {first.payload.get('content', '')[:100]}...")
    elif isinstance(search_results, list) and search_results:
        first = search_results[0]
        print(f"   First result score: {first.score}")
        print(f"   First result text: {first.payload.get('content', '')[:100]}...")

except Exception as e:
    print(f"   [ERROR] Qdrant search failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test 7: Test full RAG pipeline
print("\n7. Testing full RAG pipeline...")
async def test_rag():
    try:
        answer, sources = await rag_service.query_rag_pipeline(
            question="What is ROS?",
            context=None
        )
        print(f"   [OK] RAG pipeline executed")
        print(f"   Answer: {answer[:200]}...")
        print(f"   Sources count: {len(sources)}")
    except Exception as e:
        print(f"   [ERROR] RAG pipeline failed: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(test_rag())

print("\n" + "=" * 60)
print("Diagnostic test complete!")
print("=" * 60)
