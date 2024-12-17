from typing import Dict, List
from dataclasses import dataclass

@dataclass
class BehaviorPattern:
    pattern_type: str
    indicators: List[str]
    severity: float
    evidence: Dict

class BehaviorMonitor:
    def __init__(self):
        self.behavior_thresholds = {
            'payment_pattern': 0.2,
            'supplier_change': 0.15,
            'customer_concentration': 0.3
        }
    
    def analyze_behavior_patterns(self, data: Dict) -> List[BehaviorPattern]:
        patterns = []
        
        # Analyze payment patterns
        payment_patterns = self._analyze_payment_patterns(data)
        patterns.extend(payment_patterns)
        
        # Analyze supplier relationships
        supplier_patterns = self._analyze_supplier_patterns(data)
        patterns.extend(supplier_patterns)
        
        # Analyze customer patterns
        customer_patterns = self._analyze_customer_patterns(data)
        patterns.extend(customer_patterns)
        
        return patterns