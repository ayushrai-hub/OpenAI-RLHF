import unittest
from unittest.mock import patch
from ideal_completion import (
    calculate_haversine,
    calculate_initial_compass_bearing,
    compute_pixel_coords,
    nearby_roads,
)

class TestIdealCompletion(unittest.TestCase):

    def test_calculate_haversine(self):
        # Verify the haversine distance between two points
        # Check if the calculated distance between (0,0) and (0,1) is approximately 111.319 km
        self.assertAlmostEqual(calculate_haversine(0, 0, 0, 1), 111319, delta=500)
        # Ensure distance between the same point is zero
        self.assertEqual(calculate_haversine(0, 0, 0, 0), 0)

    def test_calculate_initial_compass_bearing(self):
        # Test the compass bearing between points
        # Verify north direction with latitude change only
        self.assertAlmostEqual(calculate_initial_compass_bearing(33.0, -118.0, 34.0, -118.0), 0, delta=1)
        # Verify east direction with longitude change only
        self.assertAlmostEqual(calculate_initial_compass_bearing(33.0, -118.0, 33.0, -117.0), 90, delta=1)
        # Ensure no bearing is required for the same point
        self.assertEqual(calculate_initial_compass_bearing(33.0, -118.0, 33.0, -118.0), 0)

    def test_compute_pixel_coords_off_center(self):
        # Verify pixel coordinates for an object slightly to the right of the drone's view
        # The test ensures the algorithm properly maps off-center objects to the right of the image center
        drone_lat = 33.0
        drone_lon = -118.0
        drone_alt = 100
        drone_pitch = 0
        drone_roll = 0
        drone_yaw = 0
        obj_lat = 33.0
        obj_lon = -117.999
        img_width = 3840
        img_height = 2160
        horiz_fov = 62
        vert_fov = 45

        pixel_x, pixel_y = compute_pixel_coords(
            drone_lat, drone_lon, drone_alt, drone_pitch, drone_roll, drone_yaw,
            obj_lat, obj_lon, img_width, img_height, horiz_fov, vert_fov
        )

        # Object to the right should appear right of the image center
        self.assertTrue(pixel_x > img_width / 2)

    @patch('ideal_completion.requests.get')
    def test_nearby_roads(self, mock_get):
        # Verify road fetching using mocked API response
        # Mock API response includes a single road for simplicity
        mock_response = {
            'elements': [
                {
                    'type': 'way',
                    'tags': {'name': 'Mocked Road'},
                    'geometry': [
                        {'lat': 33.0, 'lon': -118.0},
                        {'lat': 33.0005, 'lon': -118.0005}
                    ]
                }
            ]
        }
        mock_get.return_value.json.return_value = mock_response
        roads = nearby_roads(33.0, -118.0)
        # Check if the mocked road data is returned correctly
        self.assertEqual(len(roads), 1)
        self.assertEqual(roads[0]['name'], 'Mocked Road')
        self.assertEqual(roads[0]['coordinates'], [(33.0, -118.0), (33.0005, -118.0005)])

        # Mock response for no nearby roads
        mock_get.return_value.json.return_value = {'elements': []}
        # Ensure no roads are found in absence of data
        self.assertEqual(len(nearby_roads(33.0, -118.0)), 0)

    def test_object_behind_drone(self):
        # Verify handling of objects directly behind the drone
        # Ensure objects behind the field of view are mapped to default positions
        drone_lat = 33.0
        drone_lon = -118.0
        drone_alt = 100
        drone_pitch = 0
        drone_roll = 0
        drone_yaw = 0
        obj_lat = 32.999
        obj_lon = -118.0
        img_width = 3840
        img_height = 2160
        horiz_fov = 62
        vert_fov = 45

        pixel_x, pixel_y = compute_pixel_coords(
            drone_lat, drone_lon, drone_alt, drone_pitch, drone_roll, drone_yaw,
            obj_lat, obj_lon, img_width, img_height, horiz_fov, vert_fov
        )

        # Verify the mapping of out-of-view objects to a default position
        self.assertEqual(pixel_x, img_width // 2)
        self.assertEqual(pixel_y, img_height - 1)

    def test_object_far_to_side(self):
        # Verify pixel mapping for objects far to the side of the drone's view
        drone_lat = 33.0
        drone_lon = -118.0
        drone_alt = 100
        drone_pitch = 0
        drone_roll = 0
        drone_yaw = 0
        obj_lat = 33.0
        obj_lon = -117.99
        img_width = 3840
        img_height = 2160
        horiz_fov = 62
        vert_fov = 45

        pixel_x, pixel_y = compute_pixel_coords(
            drone_lat, drone_lon, drone_alt, drone_pitch, drone_roll, drone_yaw,
            obj_lat, obj_lon, img_width, img_height, horiz_fov, vert_fov
        )

        # Objects far to the side should map near the edge of the image
        self.assertTrue(pixel_x > img_width - 50)

    def test_object_below_drone(self):
        # Verify the behavior for objects significantly below the drone's altitude
        # Objects should appear in the lower part of the image
        drone_lat = 33.0
        drone_lon = -118.0
        drone_alt = 500
        drone_pitch = 0
        drone_roll = 0
        drone_yaw = 0
        obj_lat = 33.0005
        obj_lon = -118.0
        img_width = 3840
        img_height = 2160
        horiz_fov = 62
        vert_fov = 45

        pixel_x, pixel_y = compute_pixel_coords(
            drone_lat, drone_lon, drone_alt, drone_pitch, drone_roll, drone_yaw,
            obj_lat, obj_lon, img_width, img_height, horiz_fov, vert_fov
        )

        # Verify the object appears in the lower part of the image
        self.assertAlmostEqual(pixel_x, img_width / 2, delta=50)
        self.assertTrue(pixel_y > img_height / 2)

if __name__ == "__main__":
    unittest.main(verbosity=2)