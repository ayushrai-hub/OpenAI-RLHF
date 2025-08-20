import pytest
from unittest.mock import Mock, MagicMock, patch
import os

# Import the function to test
from your_module import get_list_of_doctors_with_jobs


@patch("your_module.get_lookup_table")
def test_get_list_of_doctors_with_jobs(mock_get_lookup_table):
    # Mock the DynamoDB table
    mock_table = Mock()
    mock_get_lookup_table.return_value = mock_table

    # Create mock return value for get_item
    mock_table.get_item.return_value = {
        "Item": {"details": "some doctor job details"}
    }

    # Call the function
    result = get_list_of_doctors_with_jobs()

    # Assert that the table "get_item" method was called with correct arguments
    mock_table.get_item.assert_called_once_with(
        Key={
            'jobs': 'ListDoctorHasJobs',
            'doctor_id': 'allDoctors'
        },
        AttributesToGet=['details']
    )

    # Assert the function returns the expected result
    assert result == {"details": "some doctor job details"}

    # Test case where get_item returns no Item
    mock_table.get_item.return_value = {}
    result = get_list_of_doctors_with_jobs()

    # Assert the result is None when no Item is returned
    assert result is None
