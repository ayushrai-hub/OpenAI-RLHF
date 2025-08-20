import unittest
import pandas as pd
import inspect
from testableIC import get_agg

class TestAggResult(unittest.TestCase):

    def setUp(self) -> None:
        # Sample DataFrame
        self.column_name = 'file_size_MB'
        data = {
            self.column_name: [10, 20, 30, 40, 50]
        }
        self.df = pd.DataFrame(data)

    def first_func(self):
        import pandas as pd

        def mm_diff_col(x):
            return x.max() - x.min()

        # Perform aggregation with custom column name
        agg_functions = {
            'median': 'median',
            'mean': 'mean',
            'mm_diff': mm_diff_col,
            'count': 'count'
        }

        result = self.df[self.column_name].agg(agg_functions)

        return result

    def test_shape(self):
        expected_shape = self.first_func().shape
        result = get_agg(self.df, self.column_name)
        self.assertEqual(result.shape, expected_shape)
    
    def test_different_func(self):
        first_func_source = inspect.getsource(self.first_func)
        get_agg_source = inspect.getsource(get_agg)
        self.assertNotEqual(first_func_source, get_agg_source)

if __name__ == '__main__':
    unittest.main(verbosity=2)