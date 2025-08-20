import unittest
import os

import cppyy
import numpy as np
from netCDF4 import Dataset


class TestNetCDF(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            # Load the C++ code from the file
            cpp_file_name = "ideal_completion.cpp"
            cpp_file_path = os.path.abspath(
                os.path.join(os.path.dirname(__file__), cpp_file_name)
            )

            if not os.path.exists(cpp_file_path):
                raise FileNotFoundError(f"{cpp_file_path} not found")

            cppyy.load_library("netcdf_c++4")

            with open(cpp_file_path, "r", encoding="utf8") as cpp_file:
                cpp_code = cpp_file.read()

            # Compile the C++ code using cppyy
            cppyy.cppdef(cpp_code)

            # Define a C++ namespace and types
            cls.std = cppyy.gbl.std

            cls.creat_dataset()

        except FileNotFoundError as err:
            cls.fail(cls, f"Setup failed: {str(err)}")
        except Exception as err:
            cls.fail(cls, f"Error during C++ compilation: {str(err)}")

    @classmethod
    def creat_dataset(cls):
        """Generate dataset"""
        times = np.linspace(0, 25, 25)
        depths = np.linspace(0, 100, 50)
        lats = np.linspace(-50, 0, 50)
        lons = np.linspace(0, 90, 90)

        ones = np.ones((25, 50, 50, 90))  # All values set to 1.0

        # Create sample NetCDF files
        cls.create_sample_nc_file("dataset1.nc", times, depths, lats, lons)
        cls.create_sample_nc_file("dataset2.nc", times, depths, lats, lons, ones)

    @classmethod
    def create_sample_nc_file(
        cls, filename, times, depths, lats, lons, data_values=None
    ):
        """Creates a sample NetCDF file with given dimensions."""
        with Dataset(filename, "w", format="NETCDF4") as ncfile:
            # Define dimensions
            ncfile.createDimension("time", len(times))
            ncfile.createDimension("depth", len(depths))
            ncfile.createDimension("lat", len(lats))
            ncfile.createDimension("lon", len(lons))

            # Create coordinate variables
            time_var = ncfile.createVariable("time", "f8", ("time",))
            depth_var = ncfile.createVariable("depth", "f8", ("depth",))
            lat_var = ncfile.createVariable("lat", "f8", ("lat",))
            lon_var = ncfile.createVariable("lon", "f8", ("lon",))

            # Assign data to coordinate variables
            time_var[:] = times
            depth_var[:] = depths
            lat_var[:] = lats
            lon_var[:] = lons

            # # Create data variable
            data_var = ncfile.createVariable(
                "data", "f8", ("time", "depth", "lat", "lon")
            )
            if data_values is None:
                # Generate synthetic data (sinusoidal pattern)
                data = (
                    np.sin(np.linspace(0, np.pi, len(times)).reshape(-1, 1, 1, 1))
                    + np.cos(np.linspace(0, np.pi, len(depths)).reshape(1, -1, 1, 1))
                    + np.sin(np.linspace(0, np.pi, len(lats)).reshape(1, 1, -1, 1))
                    + np.cos(np.linspace(0, np.pi, len(lons)).reshape(1, 1, 1, -1))
                )

                data_var[:] = data
            else:
                data_var[:] = data_values

    @classmethod
    def tearDownClass(cls):
        files = ["dataset1.nc", "dataset2.nc"]
        for file_path in files:
            if os.path.exists(file_path):
                os.remove(file_path)

    def test_get_value_within_bounds(self):
        # Get value within bounds

        mgr = cppyy.gbl.EnvironmentManager()
        mgr.addDataset("dataset1.nc")
        expected_output = 2
        self.assertAlmostEqual(
            mgr.getValue(12.5, 50, -25, 45), expected_output, places=1
        )

    def test_get_value_out_of_bounds(self):
        # Get value out of bounds

        mgr = cppyy.gbl.EnvironmentManager()
        mgr.addDataset("dataset1.nc")
        time = -1.0  # Invalid time
        depth = 10000  # Invalid depth
        lat = -100.0  # Invalid latitude
        lon = 200.0  # Invalid longitude
        self.assertTrue(self.std.isnan(mgr.getValue(time, depth, lat, lon)))

    def test_multiple_datasets(self):
        # Test multiple datasets

        mgr = cppyy.gbl.EnvironmentManager()
        mgr.addDataset("dataset1.nc")
        mgr.addDataset("dataset2.nc")
        expected_output = 1.5
        self.assertAlmostEqual(
            mgr.getValue(12.5, 50, -25, 45), expected_output, places=1
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)