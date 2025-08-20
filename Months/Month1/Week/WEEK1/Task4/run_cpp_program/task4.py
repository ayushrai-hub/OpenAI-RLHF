
import subprocess
import unittest

def run_cpp_program():
    result = subprocess.run(['./hello'], capture_output=True, text=True)
    print(result)
    return result.stdout.strip()

class TestCppOutput(unittest.TestCase):
    def test_hello_world_output(self):
        expected_output = "Hello, World!"
        actual_output = run_cpp_program()
        self.assertEqual(actual_output, expected_output)

if __name__ == '__main__':
    unittest.main(verbosity=2)