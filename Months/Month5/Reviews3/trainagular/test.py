import unittest
from PIL import Image, ImageDraw
from teatableIc import create_spectrum


class TestWaterGlassApp(unittest.TestCase):

    def setUp(self):
        # Create a blank image with support for transparency (RGBA)
        self.width = 300
        self.height = 300
        self.image = Image.new("RGBA", (self.width, self.height), (255, 255, 255, 0))
        self.draw = ImageDraw.Draw(self.image)

    def test_marker_at_left_side(self):
        # Test if the marker is at the left side of the color scale
        color_start = (225, 234, 242)
        color_end = (96, 72, 33)
        ntu_value = 1500

        create_spectrum(self.draw, 200, 20, 50, 260, color_start, color_end, ntu_value)

        marker_x_position = 200  
        for y in range(20, 260):
            self.assertEqual(self.image.getpixel((marker_x_position, y))[3], 255, "Marker is not on the left side of the scale")
    
    def test_3000_label_visible(self):
        # Test if the 3000 label is visible on the color scale
        color_start = (225, 234, 242)
        color_end = (96, 72, 33)
        ntu_value = 3000

        create_spectrum(self.draw, 200, 20, 50, 260, color_start, color_end, ntu_value)

        
        for x in range(250, 260):
            for y in range(20, 30):  
                if self.image.getpixel((x, y))[3] > 0:
                    self.assertTrue(True)
                    return
        self.fail("3000 label is not visible on the color scale")
    
    def test_marker_orientation(self):
        # Test if the triangular marker is pointing left based on its coordinates.
        
        color_start = (225, 234, 242)
        color_end = (96, 72, 33)
        ntu_value = 1500

        # Draw the spectrum and get the triangle's coordinates
        triangle_coords = create_spectrum(self.draw, 200, 20, 50, 260, color_start, color_end, ntu_value)

        # Determine if the triangle points left or right based on its coordinates
        unique_coords = list(set(triangle_coords))

        # Sort by the y-coordinate to identify the top point
        unique_coords.sort(key=lambda p: p[1])
        
        base_points = unique_coords[:-1]  # Remaining points are the base points

        # Check if the base points are positioned to determine left or right
        if base_points[0][0] > base_points[1][0]:
            direction = "LEFT"
        else:
            direction = "RIGHT"

        # Assert that the triangle is pointing left
        self.assertEqual(direction, "LEFT", "The marker is not pointing left.")

if __name__ == "__main__":
    unittest.main(verbosity=2)