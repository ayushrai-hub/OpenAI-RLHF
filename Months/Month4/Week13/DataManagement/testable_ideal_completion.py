from dataclasses import dataclass, field
from typing import List, Dict, Callable, Any
from datetime import datetime

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
        for rule in self.rules:
            field = rule.field
            operator = rule.operator
            value = rule.value
            threshold = rule.threshold

            val1 = record1.get(field)
            val2 = record2.get(field)

            if operator == 'equals':
                if val1 != val2:
                    return False
            elif operator == 'contains':
                if val1 is None or val2 is None or val1 not in val2:
                    return False
            elif operator == 'similarity':
                similarity = compute_similarity(val1, val2)
                if similarity < threshold:
                    return False
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
        for field_source in self.field_sources:
            for source in field_source.sources:
                for record in records:
                    if record.get('source') == source and field_source.field in record:
                        master_record[field_source.field] = record[field_source.field]
                        break
                if field_source.field in master_record:
                    break
            else:
                master_record[field_source.field] = None
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

class EnhancedMaster:
    def __init__(self, name: str, matching_policy: MatchingPolicy,
                 mastering_policy: MasteringPolicy, sources: List[str],
                 validation_rules: List[ValidationRule] = None):
        self.name = name
        self.matching_policy = matching_policy
        self.mastering_policy = mastering_policy
        self.sources = sources
        self.validation_rules = validation_rules if validation_rules else []
        self.audit_logs = []

    def validate_record(self, record: Dict) -> List[str]:
        errors = []
        for rule in self.validation_rules:
            for check, error_message in zip(rule.checks, rule.error_messages):
                if not check(record.get(rule.field)):
                    errors.append(error_message)
        return errors

    def log_change(self, action: str, entity_id: str, changes: Dict, source: str):
        self.audit_logs.append(AuditLog(
            timestamp=datetime.now(),
            action=action,
            entity_id=entity_id,
            changes=changes,
            source=source
        ))

    def create_master_record(self, new_record: Dict, existing_masters: List[Dict]) -> Dict:
        matching_records = [
            master for master in existing_masters
            if self.matching_policy.matches(master, new_record)
        ]

        if matching_records:
            all_records = matching_records + [new_record]
            consolidated = self.mastering_policy.consolidate(all_records)
            self.log_change('update', new_record.get('entity_id'), consolidated, new_record.get('source'))
            return consolidated
        else:
            consolidated = self.mastering_policy.consolidate([new_record])
            self.log_change('create', new_record.get('entity_id'), consolidated, new_record.get('source'))
            return consolidated

def compute_similarity(str1: str, str2: str) -> float:
    if not str1 or not str2:
        return 0.0
    common = set(str1.lower()) & set(str2.lower())
    return len(common) / max(len(str1), len(str2))

def is_valid_tax_id(value: str) -> bool:
    return value.isdigit() and len(value) == 9

def is_valid_revenue(value: float) -> bool:
    return isinstance(value, (int, float)) and value >= 0
