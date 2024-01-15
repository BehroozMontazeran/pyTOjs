import unittest
from environment_all import GenericWorld

class TestGenericWorld(unittest.TestCase):
    def test_send_game_events(self):
        # Initialize GenericWorld instance
        world = GenericWorld()

        # Add agents to the world
        world.agents = ['agent1', 'agent2']

        # Add active agents to the world
        world.active_agents = ['agent2']

        # Set agent1 parameters
        agent1 = 'agent1'  # Replace with actual agent object
        agent1.train = True
        agent1.dead = False

        # Set agent2 parameters
        agent2 = 'agent2'  # Replace with actual agent object
        agent2.train = True
        agent2.dead = False

        # Stub process_game_events and wait_for_game_event_processing methods
        def process_game_events(state):
            pass

        def wait_for_game_event_processing():
            pass

        # Replace agent methods with stubs
        agent1.process_game_events = process_game_events
        agent1.wait_for_game_event_processing = wait_for_game_event_processing

        agent2.process_game_events = process_game_events
        agent2.wait_for_game_event_processing = wait_for_game_event_processing

        # Call the send_game_events method
        world.send_game_events()

        # Assert that process_game_events and wait_for_game_event_processing are called for agent1
        self.assertEqual(agent1.process_game_events.call_count, 1)
        self.assertEqual(agent1.wait_for_game_event_processing.call_count, 1)

        # Assert that process_game_events and wait_for_game_event_processing are not called for agent2
        self.assertEqual(agent2.process_game_events.call_count, 0)
        self.assertEqual(agent2.wait_for_game_event_processing.call_count, 0)

if __name__ == '__main__':
    unittest.main()