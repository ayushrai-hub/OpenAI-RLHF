
import pandas as pd
import numpy as np
import itertools

def calculate_food_benefit(dataset: pd.DataFrame, foodData: pd.DataFrame) -> pd.Series:
    # Step 1: Update to the latest benefit rules if current year's updates are missing
    all_years = dataset['ruleYear'].unique()
    data_years_available = foodData['ruleYear'].unique()
    years_needed_mask = np.isin(all_years, data_years_available, invert=True)
    years_needed = all_years[years_needed_mask]

    # Project forward with future data
    max_year_with_data = foodData['ruleYear'].max()
    future_years = years_needed[years_needed > max_year_with_data]
    
    if len(future_years) > 0:
        # Generate dataframe for future years
        future_frame = pd.DataFrame(
            list(itertools.product(foodData['stateFIPS'].unique(), foodData['famsize'].unique(), future_years)),
            columns=['stateFIPS', 'famsize', 'Year']
        )

        # Merge last available data
        merge_data = foodData[foodData['ruleYear'] == max_year_with_data]
        future_frame = future_frame.merge(merge_data, on=['stateFIPS', 'famsize'], how='left') \
                                   .drop(columns='ruleYear').rename(columns={"Year": "ruleYear"})

        # Attach both projected and historical benefit information
        foodData = pd.concat([foodData, future_frame], ignore_index=True)

    # Join historical rules
    dataset = pd.merge(dataset, foodData, on=['ruleYear', 'stateFIPS', 'famsize'], how='left')

    # Step A: Calculate total countable income
    income_columns = ['income', 'income.gifts', 'income.childSupport', 'income.investment', 
                      'value.stipend', 'value.support', 'value.assistance']
    dataset['incomeGross'] = dataset[income_columns].sum(axis=1, skipna=True)

    # Check for elderly or disabled household members
    disability_cols = [f'disability_{i}' for i in range(1, 13)]
    age_cols = [f'ageMember{i}' for i in range(1, 13)]
    dataset['disabledNumber'] = (dataset[disability_cols].fillna(0) == 1).sum(axis=1)
    dataset['elderlyNumber'] = (dataset[age_cols] > 60).sum(axis=1)
    dataset['kidNumber'] = (dataset[age_cols] < 19).sum(axis=1)

    # Step I: Earned income reduction
    dataset['EarnedIncomeReduction'] = 0.2 * dataset['income']

    # Step II: Adjusted income
    dataset['adjIncome'] = (dataset['incomeGross'] - dataset['EarnedIncomeReduction']
                            - 12 * dataset['StandardReduction'] - dataset['netexp.childcare']).clip(lower=0)

    # Step III: Utility Deductions
    conditions_mandatory = (
        (dataset['netexp.utilities'] > 0) |
        (dataset['HeatandEat'] == "Yes")
    ) & (dataset['HCSUA'] == "Mandatory")

    dataset.loc[conditions_mandatory, 'UtilityReduction'] = 12 * dataset.loc[conditions_mandatory, 'HCSUAVal']

    conditions_optional = (
        (dataset['netexp.utilities'] > 0) |
        (dataset['HeatandEat'] == "Yes")
    ) & (dataset['HCSUA'] == "Optional")

    dataset.loc[conditions_optional, 'UtilityReduction'] = np.maximum(
        12 * dataset['HCSUAVal'],
        dataset['netexp.utilities']
    )

    dataset['UtilityReduction'] = dataset['UtilityReduction'].fillna(0)

    # Step V: Medical Expense Reductions
    for i in range(1, 13):
        assist_col = f'value.assist{i}'
        assist_amt_col = f'assistAmount{i}'
        age_col = f'ageMember{i}'
        medical_col = f'MedicalReduction.person{i}'
        
        dataset[medical_col] = np.where(
            (dataset[assist_col] > 0) | 
            (dataset[assist_amt_col] > 0) | 
            (dataset[age_col] > 60),
            dataset['medExpenses'],
            0
        )

    medical_cols = [f'MedicalReduction.person{i}' for i in range(1, 13)]
    dataset['MedicalReduction'] = dataset[medical_cols].sum(axis=1) - dataset['MedReductionFloor'] * 12
    dataset['MedicalReduction'] = dataset['MedicalReduction'].clip(lower=0)

    # Step IV: Net Income
    dataset['netIncome'] = (dataset['adjIncome'] - 
                            np.minimum(
                                dataset['netexp.housing'] + dataset['UtilityReduction'] + dataset['MedicalReduction'] - 0.5 * dataset['adjIncome'], 
                                dataset['MaxShelterReduction'] * 12
                            )).clip(lower=0)

    # Step V-VI: Verify eligibility and compute food aid value

    # Modify NY rules for FPL threshold with dependent care
    ny_condition = (dataset['stateFIPS'] == 36)
    dependent_condition = (dataset['netexp.childcare'] > 0)
    dataset.loc[ny_condition & dependent_condition, 'GrossIncomeLimit'] = dataset['FPL'] * 2

    dataset.loc[~dependent_condition & ny_condition, 'GrossIncomeLimit'] = dataset['FPL'] * 1.5

    # Apply special BBCE rules in NH for dependents
    nh_condition = (dataset['stateFIPS'] == 33)
    dependents_present = (dataset['kidNumber'] > 0)
    
    dataset.loc[nh_condition & dependents_present, 'GrossIncomeLimit'] = dataset['FPL'] * 1.85
    dataset.loc[nh_condition & dependents_present, ['AssetLimit_nonElderDisable', 
                                                    'AssetLimit_ElderlyDisabled_above200FPL', 
                                                    'AssetLimit_ElderlyDisabled_below200FPL']] = 999999

    dataset.loc[nh_condition & ~dependents_present, 'GrossIncomeLimit'] = dataset['FPL'] * 1.3
    dataset.loc[nh_condition & ~dependents_present, ['AssetLimit_nonElderlyDisable',
                                                     'AssetLimit_ElderlyDisabled_above200FPL',
                                                     'AssetLimit_ElderlyDisabled_below200FPL']] = dataset[['AssetFedLimit_nonElderlyDisable',
                                                                                                          'AssetFedLimit_ElderlyDisable',
                                                                                                          'AssetFedLimit_ElderlyDisable']].values

    # Checks for categorical eligibility
    assist_support_cols = [
        'value.assist1', 'value.assist2', 'value.assist3', 'value.assist4',
        'value.assist5', 'value.assist6', 'value.supportChild1', 
        'value.supportChild2', 'value.supportChild3', 'value.supportChild4', 
        'value.supportChild5', 'value.supportChild6'
    ]
    dataset['assistCount'] = (dataset[assist_support_cols] > 0).sum(axis=1)
    dataset['nonCategoric_seeker_ssi'] = dataset['assistCount'] < dataset['famsize']
    dataset['nonCategoric_seeker_stipend'] = dataset['value.stipend'] == 0

    # Income and asset eligibility
    dataset['failGrossIncomeTest'] = (
        (dataset['incomeGross'] > dataset['GrossIncomeLimit']) &
        (dataset['nonCategoric_seeker_stipend']) &
        (dataset['nonCategoric_seeker_ssi'])
    )

    dataset['failNetIncomeTest_nonElderDisable'] = (
        (dataset['disabledNumber'] == 0) &
        (dataset['elderlyNumber'] == 0) &
        (dataset['netIncome'] > dataset['NetIncomeLimit_nonElderDisable'])
    )

    dataset['failNetIncomeTest_ElderlyDisabled'] = (
        ((dataset['disabledNumber'] > 0) | (dataset['elderlyNumber'] > 0)) &
        (dataset['netIncome'] > dataset['NetIncomeLimit_ElderlyDisabled'])
    )

    # Asset tests
    dataset['failAssetTest_nonElder'] = (
        (dataset['disabledNumber'] == 0) &
        (dataset['elderlyNumber'] == 0) &
        (dataset['totalAssets'] > dataset['AssetLimit_nonElder']) & 
        (dataset['nonCategoric_seeker_stipend']) &
        (dataset['nonCategoric_seeker_ssi'])
    )

    dataset['failAssetTest_ElderAbove200FPL'] = (
        ((dataset['disabledNumber'] > 0) | (dataset['elderlyNumber'] > 0)) &
        (dataset['incomeGross'] <= 2 * dataset['FPL']) &
        (dataset['totalAssets'] > dataset['AssetLimit_ElderlyDisabled_below200FPL']) &
        (dataset['nonCategoric_seeker_stipend']) &
        (dataset['nonCategoric_seeker_ssi'])
    )

    dataset['failAssetTest_ElderBelow200FPL'] = (
        ((dataset['disabledNumber'] > 0) | (dataset['elderlyNumber'] > 0)) &
        (dataset['incomeGross'] > 2 * dataset['FPL']) &
        (dataset['totalAssets'] >
         
    dataset['AssetLimit_ElderlyDisabled_above200FPL']) &
        (dataset['nonCategoric_seeker_stipend']) &
        (dataset['nonCategoric_seeker_ssi'])
    )

    # Calculate benefit amount if eligible
    benefit_subset = dataset.loc[~(
        dataset['failGrossIncomeTest'] |
        dataset['failNetIncomeTest_ElderlyDisabled'] |
        dataset['failNetIncomeTest_nonElderDisable'] |
        dataset['failAssetTest_nonElder'] |
        dataset['failAssetTest_ElderBelow200FPL'] |
        dataset['failAssetTest_ElderAbove200FPL']
    )].index

    dataset['foodAid'] = 0
    max_aid = dataset.loc[benefit_subset, 'MaxAid'].values
    min_aid = dataset.loc[benefit_subset, 'MinAid'].values
    net_income = dataset.loc[benefit_subset, 'netIncome'].values

    benefit_value = np.minimum(
        np.maximum(12 * max_aid - 0.3 * net_income, 12 * min_aid),
        12 * max_aid
    )
    
    dataset.loc[benefit_subset, 'foodAid'] = np.round(benefit_value, decimals=0)
    
    return dataset['foodAid']


