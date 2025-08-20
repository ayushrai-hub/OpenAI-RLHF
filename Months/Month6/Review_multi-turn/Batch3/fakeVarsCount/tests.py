import os
import sys
import unittest
import cppyy

class TestCppyy(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.currentDirectory = os.path.abspath(os.path.dirname(__file__))
        os.chdir(cls.currentDirectory)
        cppyy.include('ideal_completion.cpp')

    # Helper method to delete generated files
    def delete_files(self):
        inputTxtFilePath = os.path.join(self.currentDirectory, 'input.txt')
        outputTxtFilePath = os.path.join(self.currentDirectory, 'captured_output.txt')
        try:
            if os.path.exists(inputTxtFilePath):
                os.remove(inputTxtFilePath)
            if os.path.exists(outputTxtFilePath):
                os.remove(outputTxtFilePath)
        except Exception as e:
            print(f"Error deleting files")

    def tearDown(self):
        self.delete_files()

    # Helper method to execute the `main()` method with the provided stdin input.
    # Returns the stdout output of the program when run with the given input
    def exec_main_with_stdin(self, input):
        with open("input.txt", "w") as f:
            f.write(input)

        # Reopen the file in read mode for input redirection
        with open("input.txt", "r") as f:
            # Save the original stdin file descriptor
            original_stdin_fd = sys.stdin.fileno()

            saved_stdin = os.dup(original_stdin_fd)
            os.dup2(f.fileno(), original_stdin_fd)
            main_function = cppyy.gbl.main

            try:
                with open("captured_output.txt", "w") as temp_output:
                    original_stdout_fd = sys.stdout.fileno()
                    saved_stdout = os.dup(original_stdout_fd)
                    os.dup2(temp_output.fileno(), original_stdout_fd)
                    main_function()
            finally:
                # Restore the original stdin and stdout
                os.dup2(saved_stdin, original_stdin_fd)
                os.close(saved_stdin)
                os.dup2(saved_stdout, original_stdout_fd)
                os.close(saved_stdout)

        with open("captured_output.txt", "r") as temp_output:
            captured_output = temp_output.read() # Load the captured stdout output

        return str(captured_output).lower()


    # Purpose: Perform the Simplex maximization calculation on an expression with two variables using <= constraints
    # Importance: This test ensures that the code delivers the correct best outcome for an objective expression with two variables when performing maximization
    def test_maximization_two_variables_lesser_than_comparison(self):
        test_input = "2\n2\n1\n3\n5\n2\n3\n2\n1\n0\n0\n<=\n<=\n8\n4\n" # Input to stdin
        output = self.exec_main_with_stdin(test_input)
        self.assertIn("best outcome for objective function: 13.33", output)


    # Purpose: Perform the Simplex minimization calculation on an expression with two variables using >= constraints
    # Importance: This test ensures that the code delivers the correct best outcome for an objective expression with two variables when performing minimization
    def test_minimization_two_variables_greater_than_comparison(self):
        test_input = "2\n1\n0\n1\n1\n1\n1\n0\n0\n>=\n10\n" # Input to stdin
        output = self.exec_main_with_stdin(test_input)
        self.assertIn("best outcome for objective function: 10.00", output)


    # Purpose: Perform the Simplex minimization calculation on an expression that results in an unbounded solution
    # Importance: This test ensures that the code correctly recognizes when a given problem statement results in an unbounded solution
    def test_unbounded_problem(self):
        test_input = "2\n1\n1\n1\n1\n1\n-1\n0\n0\n>=\n2\n"
        output = self.exec_main_with_stdin(test_input)
        self.assertIn("solution is unbounded", output)

    
    # Purpose: Perform the Simplex minimization calculation on an expression such that no feasible solution exists
    # Importance: This test ensures that the code correctly recognizes when a given problem statement is infeasible
    def test_unfeasible_problem(self):
        test_input = "2\n2\n1\n1\n1\n1\n1\n1\n1\n0\n0\n<=\n>=\n1\n3\n"
        output = self.exec_main_with_stdin(test_input)
        self.assertIn("unfeasible", output)

    # Purpose: Run the code with invalid inputs and ensure no errors are thrown
    # Importance: The code should be able to handle invalid inputs gracefully without throwing errors
    def test_invalid_input(self):
        test_input = "2\n2\n6\n1\n1\n1\n1\n1\n1\n1\n0\n0\n<=\n>=\n1\n3\n"
        output = self.exec_main_with_stdin(test_input)
        self.assertIn("invalid input", output)
        

if __name__ == "__main__":
    unittest.main(verbosity=2)