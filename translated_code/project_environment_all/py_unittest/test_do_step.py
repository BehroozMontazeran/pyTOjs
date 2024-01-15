import unittest
from environment_all import GenericWorld

class GenericWorldTestCase(unittest.TestCase):
    def setUp(self):
        self.world = GenericWorld()

    def test_do_step(self):
        # Test initial values
        self.assertTrue(self.world.running)
        self.assertEqual(self.world.step, 0)
        self.assertEqual(self.world.user_input, '')

        # Call the do_step method with a specific user_input
        self.world.do_step('MOVE_LEFT')

        # Assert that the step count and user_input are updated correctly
        self.assertEqual(self.world.step, 1)
        self.assertEqual(self.world.user_input, 'MOVE_LEFT')

        # Assert that additional methods are called
        self.assertTrue(self.world.poll_and_run_agents_called)
        self.assertTrue(self.world.collect_coins_called)
        self.assertTrue(self.world.update_explosions_called)
        self.assertTrue(self.world.update_bombs_called)
        self.assertTrue(self.world.evaluate_explosions_called)
        self.assertTrue(self.world.send_game_events_called)

        # Assert that the end_round method is not called
        self.assertFalse(self.world.end_round_called)

    def test_do_step_default_input(self):
        # Call the do_step method with default user_input (WAIT)
        self.world.do_step()

        # Assert that the user_input is updated correctly
        self.assertEqual(self.world.user_input, 'WAIT')

    def tearDown(self):
        self.world = None

if __name__ == '__main__':
    unittest.main()