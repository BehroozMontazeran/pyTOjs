import unittest
from environment_all import BombeRLeWorld

class BombeRLeWorldTest(unittest.TestCase):
    def test_get_state_for_agent(self):
        # Setup
        world = BombeRLeWorld()
        agent = Agent()  # Assuming Agent class is defined
        
        # Exercise
        state = world.get_state_for_agent(agent)
        
        # Verify
        self.assertIsNotNone(state)
        self.assertIsInstance(state, dict)
        self.assertIn('round', state)
        self.assertIn('step', state)
        self.assertIn('field', state)
        self.assertIn('self', state)
        self.assertIn('others', state)
        self.assertIn('bombs', state)
        self.assertIn('coins', state)
        self.assertIn('user_input', state)
        self.assertIn('explosion_map', state)
        
        explosion_map = state['explosion_map']
        self.assertIsInstance(explosion_map, np.ndarray)
        self.assertEqual(explosion_map.shape, world.arena.shape)
        
        # Cleanup (if necessary)
        
if __name__ == '__main__':
    unittest.main()