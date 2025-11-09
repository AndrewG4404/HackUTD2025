#!/bin/bash

# Test Application Workflow - Quick Verification Script
# This script helps verify the new application workflow features are working

echo "═══════════════════════════════════════════════════════════"
echo "  APPLICATION WORKFLOW TEST - VENDORLENS"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if servers are running
echo -e "${BLUE}[1/3] Checking Server Status...${NC}"
echo ""

if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend is running at http://localhost:8000${NC}"
else
    echo -e "${YELLOW}⚠️  Backend is not running. Please run: bash START_SERVERS.sh${NC}"
    exit 1
fi

if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Frontend is running at http://localhost:3000${NC}"
else
    echo -e "${YELLOW}⚠️  Frontend is not running. Please run: bash START_SERVERS.sh${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}[2/3] Checking Recent Evaluations...${NC}"
echo ""

# Get recent evaluations
EVALS=$(curl -s http://localhost:8000/api/evaluations | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if isinstance(data, list) and len(data) > 0:
        recent = [e for e in data if e.get('type') == 'application'][:3]
        for e in recent:
            print(f\"{e.get('id')} | {e.get('name')} | {e.get('status')}\")
    else:
        print('No evaluations found')
except:
    print('Error parsing evaluations')
" 2>/dev/null)

if [ -z "$EVALS" ] || [ "$EVALS" = "No evaluations found" ]; then
    echo -e "${YELLOW}No application evaluations found yet.${NC}"
    echo ""
    echo -e "${BLUE}To test the new features:${NC}"
    echo "1. Navigate to http://localhost:3000/apply"
    echo "2. Submit a vendor application (e.g., Slack)"
    echo "3. Wait for the workflow to complete"
    echo "4. View the evaluation to see the new UI components"
else
    echo -e "${GREEN}Recent Application Evaluations:${NC}"
    echo "$EVALS"
fi

echo ""
echo -e "${BLUE}[3/3] Testing Instructions${NC}"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  NEW FEATURES TO VERIFY"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "1. Submit a new application at:"
echo "   ${GREEN}http://localhost:3000/apply${NC}"
echo ""
echo "   Test Data:"
echo "   - Vendor: Slack Technologies, LLC"
echo "   - Website: https://slack.com"
echo "   - Email: contact@slack.com"
echo "   - Product: Slack Enterprise Grid"
echo ""
echo "2. After submission, you should see:"
echo ""
echo "   ${GREEN}✓ Fit vs Requirements Matrix${NC}"
echo "     - 4 dimension cards (Compliance, Interoperability, Finance, Adoption)"
echo "     - Requirements with Met/Unmet badges"
echo "     - Color-coded (green = met, red = unmet)"
echo ""
echo "   ${GREEN}✓ Failing Criteria & Evidence${NC}"
echo "     - Unmet requirements per dimension"
echo "     - Evidence URLs (clickable links)"
echo "     - Remediation steps for vendor"
echo ""
echo "   ${GREEN}✓ Decision Buttons${NC}"
echo "     - Approve / Approve with Actions / Decline"
echo "     - Modal for decision notes and action items"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo ""
echo -e "${GREEN}Ready to test!${NC} Open http://localhost:3000/apply in your browser"
echo ""

