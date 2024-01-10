import unittest
from ..project_environment_all.environment_all import GenericWorld

class TestGenericWorld(unittest.TestCase):

    def test_add_agent(self):
        world = GenericWorld()
        
        agent_dir = "agent_directory"
        name = "agent1"
        train = True

        # Call the add_agent method
        world.add_agent(agent_dir, name, train)

        # Verify the agent has been added to the agents list
        self.assertEqual(len(world.agents), 1)
        agent = world.agents[0]
        self.assertEqual(agent.agent_dir, agent_dir)
        self.assertEqual(agent.name, name)
        self.assertEqual(agent.train, train)
        self.assertIsInstance(agent.backend, SequentialAgentBackend)
        self.assertEqual(agent.backend.train, train)
        self.assertEqual(agent.backend.name, name)
        self.assertEqual(agent.color, agent.color)

        # Verify that color has been popped from the colors list
        self.assertEqual(len(world.colors), s.MAX_AGENTS - 1)

        # Verify assertion error is raised when maximum agents is exceeded
        with self.assertRaises(AssertionError):
            # Add more agents to exceed the maximum limit
            for i in range(s.MAX_AGENTS):
                world.add_agent(agent_dir, f"agent{i+2}", train)