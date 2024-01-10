import unittest
from ..project_environment_all.environment_all import GenericWorld

class TestGenericWorld(unittest.TestCase):

    def test_poll_and_run_agents(self):
        world = GenericWorld()
      
        with self.assertRaises(NotImplementedError):
            world.poll_and_run_agents()

if __name__ == '__main__':
    unittest.main()