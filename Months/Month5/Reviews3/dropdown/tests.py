import unittest
import plotly.graph_objects as go
from testableIC  import generate_customer_period_revenue_figure

class TestCustomerPeriodRevenueFigure(unittest.TestCase):

    def test_function_runs_without_error(self):
        """Test if the function runs without throwing errors."""
        try:
            fig = generate_customer_period_revenue_figure()
        except Exception as e:
            self.fail(f"Function raised an exception: {e}")

    def test_figure_type(self):
        """Test if the function returns a plotly.graph_objs.Figure object."""
        try:
            fig = generate_customer_period_revenue_figure()
            self.assertIsInstance(fig, go.Figure, "The object returned is not a Plotly Figure")
        except Exception as e:
            self.fail(f"Function raised an exception: {e}")
            
    def test_initial_visibility_settings(self):
        """Test if the initial visibility is set properly."""
        try:
            fig = generate_customer_period_revenue_figure()
            customer_a_visible = [trace.visible for trace in fig.data if trace.name.startswith('Customer A')]
            other_customers_visible = [trace.visible for trace in fig.data if not trace.name.startswith('Customer A')]

            # Assert that all traces for Customer A are visible
            self.assertTrue(all(customer_a_visible), "Not all Customer A traces are visible initially")

            # Assert that no traces for other customers are visible
            self.assertFalse(any(other_customers_visible), "Some non-Customer A traces are visible initially")
        except Exception as e:
            self.fail(f"Function raised an exception: {e}")

if __name__ == '__main__':
    unittest.main(verbosity=2)
