import unittest
from environment_all import GenericWorld

class TestGenericWorld(unittest.TestCase):

    def test_end_method(self):
        # Arrange
        world = GenericWorld()

        # Act
        world.end()

        # Assert
        # Add your assertions here based on the expected behavior of the method
        # For example, you can assert that the logger's info method was called or the exit message was sent to agents

if __name__ == '__main__':
    unittest.main()