"""
Simple test script for the agent workflow
Tests the Nemotron client and basic agent execution
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test imports
print("Testing imports...")
from services.nemotron_client import get_nemotron_client
from services.agents.intake_agent import IntakeAgent
from services.document_processor import extract_text_from_pdf

print("✓ All imports successful\n")

# Test Nemotron client
print("="*60)
print("Testing Nemotron Client")
print("="*60)

client = get_nemotron_client()
print(f"✓ Client initialized")
print(f"  Model: {client.model}")
print(f"  API Key: {client.api_key[:10]}..." if client.api_key else "  API Key: Not set!")

# Test a simple completion
print("\nTesting chat completion...")
try:
    response = client.chat_completion(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'Hello from Nemotron!' in one sentence."}
        ],
        max_tokens=50
    )
    print(f"✓ Response: {response}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test JSON completion
print("\nTesting JSON completion...")
try:
    response = client.chat_completion_json(
        messages=[
            {"role": "user", "content": 'Return a JSON object with fields: {"status": "working", "message": "test"}'}
        ],
        max_tokens=100
    )
    print(f"✓ Response: {response}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test Intake Agent
print("\n" + "="*60)
print("Testing Intake Agent")
print("="*60)

intake_agent = IntakeAgent()
print(f"✓ Agent initialized: {intake_agent.name} ({intake_agent.role})")

# Create test context
test_context = {
    "vendor": {
        "name": "Test Company",
        "website": "https://example.com",
        "product_name": "TestCRM",
        "product_description": "A customer relationship management system for small businesses",
        "files": [],
        "doc_urls": []
    }
}

print("\nExecuting agent...")
try:
    result = intake_agent.execute(test_context)
    print(f"✓ Agent execution successful!")
    print(f"  Summary: {result.get('summary', 'N/A')}")
    print(f"  Fields: {result.get('fields', {})}")
except Exception as e:
    print(f"✗ Error: {e}")

print("\n" + "="*60)
print("Test Complete!")
print("="*60)
print("\nIf all tests passed, your agent workflow is ready to use!")
print("Next steps:")
print("1. Start MongoDB: docker-compose up -d")
print("2. Run backend: python backend/main.py")
print("3. Test via Swagger UI: http://localhost:8000/docs")

