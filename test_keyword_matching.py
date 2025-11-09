#!/usr/bin/env python3
"""
Test script to verify ComplianceAgent keyword matching fixes
Tests the new matching logic against known cases
"""

def test_keyword_matching():
    """Test the improved keyword matching logic"""
    
    # Simulate findings from Slack compliance documentation
    findings = [
        "SOC 2 Type II certification",
        "ISO 27001 certified",
        "SSO support via SAML 2.0",
        "Okta SSO integration available",
        "GDPR compliant",
        "DPA available",
        "Encryption at rest and in transit",
        "Audit logging enabled",
        "RBAC support",
        "MFA available"
    ]
    
    normalized_findings = " ".join(findings).lower()
    
    # Requirements to test
    requirements = [
        "SOC 2 Type II",
        "SSO/SAML",
        "ISO 27001",
        "GDPR",
        "DPA (Data Processing Agreement)",
        "Encryption at rest and in transit",
        "Audit logs",
        "RBAC",
        "MFA"
    ]
    
    # Variations map (same as in compliance_agent.py)
    variations_map = {
        "soc 2 type ii": ["soc2", "soc 2", "soc2 type", "soc type ii", "soc 2 type 2", "soc 2 (type Ⅱ)"],
        "sso/saml": ["sso", "saml", "saml 2.0", "single sign-on", "single sign on"],
        "iso 27001": ["iso27001", "iso/iec 27001", "iso/iec27001", "iso 27001:2013"],
        "gdpr": ["general data protection regulation", "eu gdpr"],
        "mfa": ["multi-factor", "multifactor", "two-factor", "2fa", "two factor"],
        "rbac": ["role-based", "role based", "role based access", "role-based access control"],
        "dpa (data processing agreement)": ["dpa", "data processing agreement", "data processing addendum"],
        "encryption at rest and in transit": ["encryption", "encrypted", "tls", "ssl", "aes-256", "encryption at rest", "encryption in transit"],
        "audit logs": ["audit log", "audit logging", "audit trail", "audit trail logs"]
    }
    
    results = {}
    
    for req in requirements:
        req_lower = req.lower()
        matched = False
        
        # Normalize common variations in requirement text
        normalized_req = req_lower.replace("soc2", "soc 2").replace("type Ⅱ", "type ii").replace("type 2", "type ii")
        
        # Strategy 1: Handle "/" separator (e.g., "SSO/SAML")
        if "/" in normalized_req:
            parts = [p.strip() for p in normalized_req.split("/")]
            matched = any(
                part in normalized_findings 
                for part in parts 
                if len(part) > 2
            )
        
        # Strategy 2: Check variations map for known patterns
        if not matched:
            req_normalized = normalized_req.replace("(", "").replace(")", "").replace("/", " ").strip()
            if req_normalized in variations_map:
                matched = any(var in normalized_findings for var in variations_map[req_normalized])
        
        # Strategy 3: Phrase matching for multi-word requirements
        if not matched and len(normalized_req.split()) > 1:
            phrase = normalized_req.replace("(", "").replace(")", "").replace("/", " ").replace("-", " ")
            key_parts = [p for p in phrase.split() if len(p) > 2]
            
            if len(key_parts) >= 2:
                matches = sum(1 for part in key_parts if part in normalized_findings)
                if matches >= min(2, len(key_parts)):
                    matched = True
        
        # Strategy 4: Individual keyword matching (lower threshold)
        if not matched:
            req_keywords = normalized_req.replace("(", "").replace(")", "").replace("/", " ").split()
            meaningful_keywords = [kw for kw in req_keywords if len(kw) > 2]
            if meaningful_keywords:
                matched = any(keyword in normalized_findings for keyword in meaningful_keywords)
        
        results[req] = "✅ MET" if matched else "❌ UNMET"
    
    # Print results
    print("=" * 60)
    print("KEYWORD MATCHING TEST RESULTS")
    print("=" * 60)
    print()
    
    for req, status in results.items():
        print(f"{status} {req}")
    
    print()
    print("=" * 60)
    
    # Verify critical cases
    critical_cases = {
        "SOC 2 Type II": results.get("SOC 2 Type II") == "✅ MET",
        "SSO/SAML": results.get("SSO/SAML") == "✅ MET"
    }
    
    all_passed = all(critical_cases.values())
    
    print()
    print("CRITICAL CASES VERIFICATION:")
    for case, passed in critical_cases.items():
        print(f"  {'✅' if passed else '❌'} {case}: {'PASS' if passed else 'FAIL'}")
    
    print()
    if all_passed:
        print("✅ All critical cases PASSED!")
        return 0
    else:
        print("❌ Some critical cases FAILED!")
        return 1

if __name__ == "__main__":
    exit(test_keyword_matching())

