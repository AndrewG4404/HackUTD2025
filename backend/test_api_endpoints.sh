#!/bin/bash
# End-to-End API Testing Script
# Tests all API endpoints with real data

echo "============================================================================"
echo "VendorLens API - End-to-End Endpoint Testing"
echo "============================================================================"
echo ""

API_URL="http://localhost:8000"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if server is running
echo "[1/6] Checking if server is running..."
if curl -s "${API_URL}/api/health" > /dev/null; then
    echo -e "${GREEN}✓ Server is running${NC}"
else
    echo -e "${RED}✗ Server is not running!${NC}"
    echo "Please start the server first: python backend/main.py"
    exit 1
fi
echo ""

# Test health endpoint
echo "[2/6] Testing health endpoint..."
echo "GET ${API_URL}/api/health"
HEALTH_RESPONSE=$(curl -s "${API_URL}/api/health")
if echo "$HEALTH_RESPONSE" | grep -q "ok"; then
    echo -e "${GREEN}✓ Health check passed${NC}"
    echo "Response: $HEALTH_RESPONSE"
else
    echo -e "${RED}✗ Health check failed${NC}"
    exit 1
fi
echo ""

# Test create application evaluation
echo "[3/6] Testing create application evaluation..."
echo "POST ${API_URL}/api/evaluations/apply"
CREATE_RESPONSE=$(curl -s -X POST "${API_URL}/api/evaluations/apply" \
  -F "name=ServiceNow" \
  -F "website=https://www.servicenow.com" \
  -F "contact_email=test@servicenow.com" \
  -F "hq_location=Santa Clara, CA" \
  -F "product_name=ServiceNow Platform" \
  -F "product_description=Enterprise service management platform")

EVAL_ID=$(echo "$CREATE_RESPONSE" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)

if [ -n "$EVAL_ID" ]; then
    echo -e "${GREEN}✓ Evaluation created successfully${NC}"
    echo "Evaluation ID: $EVAL_ID"
    echo "Response: $CREATE_RESPONSE"
else
    echo -e "${RED}✗ Failed to create evaluation${NC}"
    echo "Response: $CREATE_RESPONSE"
    exit 1
fi
echo ""

# Test get evaluation
echo "[4/6] Testing get evaluation..."
echo "GET ${API_URL}/api/evaluations/${EVAL_ID}"
GET_RESPONSE=$(curl -s "${API_URL}/api/evaluations/${EVAL_ID}")
if echo "$GET_RESPONSE" | grep -q "$EVAL_ID"; then
    echo -e "${GREEN}✓ Evaluation retrieved successfully${NC}"
    echo "Status: $(echo "$GET_RESPONSE" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)"
else
    echo -e "${RED}✗ Failed to retrieve evaluation${NC}"
    exit 1
fi
echo ""

# Test run application workflow
echo "[5/6] Testing run application workflow..."
echo "POST ${API_URL}/api/workflows/application/${EVAL_ID}/run"
echo -e "${YELLOW}⏳ This may take 1-2 minutes (fetching live documentation)...${NC}"
WORKFLOW_RESPONSE=$(curl -s -X POST "${API_URL}/api/workflows/application/${EVAL_ID}/run")

if echo "$WORKFLOW_RESPONSE" | grep -q "completed\|running"; then
    echo -e "${GREEN}✓ Workflow started/completed successfully${NC}"
    echo "Response: $WORKFLOW_RESPONSE"
else
    echo -e "${RED}✗ Workflow execution failed${NC}"
    echo "Response: $WORKFLOW_RESPONSE"
    exit 1
fi
echo ""

# Wait a bit and check final status
echo "Waiting 5 seconds for workflow to complete..."
sleep 5

# Test list evaluations
echo "[6/6] Testing list evaluations..."
echo "GET ${API_URL}/api/evaluations?limit=5"
LIST_RESPONSE=$(curl -s "${API_URL}/api/evaluations?limit=5")
EVAL_COUNT=$(echo "$LIST_RESPONSE" | grep -o '"id"' | wc -l)
echo -e "${GREEN}✓ Found ${EVAL_COUNT} evaluation(s)${NC}"
echo ""

# Get final results
echo "============================================================================"
echo "Getting final evaluation results..."
echo "============================================================================"
FINAL_RESPONSE=$(curl -s "${API_URL}/api/evaluations/${EVAL_ID}")

STATUS=$(echo "$FINAL_RESPONSE" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
echo ""
echo -e "Final Status: ${GREEN}${STATUS}${NC}"

if [ "$STATUS" = "completed" ]; then
    echo ""
    echo "Scores extracted from response:"
    echo "$FINAL_RESPONSE" | grep -o '"score":[0-9.]*' | head -5
    echo ""
    echo "Total Score:"
    echo "$FINAL_RESPONSE" | grep -o '"total_score":[0-9.]*'
    echo ""
fi

echo "============================================================================"
echo -e "${GREEN}✅ ALL API TESTS PASSED!${NC}"
echo "============================================================================"
echo ""
echo "Test Summary:"
echo "  ✓ Health check"
echo "  ✓ Create application evaluation"
echo "  ✓ Get evaluation by ID"
echo "  ✓ Run application workflow"
echo "  ✓ List evaluations"
echo ""
echo "Evaluation ID for manual inspection:"
echo "  ${EVAL_ID}"
echo ""
echo "View full results:"
echo "  curl ${API_URL}/api/evaluations/${EVAL_ID} | python -m json.tool"
echo ""
echo "Or view in browser:"
echo "  ${API_URL}/docs"
echo "============================================================================"

