import unittest
from datetime import datetime
from typing import Dict, List
from unittest.mock import patch

# Import the classes and functions from the main module
from testable_ideal_completion import (
    MatchingRule, MatchingPolicy, FieldSource, MasteringPolicy,
    ValidationRule, EnhancedMaster, compute_similarity,
    is_valid_tax_id, is_valid_revenue
)

class TestFinancialMasterSystem(unittest.TestCase):
    def setUp(self):
        # This Sets up test fixtures before each test method.
        # It creates the basic matching policy
        self.matching_policy = MatchingPolicy(
            name="Test Matching",
            rules=[
                MatchingRule(field="entity_id", operator="equals"),
                MatchingRule(field="tax_id", operator="equals"),
                MatchingRule(field="company_name", operator="similarity", threshold=0.5)
            ]
        )

        # It creates the basic mastering policy
        self.mastering_policy = MasteringPolicy(
            name="Test Mastering",
            field_sources=[
                FieldSource(field="company_name", sources=["source_A", "source_B"]),
                FieldSource(field="annual_revenue", sources=["source_B", "source_A"]),
                FieldSource(field="address", sources=["source_A", "source_B"])
            ]
        )

        # It creates the validation rules
        self.validation_rules = [
            ValidationRule(
                field="tax_id",
                checks=[is_valid_tax_id],
                error_messages=["Invalid tax ID format"]
            ),
            ValidationRule(
                field="annual_revenue",
                checks=[is_valid_revenue],
                error_messages=["Invalid revenue value"]
            )
        ]

        # It creates the  master instance
        self.master = EnhancedMaster(
            name="Test Financial Entity",
            matching_policy=self.matching_policy,
            mastering_policy=self.mastering_policy,
            sources=["source_A", "source_B"],
            validation_rules=self.validation_rules
        )

        # It Sample valid record
        self.valid_record = {
            "entity_id": "1234",
            "tax_id": "12-3456789",
            "company_name": "Test Company",
            "annual_revenue": 1000000,
            "address": "123 Test St",
            "source": "source_A"
        }

    def test_compute_similarity(self):
        # It tests string similarity computation
        # It Verifies that the exact match returns perfect similarity score
        self.assertEqual(compute_similarity("ABC", "ABC"), 1.0)
        
        # It Verifies that the completely different strings return zero similarity
        self.assertEqual(compute_similarity("ABC", "DEF"), 0.0)
        
        # It verifies that the empty string comparison returns zero similarity
        self.assertEqual(compute_similarity("", "ABC"), 0.0)
        
        # It verifies that the partial string matches return appropriate similarity scores
        self.assertAlmostEqual(compute_similarity("Test Corp", "Test Company"), 0.6, delta=0.1)

    def test_matching_policy(self):
        # THIS tests the matching policy functionality
        record1 = self.valid_record.copy()
        record2 = self.valid_record.copy()
        
        # It verifies that the identical records are considered a match
        self.assertTrue(self.matching_policy.matches(record1, record2))
        
        # It verifies that the records with different entity IDs are not matched
        record2["entity_id"] = "5678"
        self.assertFalse(self.matching_policy.matches(record1, record2))
        
        # It verifies that the records with similar company names but matching entity IDs are considered matches
        record2["entity_id"] = record1["entity_id"]
        record2["company_name"] = "Test Corporation"
        self.assertTrue(self.matching_policy.matches(record1, record2))

    def test_mastering_policy(self):
        # THis tests mastering policy consolidation
        record1 = self.valid_record.copy()
        record2 = self.valid_record.copy()
        record2["source"] = "source_B"
        record2["company_name"] = "Test Corp B"
        
        # It verifies that the source prioritization rules are followed during consolidation
        consolidated = self.mastering_policy.consolidate([record1, record2])
        
        # It verifies that the source_A (higher priority) company name is chosen
        self.assertEqual(consolidated["company_name"], "Test Company")
        
        # It verifies that the required fields are present in consolidated record
        self.assertIn("annual_revenue", consolidated)
        self.assertIn("address", consolidated)

    def test_validation_rules(self):
        # It tests the validation rules
        # It verifies that the valid record passes all validation checks
        errors = self.master.validate_record(self.valid_record)
        self.assertEqual(len(errors), 0)
        
        # It verifies that the invalid tax ID format triggers validation error
        invalid_record = self.valid_record.copy()
        invalid_record["tax_id"] = "123-456"
        errors = self.master.validate_record(invalid_record)
        self.assertEqual(len(errors), 1)
        
        # It verifies that the negative revenue triggers validation error
        invalid_record = self.valid_record.copy()
        invalid_record["annual_revenue"] = -1000
        errors = self.master.validate_record(invalid_record)
        self.assertEqual(len(errors), 1)

    def test_create_master_record_new(self):
        # It tests the creation of new master record.
        existing_masters: List[Dict] = []
        
        # It verifies that the new master record is created when no matches exist
        master_record = self.master.create_master_record(
            self.valid_record, existing_masters
        )
        
        # It verifies that the master record contains correct data
        self.assertIsNotNone(master_record)
        self.assertEqual(master_record["entity_id"], "1234")
        
        # It verifies that the audit log creation for new record
        self.assertEqual(len(self.master.audit_logs), 1)
        self.assertEqual(self.master.audit_logs[0].action, "CREATE")

    def test_create_master_record_update(self):
        # It tests the updating existing master record.
        existing_masters = [self.valid_record.copy()]
        
        # It creates the updated version of existing record
        updated_record = self.valid_record.copy()
        updated_record["annual_revenue"] = 2000000
        
        # It verifies that the master record is updated when match exists
        master_record = self.master.create_master_record(
            updated_record, existing_masters
        )
        
        # It verifies that the update was logged correctly
        self.assertIsNotNone(master_record)
        self.assertEqual(len(self.master.audit_logs), 1)
        self.assertEqual(self.master.audit_logs[0].action, "UPDATE")

    def test_audit_logging(self):
        # It tests the audit logging functionality.
        existing_masters = [self.valid_record.copy()]
        
        # It creates the record with multiple field changes
        updated_record = self.valid_record.copy()
        updated_record["annual_revenue"] = 2000000
        updated_record["address"] = "456 New St"
        
        master_record = self.master.create_master_record(
            updated_record, existing_masters
        )
        
        # It verifies that the audit log captures all changes correctly
        self.assertEqual(len(self.master.audit_logs), 1)
        log = self.master.audit_logs[0]
        self.assertEqual(log.entity_id, "1234")
        self.assertEqual(log.source, "source_A")
        self.assertIsInstance(log.timestamp, datetime)
        self.assertIn("annual_revenue", log.changes)
        self.assertIn("address", log.changes)

    def test_invalid_record_handling(self):
        # It tests the handling of invalid records.
        # It creates the record with multiple validation errors
        invalid_record = self.valid_record.copy()
        invalid_record["tax_id"] = "invalid-id"
        invalid_record["annual_revenue"] = -1000
        
        # It verifies that the invalid record raises appropriate exception
        with self.assertRaises(ValueError) as context:
            self.master.create_master_record(invalid_record, [])
        
        # It verifies that the error message contains validation failure information
        self.assertTrue("Validation failed" in str(context.exception))

if __name__ == '__main__':
    unittest.main(verbosity=2)