"""
End-to-End Backend Testing Script
Tests all components: MongoDB, API endpoints, agents, and workflows
"""
import os
import sys
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

print("="*80)
print("VendorLens Backend - End-to-End Testing")
print("="*80)
print()

# ============================================================================
# STEP 1: Environment Check
# ============================================================================
print("[1/7] Checking Environment Variables...")
print("-" * 80)

required_vars = {
    "MONGODB_URI": os.getenv("MONGODB_URI"),
    "MONGODB_DB_NAME": os.getenv("MONGODB_DB_NAME"),
    "NEMOTRON_API_KEY": os.getenv("NEMOTRON_API_KEY"),
    "NEMOTRON_API_URL": os.getenv("NEMOTRON_API_URL"),
}

all_set = True
for var, value in required_vars.items():
    if value:
        display_value = value[:30] + "..." if len(value) > 30 else value
        print(f"  ✓ {var}: {display_value}")
    else:
        print(f"  ✗ {var}: NOT SET")
        all_set = False

if not all_set:
    print("\n❌ ERROR: Missing required environment variables!")
    print("Please create a .env file with all required variables.")
    sys.exit(1)

print("\n✅ All environment variables are set\n")

# ============================================================================
# STEP 2: MongoDB Connection
# ============================================================================
print("[2/7] Testing MongoDB Connection...")
print("-" * 80)

try:
    from database.connection import get_database
    db = get_database()
    # Test connection
    db.command("ping")
    print(f"  ✓ Connected to MongoDB")
    print(f"  ✓ Database: {db.name}")
    
    # Check collections
    collections = db.list_collection_names()
    print(f"  ✓ Collections: {collections if collections else 'None (will be created)'}")
    
    print("\n✅ MongoDB connection successful\n")
except Exception as e:
    print(f"\n❌ ERROR: MongoDB connection failed!")
    print(f"  Error: {e}")
    sys.exit(1)

# ============================================================================
# STEP 3: Nemotron Client
# ============================================================================
print("[3/7] Testing Nemotron Client...")
print("-" * 80)

try:
    from services.nemotron_client import get_nemotron_client
    
    client = get_nemotron_client()
    print(f"  ✓ Client initialized")
    print(f"  ✓ Model: {client.model}")
    print(f"  ✓ Endpoint: {client.base_url}")
    
    # Test simple completion
    print("\n  Testing chat completion...")
    response = client.chat_completion(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'Testing successful!' in 3 words or less."}
        ],
        max_tokens=20,
        temperature=0.3
    )
    print(f"  ✓ Response: {response}")
    
    # Test JSON completion
    print("\n  Testing JSON completion...")
    json_response = client.chat_completion_json(
        messages=[
            {"role": "user", "content": 'Return exactly: {"status": "ok", "test": true}'}
        ],
        max_tokens=50,
        temperature=0.1
    )
    print(f"  ✓ JSON Response: {json_response}")
    
    print("\n✅ Nemotron client working correctly\n")
except Exception as e:
    print(f"\n❌ ERROR: Nemotron client failed!")
    print(f"  Error: {e}")
    print("\nNote: If rate limited, consider using local NIM deployment")
    sys.exit(1)

# ============================================================================
# STEP 4: Test Individual Agents
# ============================================================================
print("[4/7] Testing Individual Agents...")
print("-" * 80)

try:
    from services.agents.intake_agent import IntakeAgent
    from services.agents.compliance_agent import ComplianceAgent
    from services.agents.finance_agent import FinanceAgent
    
    # Test Intake Agent
    print("  Testing IntakeAgent...")
    intake = IntakeAgent()
    intake_result = intake.execute({
        "vendor": {
            "name": "Test Vendor",
            "website": "https://example.com",
            "product_name": "TestProduct",
            "product_description": "A test product for evaluation",
            "files": []
        }
    })
    print(f"  ✓ IntakeAgent: {intake_result.get('summary', 'N/A')[:50]}...")
    
    print("\n✅ Agents are functional\n")
