import pytest
from unittest.mock import MagicMock, patch
import os

# The function to be tested is defined here
def get_list_of_doctors_with_jobs():
    primaryKey = "ListDoctorHasJobs"
    secondaryKey = "allDoctors"

    table = get_lookup_table()
    currentItem = table.get_item(
        Key={
            'jobs': primaryKey,
            'doctorId': secondaryKey
        },
        AttributesToGet=['details']
    )
    return currentItem.get("Item")

def get_lookup_table():
    # This function should return the DynamoDB table object
    pass

# The test function
def test_get_list_of_doctors_with_jobs(mocker):
    # Mock get_lookup_table to return a MagicMock object for the DynamoDB table
    mockedTable = MagicMock()
    mocker.patch(__name__ + '.get_lookup_table', return_value=mockedTable)
    
    # Define the mock response for get_item
    mockResponse = {
        'Item': {
            'details': 'Details about doctors with jobs'
        }
    }
    mockedTable.get_item.return_value = mockResponse
    
    # Execute the function
    result = get_list_of_doctors_with_jobs()
    
    # Assert the get_item was called correctly
    mockedTable.get_item.assert_called_once_with(
        Key={
            'jobs': 'ListDoctorHasJobs',
            'doctorId': 'allDoctors'
        },
        AttributesToGet=['details']
    )
    
    # Assert that the function returns the correct item
    assert result == 'Details about doctors with jobs', "The function should return the details of doctors with jobs"

# Testing in an environment where host origin might need to be mocked
@patch.dict(os.environ, {"AWS_EXECUTION_ENV": "lambda-host-testing"})
def test_with_mocked_host_origin(mocker):
    # This test ensures that the function behaves correctly when the host origin is mocked as required.
    test_get_list_of_doctors_with_jobs(mocker)
