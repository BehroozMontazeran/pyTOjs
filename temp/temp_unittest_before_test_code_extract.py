Here's a unit test for the `new_round` method of the `GenericWorld` class:

```python
import unittest
from project_environment_all.environment_all import GenericWorld

class GenericWorldTestCase(unittest.TestCase):
    def test_new_round(self):
        world = GenericWorld()
        world.running = True
        world.round = 5
        world.args = MagicMock()
        world.args.match_name = None
        world.logger = MagicMock()
        world.build_arena = MagicMock(return_value=([], [], []))
        agent1 = MagicMock()
        agent2 = MagicMock()
        world.active_agents = [agent1, agent2]
        agent1.start_round = MagicMock()
        agent2.start_round = MagicMock()

        world.new_round()

        self.assertFalse(world.running)
        self.assertEqual(world.round, 6)
        self.assertEqual(world.step, 0)
        self.assertEqual(world.bombs, [])
        self.assertEqual(world.explosions, [])
        self.assertEqual(world.round_id, "Round 06 (2022-01-01 00:00:00)")
        self.assertEqual(world.arena, [])
        self.assertEqual(world.coins, [])
        self.assertEqual(world.agents, [])
        self.assertEqual(world.replay["round"], 6)
        self.assertEqual(world.replay["arena"], [])
        self.assertEqual(world.replay["coins"], [])
        self.assertEqual(world.replay["agents"], [])
        self.assertEqual(world.replay["actions"], {})
        self.assertEqual(world.replay["permutations"], [])
        world.logger.warning.assert_called_with('New round requested while still running')
        self.assertTrue(agent1.start_round.called)
        self.assertTrue(agent2.start_round.called)

if __name__ == '__main__':
    unittest.main()
```

Note that you will need to replace the `MagicMock` objects and their method calls with relevant setups and assertions specific to your test case. This example demonstrates how to mock certain attributes and methods to isolate the behavior of the `new_round` method.