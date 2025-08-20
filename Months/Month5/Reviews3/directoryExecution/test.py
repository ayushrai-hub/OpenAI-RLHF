import unittest
import textwrap
from pathlib import Path
from testableIC import execute_python_code

class TestPythonFileExecution(unittest.TestCase):
    
    def setUp(self):
        self.python_code = textwrap.dedent("""
            with open('/tmp/test.txt', 'w') as f:
                f.write('Hello, World!')
            """
            )
        
    def tearDown(self):
        Path('/tmp/test.txt').unlink()
        if Path('/tmp/test.py').exists():
            Path('/tmp/test.py').unlink()
    
    def test_no_file(self):
        output_file="/tmp/test.py"
        execute_python_code(self.python_code, output_file)
        self.assertFalse(Path(output_file).exists())
        
    
    def test_result_of_file(self):
        execute_python_code(self.python_code)
        with open('/tmp/test.txt', 'r') as f:
            self.assertEqual(f.read(), 'Hello, World!')
        
if __name__ == '__main__':
    unittest.main(verbosity=2)