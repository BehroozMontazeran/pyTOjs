import unittest
from environment_all import GenericWorld

class TestGenericWorld(unittest.TestCase):
    def setUp(self):
        self.world = GenericWorld()  # Create an instance of the GenericWorld class

    def tearDown(self):
        self.world = None  # Clear the instance after each test

    def test_new_round(self):
        # Test that the method sets the correct attributes and starts the round
        self.world.running = False
        self.world.round = 5

        self.world.new_round()

        # Check the new round attributes
        self.assertEqual(self.world.round, 6)
        self.assertEqual(self.world.step, 0)
        self.assertEqual(self.world.bombs, [])
        self.assertEqual(self.world.explosions, [])
        self.assertTrue(self.world.running)

        # Check the round_id format
        expected_round_id = f"Round 06 ({datetime.now().strftime('%Y-%m-%d %H-%M-%S')})"
        self.assertEqual(self.world.round_id, expected_round_id)

        # Check that other method calls are made
        self.assertTrue(self.world.build_arena.called)
        for agent in self.world.active_agents:
            self.assertTrue(agent.start_round.called)

        # Check the replay dictionary
        self.assertEqual(self.world.replay['round'], 6)
        self.assertEqual(self.world.replay['arena'].shape, (expected_arena_size,))
        self.assertEqual(len(self.world.replay['coins']), expected_num_coins)
        self.assertEqual(len(self.world.replay['agents']), len(self.world.active_agents))
        self.assertEqual(len(self.world.replay['actions']), len(self.world.active_agents))
        self.assertEqual(len(self.world.replay['permutations']), expected_num_permutations)