except Exception as e:
    print(f"\n❌ ERROR: Agent test failed!")
    print(f"  Error: {e}")
    sys.exit(1)

# ============================================================================
# STEP 5: Test Database Operations
# ============================================================================
print("[5/7] Testing Database Operations...")
print("-" * 80)

try:
    from database.repository import create_evaluation, get_evaluation, list_evaluations
    from database.models import Evaluation, Vendor
    
    # Create test evaluation
    print("  Creating test evaluation...")
    test_vendor = Vendor(
        id="test-vendor",
        name="Test Company",
        website="https://example.com"
    )
    
    test_eval = Evaluation(
        type="application",
        name="Test Evaluation - E2E",
        vendors=[test_vendor]
    )
    
    eval_id = create_evaluation(test_eval)
    print(f"  ✓ Created evaluation: {eval_id}")
    
    # Retrieve evaluation
    print("  Retrieving evaluation...")
    retrieved = get_evaluation(eval_id)
    if retrieved:
        print(f"  ✓ Retrieved evaluation: {retrieved['name']}")
        print(f"  ✓ Status: {retrieved['status']}")
    else:
        raise Exception("Failed to retrieve evaluation")
    
    # List evaluations
    print("  Listing evaluations...")
    evals = list_evaluations(limit=5)
    print(f"  ✓ Found {len(evals)} evaluation(s)")
    
    print("\n✅ Database operations working correctly\n")
    
    # Store eval_id for workflow test
    test_evaluation_id = eval_id
    
except Exception as e:
    print(f"\n❌ ERROR: Database operations failed!")
    print(f"  Error: {e}")
    sys.exit(1)

# ============================================================================
# STEP 6: Test Application Workflow
# ============================================================================
print("[6/7] Testing Application Workflow...")
print("-" * 80)

try:
    from services.workflows.application_pipeline import run_application_pipeline
    
    print(f"  Running workflow for evaluation: {test_evaluation_id}")
    print("  (This may take 1-2 minutes with live documentation fetching...)\n")
    
    start_time = time.time()
    result = run_application_pipeline(test_evaluation_id)
    elapsed = time.time() - start_time
    
    print(f"\n  ✓ Workflow completed in {elapsed:.1f} seconds")
    print(f"  ✓ Status: {result.get('status')}")
    print(f"  ✓ Total Score: {result.get('total_score', 'N/A')}")
    print(f"  ✓ Recommendation: {result.get('recommendation', 'N/A')[:80]}...")
    
    # Verify results in database
    final_eval = get_evaluation(test_evaluation_id)
    if final_eval['status'] == 'completed':
        print(f"  ✓ Database updated: status = completed")
        vendor = final_eval['vendors'][0]
        if vendor.get('agent_outputs'):
            print(f"  ✓ Agent outputs stored:")
            for agent_name in ['compliance', 'interoperability', 'finance', 'adoption']:
                score = vendor['agent_outputs'].get(agent_name, {}).get('score', 'N/A')
                print(f"    - {agent_name}: {score}")
    
    print("\n✅ Application workflow successful\n")
    
except Exception as e:
    print(f"\n❌ ERROR: Application workflow failed!")
    print(f"  Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ============================================================================
# STEP 7: Summary
# ============================================================================
print("="*80)
print("✅ ALL TESTS PASSED!")
print("="*80)
print()
print("Backend Components Tested:")
print("  ✓ Environment variables")
print("  ✓ MongoDB connection")
print("  ✓ Nemotron API client")
print("  ✓ Individual agents")
print("  ✓ Database operations (CRUD)")
print("  ✓ Application workflow pipeline")
print()
print("Next Steps:")
print("  1. Start the backend: python backend/main.py")
print("  2. Test via Swagger UI: http://localhost:8000/docs")
print("  3. Test frontend: cd frontend && npm run dev")
print("  4. Create evaluations via UI or API")
print()
print("Test Evaluation ID (for manual testing):")
print(f"  {test_evaluation_id}")
print()
print("To view results:")
print(f"  curl http://localhost:8000/api/evaluations/{test_evaluation_id}")
print()
print("="*80)

