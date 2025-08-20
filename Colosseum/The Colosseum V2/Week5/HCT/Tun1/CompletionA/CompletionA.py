hct_outcome_variables = {
    "patient_characteristics": {
        "demographics": [
            "r_age",
            "r_sex",
            "d_age",
            "adult",
            "bmi",
            "bmipct",
            "did_rollup_race",
            "rid_rollup_race",
            "d_ethn",
            "country"
        ],
        "medical_history": [
            "d_num_preg",
            "d_preg",
            "d_abo_rh"
        ]
    },
    
    "disease_characteristics": {
        "diagnosis": [
            "condclas",     # Disease classification
            "condgrp",      # Disease group
            "mdsdist",      # MDS distribution
            "cmldist",      # CML distribution
            "lymsubgp",     # Lymphoma subgroup
            "amlrxrel",     # AML relapse
            "cytogener",    # Cytogenetics
            "flt3_itd"      # FLT3 mutation status
        ],
        "disease_status": [
            "datedx",       # Date of diagnosis
            "subdis2",      # Disease subset
            "myeissdx"      # Myeloid disease
        ]
    },
    
    "donor_characteristics": {
        "matching": {
            "hla_typing": [
                "d_drb1_typ1_1",
                "d_dpb1_typ1",
                "d_dqb1_typ1",
                "d_dqa1_typ1",
                "d_a_typ1_1",
                "d_b_typ1",
                "d_c_typ1"
            ],
            "matching_scores": [
                "himatchdrb1_1",
                "himatchdqb1_1",
                "himatchdpb1_1",
                "lomatchdrb1",
                "lomatchdqb1_1",
                "lomatchdpb1"
            ]
        },
        "donor_info": [
            "dnrtype",
            "donorgpnew",
            "d_sex",
            "bmpbdsex"      # Bone marrow/peripheral blood donor sex
        ]
    },
    
    "transplant_characteristics": {
        "procedure": [
            "txtype",           # Transplant type
            "yearoftx",         # Year of transplant
            "invivotcd",        # In vivo T-cell depletion
            "pttxtype",         # Patient transplant type
            "infus_product"     # Infusion product
        ],
        "timing": [
            "datetx",           # Date of transplant
            "consentdt"         # Consent date
        ]
    }
}
