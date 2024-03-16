import unittest
from environment_all import BombeRLeWorld

class TestBombeRLeWorld(unittest.TestCase):
    def test_setup_agents(self):
        world = BombeRLeWorld()
        agents = [("agent1", True), ("agent2", False)]

        world.setup_agents(agents)

        self.assertEqual(len(world.agents), len(agents))
        self.assertEqual(world.agents[0].agent_dir, agents[0][0])
        self.assertEqual(world.agents[0].name, agents[0][0])
        self.assertEqual(world.agents[0].train, agents[0][1])
        self.assertEqual(world.agents[1].agent_dir, agents[1][0])
        self.assertEqual(world.agents[1].name, agents[1][0])
        self.assertEqual(world.agents[1].train, agents[1][1])

if __name__ == '__main__':
    unittest.main()