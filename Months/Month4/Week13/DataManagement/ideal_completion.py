from dataclasses import dataclass, field
from typing import List, Dict, Callable, Any
from datetime import datetime
import logging
import re

# Base classes for matching and mastering
@dataclass
class MatchingRule:
    field: str
    operator: str
    value: Any = None
    threshold: float = 1.0

@dataclass
class MatchingPolicy:
    name: str
    rules: List[MatchingRule]
    description: str = ""

    def matches(self, record1: Dict, record2: Dict) -> bool:
        """Enhanced matching logic with better similarity handling."""
        for rule in self.rules:
            val1 = record1.get(rule.field)
            val2 = record2.get(rule.field)
            
            # Skip if either value is None
            if val1 is None or val2 is None:
                continue
            
            # Convert values to strings for comparison
            str_val1 = str(val1)
            str_val2 = str(val2)
            
            if rule.operator == 'equals':
                if str_val1 != str_val2:
                    return False
            elif rule.operator == 'similarity':
                similarity = compute_similarity(str_val1, str_val2)
                if similarity < rule.threshold:
                    return False
        
        # If we got through all rules without returning False, it's a match
        return True

@dataclass
class FieldSource:
    field: str
    sources: List[str]

@dataclass
class MasteringPolicy:
    name: str
    field_sources: List[FieldSource]
    default_strategy: str = "highest_priority"

    def consolidate(self, records: List[Dict]) -> Dict:
        master_record = {}
        # First, get all fields from the most recent record
        if records:
            master_record.update(records[-1])
        
        # Then apply the sourcing rules
        for field_source in self.field_sources:
            for source in field_source.sources:
                for record in records:
                    if record.get('source') == source and field_source.field in record:
                        master_record[field_source.field] = record[field_source.field]
                        break
                if field_source.field in master_record:
                    break
        return master_record

@dataclass
class ValidationRule:
    field: str
    checks: List[Callable[[Any], bool]]
    error_messages: List[str]

@dataclass
class AuditLog:
    timestamp: datetime
    action: str
    entity_id: str
    changes: Dict
    source: str

# Enhanced Master implementation
class EnhancedMaster:
    def __init__(self, name: str, matching_policy: MatchingPolicy,
                 mastering_policy: MasteringPolicy, sources: List[str],
                 validation_rules: List[ValidationRule] = None):
        """Initialize EnhancedMaster with required policies and rules."""
        self.name = name
        self.matching_policy = matching_policy
        self.mastering_policy = mastering_policy
        self.sources = sources
        self.validation_rules = validation_rules or []
        self.audit_logs = []

    def validate_record(self, record: Dict) -> List[str]:
        """Validate record against defined rules."""
        errors = []
        for rule in self.validation_rules:
            value = record.get(rule.field)
            for check, message in zip(rule.checks, rule.error_messages):
                if not check(value):
                    errors.append(f"{rule.field}: {message}")
        return errors

    def log_change(self, action: str, entity_id: str, changes: Dict, source: str):
        """Log changes to audit trail."""
        log = AuditLog(
            timestamp=datetime.now(),
            action=action,
            entity_id=entity_id,
            changes=changes,
            source=source
        )
        self.audit_logs.append(log)

    def create_master_record(self, new_record: Dict, existing_masters: List[Dict]) -> Dict:
        """Create or update master record."""
        # Validate incoming record
        errors = self.validate_record(new_record)
        if errors:
            raise ValueError(f"Validation failed: {', '.join(errors)}")

        # Calculate match scores with weighted fields
        def calculate_match_score(master: Dict) -> float:
            score = 0
            weights = {"entity_id": 0.4, "tax_id": 0.3, "company_name": 0.3}
            
            for field, weight in weights.items():
                if field in master and field in new_record:
                    if field in ["entity_id", "tax_id"]:
                        score += weight if master[field] == new_record[field] else 0
                    else:
                        similarity = compute_similarity(str(master[field]), 
                                                     str(new_record[field]))
                        score += weight * similarity
            return score

        matching_records = []
        for master in existing_masters:
            score = calculate_match_score(master)
            if score > 0.8:  # Configurable threshold
                matching_records.append((master, score))

        matching_records.sort(key=lambda x: x[1], reverse=True)

        if matching_records:
            best_match = matching_records[0][0]
            consolidated = self.mastering_policy.consolidate([best_match, new_record])
            
            # Enhanced change detection for audit logging
            changes = {}
            all_fields = set(best_match.keys()) | set(new_record.keys())
            for field in all_fields:
                old_value = best_match.get(field)
                new_value = new_record.get(field)
                if old_value != new_value and new_value is not None:
                    changes[field] = new_value
            
            self.log_change("UPDATE", best_match["entity_id"], changes, 
                          new_record["source"])
            
            return consolidated
        else:
            consolidated = self.mastering_policy.consolidate([new_record])
            # Include all fields in changes for new records
            self.log_change("CREATE", new_record.get("entity_id", ""), 
                          dict(new_record), new_record["source"])
            return consolidated

