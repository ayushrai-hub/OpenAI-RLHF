import pytest
from unittest.mock import patch, MagicMock
from my_module import get_list_of_doctors_with_jobs  # Replace 'my_module' with the name of your module

@patch('my_module.get_lookup_table')
def test_get_list_of_doctors_with_jobs(mock_get_lookup_table):
    # Mock the table object returned by get_lookup_table
    mock_table = MagicMock()
    mock_get_lookup_table.return_value = mock_table
    
    # Mock the get_item return value
    mock_table.get_item.return_value = {
        "Item": {
            "details": "Sample doctor details"
        }
    }
    
    # Call the function
    result = get_list_of_doctors_with_jobs()
    
    # Check if the right arguments were passed to get_item
    mock_table.get_item.assert_called_once_with(
        Key={'jobs': "ListDoctorHasJobs", 'doctor_id': "allDoctors"},
        AttributesToGet=['details']
    )
    
    # Check the function returns the correct item
    assert result == {'details': "Sample doctor details"}

@patch('my_module.get_lookup_table')
def test_get_list_of_doctors_with_jobs_no_item(mock_get_lookup_table):
    # Mock the table object returned by get_lookup_table
    mock_table = MagicMock()
    mock_get_lookup_table.return_value = mock_table
    
    # Mock the get_item return value with no "Item"
    mock_table.get_item.return_value = {}
    
    # Call the function
    result = get_list_of_doctors_with_jobs()
    
    # Check if the right arguments were passed to get_item
    mock_table.get_item.assert_called_once_with(
        Key={'jobs': "ListDoctorHasJobs", 'doctor_id': "allDoctors"},
        AttributesToGet=['details']
    )
    
    # Check the function handles missing Item correctly
    assert result is None
