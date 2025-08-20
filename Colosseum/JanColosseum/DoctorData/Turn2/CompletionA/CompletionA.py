import pytest
from unittest.mock import MagicMock, patch

# Mock get_lookup_table and table.get_item
@patch("your_module.get_lookup_table")
def test_get_list_of_doctors_with_jobs(mock_get_lookup_table):
    # Arrange
    mock_table = MagicMock()
    mock_get_lookup_table.return_value = mock_table
    
    # Case 1: Return a valid item
    mock_table.get_item.return_value = {"Item": {"details": "Doctor Details"}}
    
    # Act
    result = get_list_of_doctors_with_jobs()
    
    # Assert
    mock_get_lookup_table.assert_called_once()
    mock_table.get_item.assert_called_once_with(
        Key={'jobs': 'ListDoctorHasJobs', 'doctor_id': 'allDoctors'},
        AttributesToGet=['details']
    )
    assert result == {"details": "Doctor Details"}

@patch("your_module.get_lookup_table")
def test_get_list_of_doctors_with_jobs_no_item(mock_get_lookup_table):
    # Arrange
    mock_table = MagicMock()
    mock_get_lookup_table.return_value = mock_table
    
    # Case 2: Return no item (edge case)
    mock_table.get_item.return_value = {}
    
    # Act
    result = get_list_of_doctors_with_jobs()
    
    # Assert
    mock_get_lookup_table.assert_called_once()
    mock_table.get_item.assert_called_once_with(
        Key={'jobs': 'ListDoctorHasJobs', 'doctor_id': 'allDoctors'},
        AttributesToGet=['details']
    )
    assert result is None
