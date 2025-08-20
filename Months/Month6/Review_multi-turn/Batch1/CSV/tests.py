import unittest
import csv
import os
import tempfile
from ideal_completion import drop_column_from_csv  # Import the function to test

class TestDropColumnFromCSV(unittest.TestCase):

    def setUp(self):
        # Create a temporary input CSV file for testing
        self.input_file = tempfile.NamedTemporaryFile(delete=False, mode='w', newline='')
        # Create a temporary output file name
        self.output_file_name = tempfile.NamedTemporaryFile(delete=False, mode='w', newline='').name

    def tearDown(self):
        # Remove the temporary files after each test
        os.remove(self.input_file.name)
        os.remove(self.output_file_name)

    def test_drop_existing_column(self):
        """Test dropping an existing column from the CSV."""
        # Write sample data to the input CSV
        self.input_file.write("column_name,other_column\n")
        self.input_file.write("1,value1\n")
        self.input_file.write("2,value2\n")
        self.input_file.write("3,value3\n")
        self.input_file.close()  # Close the file to ensure data is written properly

        # Call the function to drop the specified column
        drop_column_from_csv(self.input_file.name, self.output_file_name, 'column_name')

        # Verify the output CSV content
        with open(self.output_file_name, mode='r', newline='') as outfile:
            reader = csv.DictReader(outfile)
            fieldnames = reader.fieldnames
            
            # Check if the fieldnames exclude the dropped column
            self.assertEqual(fieldnames, ['other_column'])  # Verify fieldnames
            rows = list(reader)
            self.assertEqual(len(rows), 3)  # Verify number of rows
            # Verify the values in the remaining column
            self.assertEqual(rows[0]['other_column'], 'value1')
            self.assertEqual(rows[1]['other_column'], 'value2')
            self.assertEqual(rows[2]['other_column'], 'value3')

    def test_drop_non_existing_column(self):
        """Test attempting to drop a non-existing column from the CSV."""
        # Write sample data to the input CSV
        self.input_file.write("column_name,other_column\n")
        self.input_file.write("1,value1\n")
        self.input_file.write("2,value2\n")
        self.input_file.write("3,value3\n")
        self.input_file.close()  # Close the file to ensure data is written properly

        # Call the function to attempt dropping a non-existing column
        drop_column_from_csv(self.input_file.name, self.output_file_name, 'non_existing_column')

        # Verify the output CSV content
        with open(self.output_file_name, mode='r', newline='') as outfile:
            reader = csv.DictReader(outfile)
            fieldnames = reader.fieldnames
            
            # Check if fieldnames remain unchanged
            self.assertEqual(fieldnames, ['column_name', 'other_column'])  # Verify fieldnames
            rows = list(reader)
            self.assertEqual(len(rows), 3)  # Verify number of rows
            # Verify the values remain unchanged
            self.assertEqual(rows[0]['column_name'], '1')
            self.assertEqual(rows[0]['other_column'], 'value1')

    def test_empty_csv(self):
        """Test behavior when the input CSV is empty."""
        # Close the empty input file
        self.input_file.close()  # Ensure the file is closed

        # Call the function with the empty input file
        drop_column_from_csv(self.input_file.name, self.output_file_name, 'column_name')

        # Verify the output CSV content is also empty
        with open(self.output_file_name, mode='r', newline='') as outfile:
            reader = csv.reader(outfile)
            rows = list(reader)
            
            # Check that the output is empty
            self.assertEqual(rows, [])  # Ensure output file is also empty

if __name__ == '__main__':
    unittest.main(verbosity=2) 