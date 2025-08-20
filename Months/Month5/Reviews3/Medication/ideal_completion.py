#ideal_completion.py
from collections import defaultdict

# Function to split text into sections
def split_text_into_sections(text):
    return text.split("\n")

# Function to verify if a label exists in a section based on its range
def label_in_section(label, section):
    return label['start'] >= section['start'] and label['end'] <= section['end']

# Modify the function to initialize a medication with lists for values
def initialize_medication_information():
    return {
        'ade': [],
        'dosage': [],
        'duration': [],
        'form': [],
        'frequency': [],
        'reason': [],
        'route': [],
        'strength': []
    }

# Primary function to process the dataset and extract medication details
def extract_medication_details(dataset):
    output_list = []
    
    connection_names = dataset['train_features']['connections'][0]['relation']['names']
    label_names = dataset['train_features']['labels'][0]['label']['names']

    # Iterate through each entry in the dataset
    for entry in dataset['train']:
        sections = split_text_into_sections(entry['text'])
        connections = entry['connections']
        labels = entry['labels']

        section_spans = []
        for index, section in enumerate(sections):
            start_pos = entry['text'].find(section)
            end_pos = start_pos + len(section)
            section_spans.append({'index': index, 'start': start_pos, 'end': end_pos, 'text': section})
        
        # List to keep track of processed sections
        merged_sections = []
        
        # Go through sections to look for medications and their related data
        for sec in section_spans:
            meds_in_section = defaultdict(initialize_medication_information)
            meds_in_associated_sections = []
            
            # Check labels to find medications in this section
            for label in labels:
                if label_names[label['label']] == 'Drug' and label_in_section(label, sec):
                    medication_name = label['text']
                    # Check connections for this medication
                    for connection in connections:
                        if connection['arg2_id'] == label['id']:
                            # Find the associated label (arg1_id)
                            associated_label = next((lbl for lbl in labels if lbl['id'] == connection['arg1_id']), None)
                            if associated_label and label_in_section(associated_label, sec):
                                connection_type = connection_names[connection['relation']].split('-')[0].lower()
                                meds_in_section[medication_name][connection_type].append(associated_label['text'])
                            else:
                                # Check if the connection exists in another section
                                associated_section = next((section for section in section_spans if label_in_section(associated_label, section)), None)
                                if associated_section and associated_section not in merged_sections:
                                    meds_in_associated_sections.append(associated_section)
            
            # Merge associated sections if applicable
            if meds_in_associated_sections:
                related_content = ' '.join([section['text'] for section in meds_in_associated_sections])
                sec['text'] += " " + related_content
                merged_sections.extend(meds_in_associated_sections)

            # If medications are found, convert single items to strings and keep lists as is
            for med_name, details in meds_in_section.items():
                for key, value in details.items():
                    if len(value) == 1:
                        meds_in_section[med_name][key] = value[0]
            
            # If medications are found, add to output_list
            if meds_in_section:
                output_list.append({'text': sec['text'], **meds_in_section})
    
    return output_list


# Updated Sample Dataset with Exact Text and Correct Labels
dataset = {
    'train': [
        {
            'text': '''Her BB was raised to 25 [**Clinic1 **] due to temporary low heart rate to mid 60s, digoxin was stopped and simvastatin reduced to 150 mg [**Clinic1 **]. 
                       Given this treatment, HR stayed within the expected range. The patient will be monitored, and atenolol was adjusted to 50 mg for better blood pressure control.''',
            'connections': [
                {'id': 'rel1', 'arg1_id': 'id1', 'arg2_id': 'id3', 'relation': 7},  # Strength-Drug (25 mg for BB)
                {'id': 'rel2', 'arg1_id': 'id2', 'arg2_id': 'id3', 'relation': 7},  # Strength-Drug (60 for BB)
                {'id': 'rel3', 'arg1_id': 'id4', 'arg2_id': 'id5', 'relation': 7},  # Strength-Drug (150 mg for Simvastatin)
                {'id': 'rel4', 'arg1_id': 'id6', 'arg2_id': 'id7', 'relation': 4},  # Form-Drug for Digoxin (stopped)
                {'id': 'rel5', 'arg1_id': 'id8', 'arg2_id': 'id5', 'relation': 4},  # Form-Drug for Simvastatin (reduced)
                {'id': 'rel6', 'arg1_id': 'id10', 'arg2_id': 'id9', 'relation': 7}  # Strength-Drug for Atenolol (50 mg)
            ],
            'labels': [
                {'id': 'id1', 'text': '25', 'start': 19, 'end': 21, 'label': 8},  # Strength (BB)
                {'id': 'id2', 'text': '60', 'start': 53, 'end': 55, 'label': 8},  # Strength (BB)
                {'id': 'id3', 'text': 'BB', 'start': 4, 'end': 6, 'label': 2},  # Drug (BB)
                {'id': 'id4', 'text': '150 mg', 'start': 92, 'end': 98, 'label': 8},  # Strength (Simvastatin)
                {'id': 'id5', 'text': 'Simvastatin', 'start': 75, 'end': 87, 'label': 2},  # Drug
                {'id': 'id6', 'text': 'stopped', 'start': 61, 'end': 68, 'label': 4},  # Form (Digoxin)
                {'id': 'id7', 'text': 'Digoxin', 'start': 48, 'end': 55, 'label': 2},  # Drug (Digoxin)
                {'id': 'id8', 'text': 'reduced', 'start': 88, 'end': 95, 'label': 4},  # Form (Simvastatin)
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