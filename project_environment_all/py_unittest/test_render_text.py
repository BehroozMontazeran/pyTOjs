import unittest
from environment_all import GUI

class GUITest(unittest.TestCase):
    def test_render_text(self):
        # Arrange
        gui = GUI()
        expected_text = "Hello, World!"
        expected_x = 100
        expected_y = 200
        expected_color = (255, 255, 255)
        expected_halign = 'left'
        expected_valign = 'top'
        expected_size = 'medium'
        expected_aa = False

        # Act
        gui.render_text(expected_text, expected_x, expected_y, expected_color, expected_halign, expected_valign, expected_size, expected_aa)

        # Assert
        # Add your assertions here to verify the expected behavior of the render_text method

if __name__ == '__main__':
    unittest.main()