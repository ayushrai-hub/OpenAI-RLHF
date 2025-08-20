import unittest
from streamlit.testing.v1 import AppTest
from ideal_completion import run_streamlit_graph

class TestTradeSignals(unittest.TestCase):

    def setUp(self) -> None:
        self.at = AppTest.from_function(run_streamlit_graph)
        self.at.run()

    def test_no_exception(self):
        assert not self.at.exception
    
    def test_title(self):
        self.assertEqual(self.at.title[0].value, "React-Flow Testing")

if __name__ == '__main__':
    unittest.main()