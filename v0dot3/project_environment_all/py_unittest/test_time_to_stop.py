import unittest
from environment_all import GenericWorld

class TestGenericWorld(unittest.TestCase):
    def test_time_to_stop(self):
        world = GenericWorld()

        # Test case 1: No active agents
        world.active_agents = []
        self.assertTrue(world.time_to_stop())

        # Test case 2: One active agent, no arena, no collectable coins, no bombs or explosions
        world.active_agents = [Agent()]
        world.arena = np.zeros((10, 10))
        world.coins = [Coin(False), Coin(False)]
        world.bombs = []
        world.explosions = []
        self.assertTrue(world.time_to_stop())

        # Test case 3: No training agent left alive
        world.active_agents = [Agent(train=False)]
        self.assertFalse(world.time_to_stop())
        world.active_agents = [Agent(train=True)]
        self.assertFalse(world.time_to_stop())

        # Test case 4: Maximum number of steps reached
        world.step = s.MAX_STEPS
        self.assertTrue(world.time_to_stop())

        # Test case 5: Default case
        world.active_agents = [Agent()]
        world.arena = np.ones((10, 10))
        world.coins = [Coin(True)]
        world.bombs = [Bomb()]
        world.explosions = [Explosion()]
        self.assertFalse(world.time_to_stop())

if __name__ == '__main__':
    unittest.main()