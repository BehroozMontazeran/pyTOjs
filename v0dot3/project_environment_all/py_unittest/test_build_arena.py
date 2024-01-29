import unittest
from environment_all import GenericWorld

class TestGenericWorld(unittest.TestCase):
    def setUp(self):
        self.generic_world = GenericWorld()

    def test_build_arena(self):
        arena, coins, active_agents = self.generic_world.build_arena()

        # Assert that the expected variables are returned
        self.assertIsInstance(arena, np.ndarray)
        self.assertIsInstance(coins, list)
        self.assertIsInstance(active_agents, list)

        # Assert that the shape of the arena is correct
        self.assertEqual(arena.shape, (s.COLS, s.ROWS))

        # Assert that the values in the arena array are correct
        self.assertIn(WALL, arena)
        self.assertIn(FREE, arena)
        self.assertIn(CRATE, arena)

        # Assert that the number of coins is as expected
        self.assertEqual(len(coins), s.SCENARIOS[self.generic_world.args.scenario]['COIN_COUNT'])

        # Assert that the length of active_agents is correct
        self.assertEqual(len(active_agents), len(self.generic_world.agents))

if __name__ == '__main__':
    unittest.main()