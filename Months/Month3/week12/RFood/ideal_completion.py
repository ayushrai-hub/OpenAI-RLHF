import pandas as pd
import numpy as np
import itertools

def calculate_food_benefit(dataset, foodData):
    if dataset.empty:
        return pd.Series(dtype=float)

    # Update benefit rules for missing years
    all_years = dataset['ruleYear'].unique()
    data_years_available = foodData['ruleYear'].unique()
    years_needed = all_years[~np.isin(all_years, data_years_available)]
    
    max_year_with_data = foodData['ruleYear'].max()
    future_years = years_needed[years_needed > max_year_with_data]
    
    if len(future_years) > 0:
        future_frame = pd.DataFrame(list(itertools.product(
            foodData['stateFIPS'].unique(),
            foodData['famsize'].unique(),
            future_years
        )), columns=['stateFIPS', 'famsize', 'ruleYear'])
        
        merge_data = foodData[foodData['ruleYear'] == max_year_with_data].copy()
        future_frame = future_frame.merge(merge_data.drop('ruleYear', axis=1), 
                                          on=['stateFIPS', 'famsize'])
        foodData = pd.concat([foodData, future_frame], ignore_index=True)

    # Merge dataset with foodData
    dataset = dataset.merge(foodData, on=['ruleYear', 'stateFIPS', 'famsize'], how='left')

    # Calculate total countable income
    income_cols = ['income', 'income.gifts', 'income.childSupport', 'income.investment',
                   'value.stipend', 'value.support', 'value.assistance']
    dataset['incomeGross'] = dataset[income_cols].fillna(0).sum(axis=1)

    # Check for elderly or disabled household members
    age_cols = [col for col in dataset.columns if col.startswith('ageMember')]
    dataset['elderlyNumber'] = (dataset[age_cols] > 60).sum(axis=1)
    dataset['kidNumber'] = (dataset[age_cols] < 19).sum(axis=1)

    # Assume no disabled members if disability columns are not present
    dataset['disabledNumber'] = 0

    # Earned income reduction
    dataset['EarnedIncomeReduction'] = 0.2 * dataset['income'].fillna(0)

    # Adjusted income
    dataset['adjIncome'] = np.maximum(0, dataset['incomeGross'] - dataset['EarnedIncomeReduction'] -
                                      12 * dataset['StandardReduction'] - dataset['netexp.childcare'].fillna(0))

    # Utility deductions
    dataset['UtilityReduction'] = 0
    mandatory_mask = ((dataset['netexp.utilities'] > 0) | (dataset['HeatandEat'] == 'Yes')) & (dataset['HCSUA'] == 'Mandatory')
    optional_mask = ((dataset['netexp.utilities'] > 0) | (dataset['HeatandEat'] == 'Yes')) & (dataset['HCSUA'] == 'Optional')
    
    dataset.loc[mandatory_mask, 'UtilityReduction'] = 12 * dataset.loc[mandatory_mask, 'HCSUAVal']
    dataset.loc[optional_mask, 'UtilityReduction'] = np.maximum(12 * dataset.loc[optional_mask, 'HCSUAVal'],
                                                                dataset.loc[optional_mask, 'netexp.utilities'])

    # Medical expense reductions
    dataset['MedicalReduction'] = np.where((dataset['elderlyNumber'] > 0) | (dataset['disabledNumber'] > 0),
                                           np.maximum(0, dataset['medExpenses'].fillna(0) - dataset['MedReductionFloor'] * 12),
                                           0)

    # Net income
    dataset['netIncome'] = np.maximum(0, dataset['adjIncome'] - 
                                      np.minimum(dataset['netexp.housing'].fillna(0) + dataset['UtilityReduction'] + 
                                                 dataset['MedicalReduction'] - 0.5 * dataset['adjIncome'],
                                                 dataset['MaxShelterReduction'] * 12))

    # Eligibility checks and benefit computation
    dataset['GrossIncomeLimit'] = np.where(dataset['stateFIPS'] == 36,
                                           np.where(dataset['netexp.childcare'] > 0, dataset['FPL'] * 2, dataset['FPL'] * 1.5),
                                           dataset['GrossIncomeLimit'])

    nh_mask = dataset['stateFIPS'] == 33
    dataset.loc[nh_mask & (dataset['kidNumber'] > 0), 'GrossIncomeLimit'] = dataset['FPL'] * 1.85
    dataset.loc[nh_mask & (dataset['kidNumber'] == 0), 'GrossIncomeLimit'] = dataset['FPL'] * 1.3

    assist_cols = [col for col in dataset.columns if col.startswith('value.assist') or col.startswith('value.supportChild')]
    dataset['assistCount'] = (dataset[assist_cols] > 0).sum(axis=1)
    dataset['isCategoricallyEligible'] = (dataset['assistCount'] > 0) | (dataset['value.stipend'] > 0)

    # Eligibility tests
    dataset['failGrossIncomeTest'] = (dataset['incomeGross'] > dataset['GrossIncomeLimit']) & ~dataset['isCategoricallyEligible']
    dataset['failNetIncomeTest'] = (dataset['netIncome'] > dataset['NetIncomeLimit_nonElderDisable']) & ~dataset['isCategoricallyEligible']
    dataset['failAssetTest'] = (dataset['totalAssets'] > dataset['AssetLimit_nonElder']) & ~dataset['isCategoricallyEligible']

    # Calculate food aid
    eligible_mask = ~(dataset['failGrossIncomeTest'] | dataset['failNetIncomeTest'] | dataset['failAssetTest']) | dataset['isCategoricallyEligible']
    
    dataset['foodAid'] = 0
    dataset.loc[eligible_mask, 'foodAid'] = np.maximum(
        np.minimum(
            np.maximum(12 * dataset.loc[eligible_mask, 'MaxAid'] - 0.3 * dataset.loc[eligible_mask, 'netIncome'], 0),
            12 * dataset.loc[eligible_mask, 'MaxAid']
        ),
        12 * dataset.loc[eligible_mask, 'MinAid']
    ).round()

    # Ensure minimum benefit for eligible households with zero net income
    zero_net_income_mask = eligible_mask & (dataset['netIncome'] == 0)
    dataset.loc[zero_net_income_mask, 'foodAid'] = np.maximum(dataset.loc[zero_net_income_mask, 'foodAid'], 12 * dataset.loc[zero_net_income_mask, 'MinAid'])

    return dataset['foodAid']