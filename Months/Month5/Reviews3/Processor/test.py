import unittest
import os
import re

class TestIntegratedProcessorCode(unittest.TestCase):

    def setUp(self):
        # Use os.path.abspath to get the absolute path of the script
        self.file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "testableIC.py"))

        # Read the content of the file
        with open(self.file_path, 'r') as file:
            self.script_content = file.read()

    def normalize_code(self, code):
        """Normalize the code by removing extra spaces, line breaks, and indentation."""
        # Remove extra spaces and line breaks
        code = code.strip()
        # Replace multiple spaces or tabs with a single space
        code = re.sub(r'\s+', ' ', code)
        return code

    def test_method_existence(self):
        """Test that plot_path and calculate_cf methods exist in the script."""
        # Check for the existence of 'def plot_path' in the script
        self.assertIn('def plot_path', self.script_content, "plot_path method is missing!")
        
        # Check for the existence of 'def calculate_cf' in the script
        self.assertIn('def calculate_cf', self.script_content, "calculate_cf method is missing!")

    def test_plot_path_definition(self):
        """Test that the definition of plot_path matches the expected code."""
        expected_code = """
        def plot_path(self, samp=0):
            positions = np.array(self._retrieve_state(samp=samp, step=None, coords=True))
            positions = pd.DataFrame(positions, columns=["x", "y"])
            return (
                so.Plot(self.ENV.detail_state, x="x", y="y", color="color")
                .add(so.Dot())
                .scale(
                    color=so.Nominal(),
                    x=so.Temporal()
                )
                .add(so.Line(positions, color="black"))
            )
        """
        # Normalize both expected and actual code
        expected_code = self.normalize_code(expected_code)
        actual_code = self.normalize_code(self.extract_function_code('plot_path'))

        # Compare the normalized code
        self.assertEqual(actual_code, expected_code, "The definition of plot_path does not match the expected code.")

    def test_calculate_cf_definition(self):
        """Test that the definition of calculate_cf matches the expected code."""
        expected_code = """
        def calculate_cf(self, axis=None, dist_occ=0, zero_pos=False):
            if self.scenario:
                sampled_state = self.ENV.states[self.state_series]
                sampled_state[:, :, 0] = self.ENV.semantic_mds[sampled_state[:, :, 0].astype(int)]
                sampled_state[:, :, 2] = self.ENV.spatial_mds[sampled_state[:, :, 2].astype(int)]
                sampled_state = sampled_state[:, :, 0:3]
                self.acf_mean, self.acf_sem = estimate_scenario_acf_v2(sampled_state, axis=axis)
            else:
                sampled_state = self._retrieve_state(samp=None, step=None, coords=False)
                if zero_pos:
                    self.acf_mean, self.acf_sem = estimate_occ_acf_zero(sampled_state.T, d=dist_occ)
                else:
                    self.acf_mean, self.acf_sem = estimate_occ_acf(sampled_state.T, d=dist_occ)
        """
        # Normalize both expected and actual code
        expected_code = self.normalize_code(expected_code)
        actual_code = self.normalize_code(self.extract_function_code('calculate_cf'))

        # Compare the normalized code
        self.assertEqual(actual_code, expected_code, "The definition of calculate_cf does not match the expected code.")

    def extract_function_code(self, function_name):
        """Extract the code of the specified function from the script content."""
        # Find the start of the function
        pattern = rf'def {function_name}\(.*\):'
        match = re.search(pattern, self.script_content)
        if not match:
            return ""
        
        start_pos = match.start()

        # Extract the function code by finding the block it belongs to
        indent_level = None
        function_lines = []
        for line in self.script_content[start_pos:].splitlines():
            stripped_line = line.strip()
            if not stripped_line:
                continue
            current_indent = len(line) - len(stripped_line)
            if indent_level is None:
                indent_level = current_indent  # set the indent level of the first line after 'def'

            if current_indent < indent_level and function_lines:
                break  # end of function block
            
            # Stop extracting if we encounter another function definition
            if stripped_line.startswith('def ') and len(function_lines) > 0:
                break

            function_lines.append(line)

        return '\n'.join(function_lines)

if __name__ == '__main__':
    unittest.main()
