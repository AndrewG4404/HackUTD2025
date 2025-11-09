#!/usr/bin/env python3
"""
Test edge cases for keyword matching
"""

def test_edge_cases():
    """Test edge cases that might cause issues"""
    
    # Edge case 1: LLM extracts "SOC2" (no space)
    findings1 = ["soc2 type ii certified"]
    normalized1 = " ".join(findings1).lower()
    
    # Edge case 2: LLM extracts "SOC 2 (Type Ⅱ)" with Unicode
    findings2 = ["soc 2 (type Ⅱ) certification"]
    normalized2 = " ".join(findings2).lower()
    
    # Edge case 3: Only "SSO" mentioned, not "SAML"
    findings3 = ["sso support available", "okta sso integration"]
    normalized3 = " ".join(findings3).lower()
    
    # Edge case 4: Only "SAML" mentioned, not "SSO"
    findings4 = ["saml 2.0 authentication"]
    normalized4 = " ".join(findings4).lower()
    
    variations_map = {
        "soc 2 type ii": ["soc2", "soc 2", "soc2 type", "soc type ii", "soc 2 type 2", "soc 2 (type Ⅱ)"],
        "sso/saml": ["sso", "saml", "saml 2.0", "single sign-on", "single sign on"],
    }
    
    def check_match(req, normalized_findings):
        req_lower = req.lower()
        matched = False
        normalized_req = req_lower.replace("soc2", "soc 2").replace("type Ⅱ", "type ii").replace("type 2", "type ii")
        
        if "/" in normalized_req:
            parts = [p.strip() for p in normalized_req.split("/")]
            matched = any(part in normalized_findings for part in parts if len(part) > 2)
        
        if not matched:
            req_normalized = normalized_req.replace("(", "").replace(")", "").replace("/", " ").strip()
            if req_normalized in variations_map:
                matched = any(var in normalized_findings for var in variations_map[req_normalized])
        
        if not matched and len(normalized_req.split()) > 1:
            phrase = normalized_req.replace("(", "").replace(")", "").replace("/", " ").replace("-", " ")
            key_parts = [p for p in phrase.split() if len(p) > 2]
            if len(key_parts) >= 2:
                matches = sum(1 for part in key_parts if part in normalized_findings)
                if matches >= min(2, len(key_parts)):
                    matched = True
        
        if not matched:
            req_keywords = normalized_req.replace("(", "").replace(")", "").replace("/", " ").split()
            meaningful_keywords = [kw for kw in req_keywords if len(kw) > 2]
            if meaningful_keywords:
                matched = any(keyword in normalized_findings for keyword in meaningful_keywords)
        
        return matched
    
    print("Testing Edge Cases:")
    print("=" * 60)
    
    # Test 1: SOC2 (no space)
    result1 = check_match("SOC 2 Type II", normalized1)
    print(f"Edge Case 1 (SOC2 no space): {'✅ PASS' if result1 else '❌ FAIL'}")
    
    # Test 2: Unicode Type Ⅱ
    result2 = check_match("SOC 2 Type II", normalized2)
    print(f"Edge Case 2 (Unicode Ⅱ): {'✅ PASS' if result2 else '❌ FAIL'}")
    
    # Test 3: Only SSO
    result3 = check_match("SSO/SAML", normalized3)
    print(f"Edge Case 3 (Only SSO): {'✅ PASS' if result3 else '❌ FAIL'}")
    
    # Test 4: Only SAML
    result4 = check_match("SSO/SAML", normalized4)
    print(f"Edge Case 4 (Only SAML): {'✅ PASS' if result4 else '❌ FAIL'}")
    
    print("=" * 60)
    
    all_passed = all([result1, result2, result3, result4])
    print(f"\n{'✅ All edge cases PASSED!' if all_passed else '❌ Some edge cases FAILED!'}")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit(test_edge_cases())

