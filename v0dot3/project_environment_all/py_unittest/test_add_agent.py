import unittest
from environment_all import GenericWorld

class TestGenericWorld(unittest.TestCase):
    def test_add_agent(self):
        world = GenericWorld()
        
        agent_dir = "agent_directory"
        name = "agent_name"
        train = True
        
        world.add_agent(agent_dir, name, train)
        
        # Assert that an agent is added to the agents list
        self.assertEqual(len(world.agents), 1)
        
        # Assert that the added agent has the correct attributes
        added_agent = world.agents[0]
        self.assertEqual(added_agent.agent_dir, agent_dir)
        self.assertEqual(added_agent.name, name)
        self.assertEqual(added_agent.train, train)
        
        # Assert that the added agent has a backend that is started
        self.assertTrue(added_agent.backend.started)
        
        # Assert that the added agent has a color assigned
        self.assertIsNotNone(added_agent.color)
        self.assertNotIn(added_agent.color, world.colors)

if __name__ == '__main__':
    unittest.main()