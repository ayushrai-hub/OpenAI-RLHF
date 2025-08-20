essential_variables_HCT_outcomes = {
    "patient_characteristics": {
        "demographics": [
            "d_age",              # Patient age
            "d_sex",              # Patient sex
            "adult",              # Adult status
            "d_ethn",             # Ethnicity
            "d_abo_rh",           # Blood type (ABO/Rh system)
            "bmi",                # Body Mass Index
            "d_num_preg",         # Number of pregnancies
        ],
        "clinical": [
            "dlco65pr",           # Diffusing capacity of lungs (pulmonary function)
            "lymdist",            # Distribution of lymphoma
            "cmldist",            # Chronic myeloid leukemia distribution
            "mdsdist",            # Myelodysplastic syndrome distribution
            "cytogener",          # Cytogenetics report
            "flt3_itd",           # FLT3 ITD mutation status
        ],
    },
    
    "donor_characteristics": {
        "demographics": [
            "r_age",              # Donor age
            "r_sex",              # Donor sex
            "dnrtype",            # Donor type (related/unrelated)
            "donorgpnew",         # Updated donor group classification
        ],
        "hla_typing": [
            "d_a_typ1",           # HLA-A type 
            "d_b_typ1",           # HLA-B type
            "d_c_typ1",           # HLA-C type
            "d_dqa1_typ1",        # HLA-DQA1 type
            "d_dqb1_typ1",        # HLA-DQB1 type
            "d_drb1_typ1",        # HLA-DRB1 type
            "d_drb3_typ1",        # HLA-DRB3 type
            "d_dpb1_typ1",        # HLA-DPB1 type
            "lomatchdrb1",        # Low match probability for DRB1
        ],
    },
    
    "transplant_specifics": {
        "pre_transplant_factors": [
            "txtype",               # Type of transplant
            "pttxtype",             # Patient transplant type
            "gvhprhrxgp",           # GVHD prophylaxis regimen group (pre-transplant)
        ],  
        "matching_details": [
            "himatchdrb1_gvh",      # High match DRB1 versus GVH
            "lomatchdpb1",          # Low match probability DPB1
            "himatchc_hvg",         # High match C against HVG
        ],
    },

    "pre_transplant_treatment": {
        "conditioning": [
            "autochem",             # Chemotherapy used pre-transplant
            "cvapr",                # Cardiovascular pre-transplant factors
            "ritux",                # Rituximab therapy pre-transplant
            "funghxpr",             # Pre-transplant antifungal therapy  
        ],
        "additional_medical": [
            "hepmilpr",             # Hepatic pre-transplant issues
            "arrhytpr",             # Arrhythmia pre-transplant report
            "bowelpr",              # Bowel-related pre-transplant details
        ],
    },

    "socio_geographical_factors": [
        "zipmedian",                # Median zip code income
        "country",                  # Country
    ],
}
