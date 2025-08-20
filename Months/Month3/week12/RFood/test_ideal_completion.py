import unittest
import pandas as pd
import numpy as np
from ideal_completion import calculate_food_benefit  

class TestCalculateFoodBenefit(unittest.TestCase):

    def setUp(self):
        # Create sample datasets for each test
        self.sample_dataset = pd.DataFrame({
            'ruleYear': [2022, 2022, 2023, 2023],
            'stateFIPS': [36, 33, 36, 33],
            'famsize': [2, 3, 4, 5],
            'income': [20000, 30000, 40000, 50000],
            'income.gifts': [1000, 1500, 2000, 2500],
            'income.childSupport': [0, 2000, 3000, 4000],
            'income.investment': [500, 1000, 1500, 2000],
            'value.stipend': [0, 1000, 0, 2000],
            'value.support': [0, 0, 1000, 1500],
            'value.assistance': [1000, 1500, 2000, 2500],
            'netexp.utilities': [1200, 1500, 1800, 2100],
            'netexp.childcare': [0, 3000, 5000, 7000],
            'netexp.housing': [12000, 15000, 18000, 21000],
            'totalAssets': [3000, 5000, 7000, 9000],
            'medExpenses': [1000, 1500, 2000, 2500],
            'HeatandEat': ['No', 'Yes', 'No', 'Yes'],
            'HCSUA': ['Mandatory', 'Optional', 'Mandatory', 'Optional'],
            'ageMember1': [30, 40, 50, 60],
            'ageMember2': [25, 35, 45, 55],
            'value.assist1': [0, 0, 0, 0],
            'value.supportChild1': [0, 0, 0, 0],
        })

        self.sample_foodData = pd.DataFrame({
            'ruleYear': [2022, 2022, 2023, 2023],
            'stateFIPS': [36, 33, 36, 33],
            'famsize': [2, 3, 4, 5],
            'StandardReduction': [200, 250, 300, 350],
            'HCSUAVal': [500, 600, 700, 800],
            'MedReductionFloor': [50, 60, 70, 80],
            'MaxShelterReduction': [600, 700, 800, 900],
            'FPL': [17000, 22000, 27000, 32000],
            'GrossIncomeLimit': [25500, 33000, 40500, 48000],
            'NetIncomeLimit_nonElderDisable': [17000, 22000, 27000, 32000],
            'NetIncomeLimit_ElderlyDisabled': [20000, 25000, 30000, 35000],
            'AssetLimit_nonElder': [3000, 3000, 3500, 3500],
            'AssetLimit_ElderlyDisabled_below200FPL': [4000, 4000, 4500, 4500],
            'AssetLimit_ElderlyDisabled_above200FPL': [5000, 5000, 5500, 5500],
            'MaxAid': [300, 400, 500, 600],
            'MinAid': [20, 25, 30, 35],
        })

    def test_basic_functionality(self):
        # Test the basic functionality of the calculate_food_benefit function
        result = calculate_food_benefit(self.sample_dataset, self.sample_foodData)
        self.assertIsInstance(result, pd.Series)
        self.assertEqual(len(result), len(self.sample_dataset))
        self.assertTrue(all(result >= 0))

    def test_zero_income(self):
        # Test the scenario where all income sources are zero
        zero_income_dataset = self.sample_dataset.copy()
        income_columns = ['income', 'income.gifts', 'income.childSupport', 'income.investment',
                          'value.stipend', 'value.support', 'value.assistance']
        zero_income_dataset[income_columns] = 0
        result = calculate_food_benefit(zero_income_dataset, self.sample_foodData)
        self.assertTrue(all(result >= 0))

    def test_missing_data(self):
        # Test how the function handles missing data
        missing_data_dataset = self.sample_dataset.copy()
        missing_data_dataset.loc[0, 'income'] = np.nan
        result = calculate_food_benefit(missing_data_dataset, self.sample_foodData)
        self.assertFalse(np.isnan(result[0]))

    def test_ny_childcare(self):
        # Test the special rule for New York households with childcare expenses
        ny_dataset = self.sample_dataset[self.sample_dataset['stateFIPS'] == 36].copy()
        ny_dataset.loc[ny_dataset.index[0], 'netexp.childcare'] = 5000
        result = calculate_food_benefit(ny_dataset, self.sample_foodData)
        self.assertTrue(result[0] > 0)

    def test_nh_with_kids(self):
        # Test the special rule for New Hampshire households with children
        nh_dataset = self.sample_dataset[self.sample_dataset['stateFIPS'] == 33].copy()
        nh_dataset['kidNumber'] = 2
        result = calculate_food_benefit(nh_dataset, self.sample_foodData)
        self.assertTrue(result[0] > 0)

    def test_elderly(self):
        # Test how the function handles elderly households
        elderly_dataset = self.sample_dataset.copy()
        elderly_dataset['ageMember1'] = 65
        result = calculate_food_benefit(elderly_dataset, self.sample_foodData)
        self.assertTrue(all(result > 0))

    def test_categorical_eligibility(self):
        # Test categorical eligibility rules
        categorical_dataset = self.sample_dataset.copy()
        categorical_dataset['value.assist1'] = 1
        result = calculate_food_benefit(categorical_dataset, self.sample_foodData)
        self.assertTrue(all(result > 0))

    def test_missing_key_columns(self):
        # Test how the function handles missing required columns
        for column in ['ruleYear', 'stateFIPS', 'famsize']:
            with self.subTest(column=column):
                invalid_dataset = self.sample_dataset.drop(columns=[column])
                with self.assertRaises(KeyError):
                    calculate_food_benefit(invalid_dataset, self.sample_foodData)

    def test_empty_dataset(self):
        # Test how the function handles an empty dataset
        empty_dataset = pd.DataFrame(columns=self.sample_dataset.columns)
        result = calculate_food_benefit(empty_dataset, self.sample_foodData)
        self.assertEqual(len(result), 0)

    def test_large_dataset(self):
        # Test the function's performance with a large dataset
        large_dataset = pd.concat([self.sample_dataset] * 1000, ignore_index=True)
        result = calculate_food_benefit(large_dataset, self.sample_foodData)
        self.assertEqual(len(result), len(large_dataset))

if __name__ == '__main__':
    unittest.main(verbosity=2)