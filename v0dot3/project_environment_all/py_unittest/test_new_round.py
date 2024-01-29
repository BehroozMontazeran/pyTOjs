from datetime import datetime
import numpy as np
import unittest
from unittest.mock import Mock
from environment_all import GenericWorld

class TestGenericWorld(unittest.TestCase):
    def setUp(self):
        self.generic_world = GenericWorld()
    
    def test_new_round(self):
        # Mock necessary dependencies
        self.generic_world.logger = Mock()
        self.generic_world.build_arena = Mock(return_value=(np.zeros((5, 5)), [], []))
        self.generic_world.active_agents = [Mock() for _ in range(2)]
        for agent in self.generic_world.active_agents:
            agent.start_round = Mock()
        
        # Call the method
        self.generic_world.new_round()
        
        # Assertions on method behavior
        self.assertFalse(self.generic_world.running)
        self.generic_world.logger.warning.assert_called_with('New round requested while still running')
        self.generic_world.end_round.assert_called_once()
        self.assertEqual(self.generic_world.round, 1)
        self.assertEqual(self.generic_world.step, 0)
        self.assertEqual(self.generic_world.bombs, [])
        self.assertEqual(self.generic_world.explosions, [])
        self.assertEqual(self.generic_world.round_id, f"Round 01 ({datetime.now().strftime('%Y-%m-%d %H-%M-%S')})")
        self.generic_world.build_arena.assert_called_once()
        for agent in self.generic_world.active_agents:
            agent.start_round.assert_called_once()
        self.assertEqual(self.generic_world.replay['round'], 1)
        self.assertTrue(np.array_equal(self.generic_world.replay['arena'], np.zeros((5, 5))))
        self.assertEqual(self.generic_world.replay['coins'], [])
        self.assertEqual(self.generic_world.replay['agents'], [])
        self.assertEqual(self.generic_world.replay['actions'], dict())
        self.assertEqual(self.generic_world.replay['permutations'], [])