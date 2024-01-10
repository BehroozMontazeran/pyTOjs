import unittest
from environment_all import GenericWorld

class GenericWorldTestCase(unittest.TestCase):

    def test_build_arena(self):
        world = GenericWorld() # Create an instance of the GenericWorld class
        with self.assertRaises(NotImplementedError):
            world.build_arena() # Call build_arena method and assert that NotImplementedError is raised

if __name__ == '__main__':
    unittest.main()