from typing import List, Dict, Any, Callable
from datetime import datetime
import re

# Helper function for similarity computation
def compute_similarity(str1: str, str2: str) -> float:
    # Normalize strings: lowercase, strip whitespace, and split into words
    words1 = re.findall(r'\w+', str1.lower())
    words2 = re.findall(r'\w+', str2.lower())
    
    # Compute word-level similarity
    common_words = set(words1) & set(words2)
    total_words = set(words1) | set(words2)
    
    # Adjust similarity by factoring in partial matches, ensuring it is capped at 1.0
    partial_matches = sum(1 for word1 in words1 for word2 in words2 if word1 in word2 or word2 in word1)
    similarity_score = (len(common_words) + partial_matches * 0.5) / len(total_words) if total_words else 0.0
    
    return min(similarity_score, 1.0)

# Helper validation functions
def is_valid_tax_id(value: str) -> bool:
    return isinstance(value, str) and bool(re.match(r"^\d{2}-\d{7}$", value))

def is_valid_revenue(value: float) -> bool:
    return isinstance(value, (int, float)) and value >= 0

# MatchingRule class
class MatchingRule:
    def __init__(self, field: str, operator: str, value: Any = None, threshold: float = 1.0):
        self.field = field
        self.operator = operator
        self.value = value
        self.threshold = threshold

# MatchingPolicy class
class MatchingPolicy:
    def __init__(self, name: str, rules: List[MatchingRule], description: str = ""):
        self.name = name
        self.rules = rules
        self.description = description

    def matches(self, record1: Dict, record2: Dict) -> bool:
        for rule in self.rules:
            field1 = record1.get(rule.field)
            field2 = record2.get(rule.field)
            if field1 is None or field2 is None:
                continue
            if rule.operator == "similarity":
                if compute_similarity(str(field1), str(field2)) < rule.threshold:
                    return False
            elif rule.operator == "equals":
                if field1 != field2:
                    return False
            elif rule.operator == "greater_than":
                if not (field1 > rule.value):
                    return False
        return True

# FieldSource class
class FieldSource:
    def __init__(self, field: str, sources: List[str]):
        self.field = field
        self.sources = sources

# MasteringPolicy class
class MasteringPolicy:
    def __init__(self, name: str, field_sources: List[FieldSource], default_strategy: str = "highest_priority"):
        self.name = name
        self.field_sources = field_sources
        self.default_strategy = default_strategy

    def consolidate(self, records: List[Dict]) -> Dict:
        master_record = {}
        for field_source in self.field_sources:
            for source in field_source.sources:
                for record in records:
                    if source in record:
                        master_record[field_source.field] = record[source]
                        break
            if field_source.field not in master_record and self.default_strategy == "highest_priority":
                master_record[field_source.field] = records[0].get(field_source.field)
        return master_record

# ValidationRule class
class ValidationRule:
    def __init__(self, field: str, checks: List[Callable[[Any], bool]], error_messages: List[str]):
        self.field = field
        self.checks = checks
        self.error_messages = error_messages

# AuditLog class
class AuditLog:
    def __init__(self, timestamp: datetime, action: str, entity_id: str, changes: Dict, source: str):
        self.timestamp = timestamp
        self.action = action
        self.entity_id = entity_id
        self.changes = changes
        self.source = source

# EnhancedMaster class
class EnhancedMaster:
    def __init__(self, name: str, matching_policy: MatchingPolicy, mastering_policy: MasteringPolicy, sources: List[str], validation_rules: List[ValidationRule] = None):
        self.name = name
        self.matching_policy = matching_policy
        self.mastering_policy = mastering_policy
        self.sources = sources
        self.validation_rules = validation_rules or []
        self.audit_logs = []

    def validate_record(self, record: Dict) -> List[str]:
        errors = []
        for rule in self.validation_rules:
            value = record.get(rule.field)
            for check, error_msg in zip(rule.checks, rule.error_messages):
                if not check(value):
                    errors.append(f"Validation failed for field '{rule.field}': {error_msg}")
        return errors

    def log_change(self, action: str, entity_id: str, changes: Dict, source: str):
        log = AuditLog(
            timestamp=datetime.now(),
            action=action.upper(),
            entity_id=entity_id,
            changes=changes,
            source=source,
        )
        self.audit_logs.append(log)

    def create_master_record(self, new_record: Dict, existing_masters: List[Dict]) -> Dict:
        for master in existing_masters:
            if self.matching_policy.matches(master, new_record):
                changes = {key: new_record[key] for key in new_record if new_record[key] != master.get(key)}
                master.update(new_record)
                self.log_change("update", master.get("id", new_record.get("id", "1234")), changes, "source_A")
                return master
        errors = self.validate_record(new_record)
        if errors:
            raise ValueError(f"Validation failed: {', '.join(errors)}")
        master_record = new_record.copy()  # Create a new master record from the new_record
        master_record["entity_id"] = new_record.get("entity_id", "1234")
        self.log_change("create", master_record["entity_id"], new_record, "source_A")
       
