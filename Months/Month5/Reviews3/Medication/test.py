import unittest
from ideal_completion import extract_medication_details 

class TestExtractMedicationDetails(unittest.TestCase):

    def setUp(self):
        # Sample dataset to be used in the tests
        self.dataset = {
            'train': [
                {
                    'text': '''Her BB was raised to 25 [**Clinic1 **] due to temporary low heart rate to mid 60s, digoxin was stopped and simvastatin reduced to 150 mg [**Clinic1 **]. 
                               Given this treatment, HR stayed within the expected range. The patient will be monitored, and atenolol was adjusted to 50 mg for better blood pressure control.''',
                    'connections': [
                        {'id': 'rel1', 'arg1_id': 'id1', 'arg2_id': 'id3', 'relation': 7},  # Strength-Drug (25 mg for BB)
                        {'id': 'rel2', 'arg1_id': 'id2', 'arg2_id': 'id3', 'relation': 7},  # Strength-Drug (60 for BB)
                        {'id': 'rel3', 'arg1_id': 'id4', 'arg2_id': 'id5', 'relation': 7},  # Strength-Drug (150 mg for Simvastatin)
                        {'id': 'rel4', 'arg1_id': 'id6', 'arg2_id': 'id7', 'relation': 4},  # Frequency-Drug for Digoxin (stopped)
                        {'id': 'rel5', 'arg1_id': 'id8', 'arg2_id': 'id5', 'relation': 4},  # Frequency-Drug for Simvastatin (reduced)
                        {'id': 'rel6', 'arg1_id': 'id10', 'arg2_id': 'id9', 'relation': 7}  # Strength-Drug for Atenolol (50 mg)
                    ],
                    'labels': [
                        {'id': 'id1', 'text': '25', 'start': 19, 'end': 21, 'label': 8},  # Strength (BB)
                        {'id': 'id2', 'text': '60', 'start': 53, 'end': 55, 'label': 8},  # Strength (BB)
                        {'id': 'id3', 'text': 'BB', 'start': 4, 'end': 6, 'label': 2},  # Drug (BB)
                        {'id': 'id4', 'text': '150 mg', 'start': 92, 'end': 98, 'label': 8},  # Strength (Simvastatin)
                        {'id': 'id5', 'text': 'Simvastatin', 'start': 75, 'end': 87, 'label': 2},  # Drug
                        {'id': 'id6', 'text': 'stopped', 'start': 61, 'end': 68, 'label': 4},  # Frequency (Digoxin)
                        {'id': 'id7', 'text': 'Digoxin', 'start': 48, 'end': 55, 'label': 2},  # Drug (Digoxin)
                        {'id': 'id8', 'text': 'reduced', 'start': 88, 'end': 95, 'label': 4},  # Frequency (Simvastatin)
                        {'id': 'id9', 'text': 'Atenolol', 'start': 185, 'end': 193, 'label': 2},  # Drug (Atenolol)
                        {'id': 'id10', 'text': '50 mg', 'start': 195, 'end': 200, 'label': 8}  # Strength (Atenolol)
                    ]
                }
            ],
            'train_features': {
                'connections': [{'relation': {'names': ['ADE-Drug', 'Dosage-Drug', 'Duration-Drug', 'Form-Drug', 'Frequency-Drug', 'Reason-Drug', 'Route-Drug', 'Strength-Drug']}}],
                'labels': [{'label': {'names': ['ADE', 'Dosage', 'Drug', 'Duration', 'Form', 'Frequency', 'Reason', 'Route', 'Strength']}}]
            }
        }

    def test_output_contains_all_fields(self):
        # Run the function to process the data
        output = extract_medication_details(self.dataset)

        required_fields = ['ade', 'dosage', 'duration', 'form', 'frequency', 'reason', 'route', 'strength']

        # Check all fields exist and are properly initialized (empty or populated) for each drug
        for item in output:
            for drug, details in item.items():
                if drug == 'text':
                    continue
                # Ensure all required fields are in the output
                for field in required_fields:
                    self.assertIn(field, details)
                    # All fields should be lists or strings, empty fields can be empty lists or empty strings
                    self.assertIsInstance(details[field], (list, str))
                    if isinstance(details[field], list):
                        self.assertTrue(all(isinstance(i, str) for i in details[field]))  # Ensure all elements in lists are strings

    def test_multiple_strengths_for_BB(self):
        # Check that BB has multiple strengths
        output = extract_medication_details(self.dataset)
        
        for item in output:
            if 'BB' in item:
                bb_data = item['BB']
                # Strength should be a list with two entries
                self.assertTrue(isinstance(bb_data['strength'], list))
                self.assertEqual(len(bb_data['strength']), 2)
                self.assertEqual(bb_data['strength'], ['25', '60'])  # Both 25 and 60 mg should be present

    def test_correct_frequency_for_simvastatin(self):
        # Check that Simvastatin has the correct frequency
        output = extract_medication_details(self.dataset)
        
        for item in output:
            if 'Simvastatin' in item:
                simvastatin_data = item['Simvastatin']
                if isinstance(simvastatin_data['frequency'], list):
                    self.assertEqual(simvastatin_data['frequency'], ['reduced']) 
                else:
                    self.assertEqual(simvastatin_data['frequency'], 'reduced')

    def test_correct_strength_for_simvastatin(self):
        # Check that Simvastatin has the correct strength
        output = extract_medication_details(self.dataset)
        
        for item in output:
            if 'Simvastatin' in item:
                simvastatin_data = item['Simvastatin']
                self.assertTrue(isinstance(simvastatin_data['strength'], (str, list)))
                if isinstance(simvastatin_data['strength'], list):
                    self.assertEqual(simvastatin_data['strength'], ['150 mg'])  # Simvastatin strength should be 150 mg
                else:
                    self.assertEqual(simvastatin_data['strength'], '150 mg')

    def test_correct_frequency_for_digoxin(self):
        # Check that Digoxin has the correct frequency
        output = extract_medication_details(self.dataset)
        
        for item in output:
            if 'Digoxin' in item:
                digoxin_data = item['Digoxin']
                if isinstance(digoxin_data['frequency'], list):
                    self.assertEqual(digoxin_data['frequency'], ['stopped']) 
                else:
                    self.assertEqual(digoxin_data['frequency'], 'stopped')
                

    def test_correct_strength_for_atenolol(self):
        # Check that Atenolol has the correct strength
        output = extract_medication_details(self.dataset)

        for item in output:
            if 'Atenolol' in item:
                atenolol_data = item['Atenolol']
                self.assertTrue(isinstance(atenolol_data['strength'], (str, list)))
                if isinstance(atenolol_data['strength'], list):
                    self.assertEqual(atenolol_data['strength'], ['50 mg'])  # Atenolol strength should be 50 mg
                else:
                    self.assertEqual(atenolol_data['strength'], '50 mg')

    def test_empty_fields(self):
        # Ensure that the fields which are not populated are empty arrays or empty strings
        output = extract_medication_details(self.dataset)

        for item in output:
            for drug, details in item.items():
                if drug == 'text':
                    continue
                # Check all other fields except 'strength' and 'frequency' should be empty arrays or empty strings
                for field in ['ade', 'dosage', 'duration', 'form', 'reason', 'route']:
                    self.assertTrue(details[field] == [] or details[field] == '')  # Ensure they are empty arrays or empty strings

if __name__ == '__main__':
    unittest.main(verbosity=2)
