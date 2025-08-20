import unittest
import os
from ideal_completion import pymatgen_code, ase_code 

class TestStructureFunctions(unittest.TestCase):

    def setUp(self):
        """Set up file paths and expected data for tests."""
        self.pymatgen_cif_file = 'pymatgen_delta_Bi2O3.cif'
        self.ase_cif_file = 'ase_delta_Bi2O3.cif'
        
        # Expected unique atomic positions (fractional) within one unit cell
        self.expected_data = [
            ('Bi', (0.25, 0.25, 0.25)),
            ('Bi', (0.4703, 0.0, 0.25)),
            ('O', (0.3936, 0.1545, 0.3804))
        ]

    def tearDown(self):
        """Remove generated CIF files after tests."""
        if os.path.exists(self.pymatgen_cif_file):
            os.remove(self.pymatgen_cif_file)
        if os.path.exists(self.ase_cif_file):
            os.remove(self.ase_cif_file)

    def test_pymatgen_code_creates_cif(self):
        """Test if pymatgen_code creates a CIF file."""
        pymatgen_code()
        self.assertTrue(os.path.exists(self.pymatgen_cif_file), "Pymatgen CIF file not created.")

    def test_pymatgen_code_runs_without_error(self):
        """Test if pymatgen_code runs without raising an error."""
        try:
            pymatgen_code()
        except Exception as e:
            self.fail(f"pymatgen_code raised an exception: {e}")

    def test_pymatgen_code_coordinates(self):
        """Test if pymatgen_code produces expected atomic coordinates."""
        structure = pymatgen_code()

        # Gather unique fractional coordinates from pymatgen output
        pymatgen_unique_coords = {(site.specie.symbol, tuple(round(c, 4) for c in site.frac_coords)) for site in structure.sites}

        # Match pymatgen coordinates within tolerance
        for element, coord in self.expected_data:
            matched = any(
                site[0] == element and all(abs(a - b) < 0.01 for a, b in zip(coord, site[1]))
                for site in pymatgen_unique_coords
            )
            self.assertTrue(matched, f"Expected coordinate {coord} for element {element} not found in pymatgen output.")

    def test_ase_code_creates_cif(self):
        """Test if ase_code creates a CIF file."""
        ase_code()
        self.assertTrue(os.path.exists(self.ase_cif_file), "ASE CIF file not created.")

    def test_ase_code_runs_without_error(self):
        """Test if ase_code runs without raising an error."""
        try:
            ase_code()
        except Exception as e:
            self.fail(f"ase_code raised an exception: {e}")

    def test_ase_code_coordinates(self):
        """Test if ase_code produces expected atomic coordinates."""
        crystal_struct = ase_code()

        # Gather unique fractional coordinates from ASE output
        ase_unique_coords = set()
        for atom in crystal_struct:
            fractional_coords = (
                round(atom.position[0] / crystal_struct.cell[0, 0], 4),
                round(atom.position[1] / crystal_struct.cell[1, 1], 4),
                round(atom.position[2] / crystal_struct.cell[2, 2], 4)
            )
            ase_unique_coords.add((atom.symbol, fractional_coords))

        # Match ASE coordinates within tolerance
        for element, coord in self.expected_data:
            matched = any(
                site[0] == element and all(abs(a - b) < 0.01 for a, b in zip(coord, site[1]))
                for site in ase_unique_coords
            )
            self.assertTrue(matched, f"Expected coordinate {coord} for element {element} not found in ASE output.")

if __name__ == "__main__":
    unittest.main(verbosity=2)