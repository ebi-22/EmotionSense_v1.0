"""
Stage 1: Rules Engine
Fast keyword-based detection for crisis, urgency, and basic emotions.
Acts as a safety net - if crisis keywords detected, always escalates.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any

class RulesEngine:
    def __init__(self, rules_path: str = None):
        if rules_path is None:
            rules_path = Path(__file__).parent.parent / "data" / "rules.json"
        
        with open(rules_path, 'r', encoding='utf-8') as f:
            self.rules = json.load(f)
        
        # Compile regex patterns for efficiency
        self.patterns = {}
        for category, keywords in self.rules.items():
            # Create case-insensitive pattern
            pattern = '|'.join(re.escape(kw) for kw in keywords)
            self.patterns[category] = re.compile(pattern, re.IGNORECASE)
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyze text for crisis indicators, urgency, and emotion keywords.
        Returns dict with is_crisis, urgency, matched_keywords, etc.
        """
        text_lower = text.lower()
        result = {
            "is_crisis": False,
            "urgency": "low",
            "matched_keywords": [],
            "rule_flags": []
        }
        
        # Check crisis keywords (HIGHEST PRIORITY)
        crisis_matches = self.patterns.get("crisis_keywords", re.compile("$^")).findall(text_lower)
        if crisis_matches:
            result["is_crisis"] = True
            result["urgency"] = "critical"
            result["matched_keywords"].extend(crisis_matches)
            result["rule_flags"].append("CRISIS_DETECTED")
        
        # Check urgency
        if not result["is_crisis"]:
            high_urgency = self.patterns.get("urgency_high", re.compile("$^")).findall(text_lower)
            if high_urgency:
                result["urgency"] = "high"
                result["matched_keywords"].extend(high_urgency)
                result["rule_flags"].append("HIGH_URGENCY")
            else:
                medium_urgency = self.patterns.get("urgency_medium", re.compile("$^")).findall(text_lower)
                if medium_urgency:
                    result["urgency"] = "medium"
                    result["matched_keywords"].extend(medium_urgency)
                    result["rule_flags"].append("MEDIUM_URGENCY")
        
        # Check anger keywords
        anger_matches = self.patterns.get("anger_keywords", re.compile("$^")).findall(text_lower)
        if anger_matches:
            result["matched_keywords"].extend(anger_matches)
            result["rule_flags"].append("ANGER_DETECTED")
        
        # Check stress keywords
        stress_matches = self.patterns.get("stress_keywords", re.compile("$^")).findall(text_lower)
        if stress_matches:
            result["matched_keywords"].extend(stress_matches)
            result["rule_flags"].append("STRESS_DETECTED")
        
        # Check sad keywords
        sad_matches = self.patterns.get("sad_keywords", re.compile("$^")).findall(text_lower)
        if sad_matches:
            result["matched_keywords"].extend(sad_matches)
            result["rule_flags"].append("SADNESS_DETECTED")
        
        # Check happy keywords
        happy_matches = self.patterns.get("happy_keywords", re.compile("$^")).findall(text_lower)
        if happy_matches:
            result["matched_keywords"].extend(happy_matches)
            result["rule_flags"].append("JOY_DETECTED")
        
        # Deduplicate
        result["matched_keywords"] = list(set(result["matched_keywords"]))
        
        return result


# Quick test
if __name__ == "__main__":
    engine = RulesEngine()
    
    test_cases = [
        "Help ASAP! I'm so angry with this delay",
        "I want to kill myself",
        "Can you help me soon? I'm a bit worried",
        "Everything is fine, just checking in"
    ]
    
    for text in test_cases:
        print(f"\nInput: {text}")
        print(f"Output: {engine.analyze(text)}")
