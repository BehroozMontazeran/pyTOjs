import unittest
from environment_all import GenericWorld

class TestGenericWorld(unittest.TestCase):

    def test_perform_agent_action(self):
        world = GenericWorld()  # Create an instance of the GenericWorld class
        
        # Create a mock Agent object with required attributes and methods
        class MockAgent:
            def __init__(self):
                self.x = 0  # Initial x-coordinate of the agent
                self.y = 0  # Initial y-coordinate of the agent
                self.bombs_left = True
                self.name = "Agent1"
                self.add_event = lambda event: None

        agent = MockAgent()  # Create an instance of the MockAgent class
        
        # Test the 'UP' action
        world.perform_agent_action(agent, 'UP')
        self.assertEqual(agent.y, -1)
        self.assertEqual(agent.add_event.call_count, 1)
        
        # Test the 'DOWN' action
        agent.y = 0  # Reset the agent's y-coordinate
        world.perform_agent_action(agent, 'DOWN')
        self.assertEqual(agent.y, 1)
        self.assertEqual(agent.add_event.call_count, 2)
        
        # Test the 'LEFT' action
        agent.y = 0  # Reset the agent's y-coordinate
        world.perform_agent_action(agent, 'LEFT')
        self.assertEqual(agent.x, -1)
        self.assertEqual(agent.add_event.call_count, 3)
        
        # Test the 'RIGHT' action
        agent.x = 0  # Reset the agent's x-coordinate
        world.perform_agent_action(agent, 'RIGHT')
        self.assertEqual(agent.x, 1)
        self.assertEqual(agent.add_event.call_count, 4)
        
        # Test the 'BOMB' action
        agent.bombs_left = True  # Reset the agent's bombs_left attribute
        world.perform_agent_action(agent, 'BOMB')
        self.assertFalse(agent.bombs_left)  # Assert that bombs_left is False
        self.assertEqual(agent.add_event.call_count, 5)
        
        # Test the 'WAIT' action
        world.perform_agent_action(agent, 'WAIT')
        self.assertEqual(agent.add_event.call_count, 6)
        
        # Test an invalid action
        agent.add_event.reset_mock()  # Reset the add_event mock
        world.perform_agent_action(agent, 'INVALID_ACTION')
        self.assertEqual(agent.add_event.call_count, 1)

if __name__ == '__main__':
    unittest.main()