def compute_similarity(str1: str, str2: str) -> float:
    """Enhanced string similarity computation for better matching."""
    if not str1 or not str2:
        return 0.0
    
    # Normalize strings
    str1 = str1.lower()
    str2 = str2.lower()
    
    # Split into words and create word lists
    words1 = str1.split()
    words2 = str2.split()
    
    # Handle exact match case
    if str1 == str2:
        return 1.0
        
    # Create sets of words
    set1 = set(words1)
    set2 = set(words2)
    
    # Calculate Jaccard similarity
    intersection = len(set1 & set2)
    union = len(set1 | set2)

    #if no words in common, return 0 immediately
    if intersection == 0:
        return 0.0
    
    # Calculate positional bonus (words in same position)
    position_matches = sum(1 for i in range(min(len(words1), len(words2))) 
                         if words1[i] == words2[i])
    position_bonus = position_matches * 0.2  # Increased position bonus
    
    # Calculate word length similarity bonus
    len_ratio = min(len(words1), len(words2)) / max(len(words1), len(words2))
    length_bonus = len_ratio * 0.1 if intersection > 0 else 0.0
    
    # Calculate final similarity
    base_similarity = intersection / union if union > 0 else 0.0
    final_similarity = min(1.0, base_similarity + position_bonus + length_bonus)
    
    return final_similarity

# Example validation functions
def is_valid_tax_id(value: str) -> bool:
    return bool(re.match(r'^\d{2}-\d{7}$', str(value)))

def is_valid_revenue(value: float) -> bool:
    return isinstance(value, (int, float)) and value >= 0

# Setup and example usage
if __name__ == "__main__":
    # Create matching policy
    matching_policy = MatchingPolicy(
        name="Basic Matching",
        rules=[
            MatchingRule(field="entity_id", operator="equals"),
            MatchingRule(field="tax_id", operator="equals")
        ]
    )

    # Create mastering policy
    mastering_policy = MasteringPolicy(
        name="Basic Mastering",
        field_sources=[
            FieldSource(field="company_name", sources=["source_A", "source_B"]),
            FieldSource(field="annual_revenue", sources=["source_B", "source_A"]),
            FieldSource(field="address", sources=["source_C", "source_A", "source_B"]),
        ]
    )

    # Create validation rules
    validation_rules = [
        ValidationRule(
            field="tax_id",
            checks=[is_valid_tax_id],
            error_messages=["Invalid tax ID format (XX-XXXXXXX required)"]
        ),
        ValidationRule(
            field="annual_revenue",
            checks=[is_valid_revenue],
            error_messages=["Revenue must be a non-negative number"]
        )
    ]

    # Create enhanced master
    enhanced_financial_master = EnhancedMaster(
        name="Enhanced Financial Entity",
        matching_policy=matching_policy,
        mastering_policy=mastering_policy,
        sources=["source_A", "source_B", "source_C"],
        validation_rules=validation_rules
    )

    # Test data
    existing_master_records = [
        {
            "entity_id": "1234",
            "tax_id": "12-3456789",
            "company_name": "Example Corporation",
            "annual_revenue": 1200000,
            "address": "456 Finance Avenue",
            "source": "source_B"
        }
    ]

    # Test the system
    try:
        incoming_record = {
            "entity_id": "1234",
            "tax_id": "12-3456789",
            "company_name": "Example Corp",
            "annual_revenue": 1000000,
            "address": "123 Finance St",
            "source": "source_A"
        }
        
        master_record = enhanced_financial_master.create_master_record(
            incoming_record, existing_master_records
        )
        
        print("\nMaster Record Created:", master_record)
        print("\nAudit Trail:")
        for log in enhanced_financial_master.audit_logs:
            print(f"{log.timestamp}: {log.action} on {log.entity_id}")
            print(f"Changes: {log.changes}")
            
    except ValueError as e:
        print(f"Validation error: {e}")