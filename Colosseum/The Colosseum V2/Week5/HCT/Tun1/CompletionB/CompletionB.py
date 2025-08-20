patient_related_variables = {
    'Demographics': [
        'r_age',           # Recipient's age  
        'r_sex',           # Recipient's sex  
        'adult',           # Indicator of adulthood  
        'd_age',           # Donor's age  
        'd_sex',           # Donor's sex  
        'd_ethn',          # Donor's ethnicity  
        'd_abo_rh',        # Donor's ABO blood type and Rh factor  
        'd_num_preg',      # Donor's number of pregnancies  
        'bmipct',          # BMI percentile  
        'bmi',             # Body Mass Index  
        'country',         # Country of origin or residence  
        'zipmean',         # Mean ZIP code area indicator  
        'zipmedian',       # Median ZIP code area indicator  
    ],
}
disease_related_variables = {
    'Disease Classification & Subtypes': [
        'cmldist',         # Chronic myeloid leukemia distribution  
        'mdsdist',         # Myelodysplastic syndrome distribution  
        'lymdist',         # Lymphoma distribution  
        'lymsubgp',        # Lymphoma subgroup  
        'amlrxrel',        # Acute myeloid leukemia relapse status  
        'mkmds',           # Marker associated with MDS  
        'mkaml',           # Marker associated with AML  
        'myeissdx',        # Myeloid disease subtype  
        'mdsrxrel',        # Myelodysplastic syndrome relapse  
        'cmltkipr',        # TKI-resistant chronic myeloid leukemia profile  
    ],
    'Disease Cytogenetics': [
        'cytogener',       # General cytogenetic risk  
        'cytogeneeln',     # Extended cytogenetic analysis  
    ],
    'Disease Group & Classification': [
        'condclas',        # Disease classification  
        'condgrp',         # Disease group  
    ],
}
hla_matching_variables = {
    'HLA-A Typing': [
        'd_a_typ1_1', 'd_a_typ2', 'd_a_typ2_2'
    ],
    'HLA-B Typing': [
        'd_b_typ1', 'd_b_typ1_2', 'd_b_typ2', 'd_b_typ2_1', 'd_b_typ2_2'
    ],
    'HLA-C Typing': [
        'd_c_typ1', 'd_c_typ1_1', 'd_c_typ2', 'd_c_typ2_1', 'd_c_typ2_2'
    ],
    'HLA-DRB Typing': [
        'r_drb1_typ1', 'd_drb1_typ1_1', 'r_drb3_typ1', 'r_drb4_typ1', 'r_drb5_typ1',
        'd_drb1_typ2', 'd_drb1_typ2_1', 'r_drb3_typ2', 'r_drb4_typ2'
    ],
    'HLA-DPB Typing': [
        'r_dpb1_typ1', 'r_dpb1_typ2', 'r_dpb1_typ2', 'd_dpb1_typ1',
        'd_dpb1_typ1_1', 'd_dpb1_typ1_2', 'd_dpb1_typ2_1', 'd_dpb1_typ2_2'
    ],
    'HLA-DQB Typing': [
        'd_dqb1_typ1', 'd_dqb1_typ2', 'd_dqb1_typ2_1', 'd_dqb1_typ2_2'
    ],
    'Serological Mismatches & Compatibility': [
        'dpb1sermis_gvh', 'dpb1sermis_hvg', 'dqa1sermis_gvh', 'dqa1sermis_hvg',
        'dqb1sermis_gvh', 'dqb1sermis_hvg', 'drb1sermis_gvh', 'drb1sermis_hvg',
        'bsermis', 'dqa1sermis'
    ],
}
transplant_related_variables = {
    'Transplant Type & Year': [
        'txtype',           # Type of transplant  
        'yearoftx',         # Year of transplantation  
    ],
    'Donor Type & Relationship': [
        'dnrtype',          # Donor type  
        'dnr_type',         # Donor category  
        'donorgpnew',       # Updated donor group  
        'donorgpnew_update' # Newly updated donor group  
    ],
    'Graft Source & Processing': [
        'apgcsf',           # G-CSF induced graft  
        'invivotcd',        # In vivo T-cell depletion  
    ],
    'Patient & Donor ABO Compatibility': [
        'rcmvpr',           # CMV status  
        'd_abo_rh'          # Donor ABO and Rh blood type  
    ]
}
pre_transplant_treatment_and_status = {
    'Disease Status & Pre-treatment': [
        'autochem',         # Chemotherapy administered before transplant  
    ],
}
miscellaneous_variables = {
    'Geographical & Environmental': [
        'country',          # Country of patient  
        'zipmean',          # ZIP code area mean  
        'zipmedian'         # ZIP code area median  
    ],
    'Socioeconomic & Genetic': [
        'cvapr',            # Cardiovascular risk  
        'dlco65pr',         # Pulmonary function test  
    ],
    'Hematological & Cellular Markers': [
        'flt3_itd',         # FLT3 internal tandem duplication mutation  
    ],
}
important_variables_by_category = {
    'Patient_Related': patient_related_variables,
    'Disease_Related': disease_related_variables,
    'HLA_Matching': hla_matching_variables,
    'Transplant_Related': transplant_related_variables,
    'Pre_Transplant_Treatment_and_Status': pre_transplant_treatment_and_status,
    'Miscellaneous': miscellaneous_variables
}
