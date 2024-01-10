import unittest
from ..project_environment_all.environment_all import GenericWorld

class TestGenericWorld(unittest.TestCase):

    def test_perform_agent_action(self):
        # Create an instance of GenericWorld and mock Agent
        world = GenericWorld()
        agent = Agent()
        action = 'UP'

        # Call the method under test
        world.perform_agent_action(agent, action)

        # Assert the expected behavior
        self.assertEqual(agent.y, agent.y - 1)
        self.assertEqual(agent.events, [e.MOVED_UP])

        # Repeat the above process for other actions, assertions, and agents
        
        # Example for action 'DOWN'
        world.perform_agent_action(agent, 'DOWN')
        self.assertEqual(agent.y, agent.y + 1)
        self.assertEqual(agent.events, [e.MOVED_DOWN])

        # Example for action 'LEFT'
        world.perform_agent_action(agent, 'LEFT')
        self.assertEqual(agent.x, agent.x - 1)
        self.assertEqual(agent.events, [e.MOVED_LEFT])

        # Example for action 'RIGHT'
        world.perform_agent_action(agent, 'RIGHT')
        self.assertEqual(agent.x, agent.x + 1)
        self.assertEqual(agent.events, [e.MOVED_RIGHT])

        # Example for action 'BOMB'
        agent.bombs_left = True
        world.perform_agent_action(agent, 'BOMB')
        self.assertTrue(agent.bombs_left)
        self.assertEqual(len(world.bombs), 1)
        self.assertEqual(agent.events, [e.BOMB_DROPPED])

        # Example for action 'WAIT'
        world.perform_agent_action(agent, 'WAIT')
        self.assertEqual(agent.events, [e.WAITED])

        # Example for invalid action
        agent.events.clear()
        world.perform_agent_action(agent, 'INVALID')
        self.assertEqual(agent.events, [e.INVALID_ACTION])


if __name__ == '__main__':
    unittest.main()