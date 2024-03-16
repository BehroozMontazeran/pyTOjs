import unittest
from environment_all import GenericWorld

class TestCollectCoins(unittest.TestCase):
    def test_collect_coins(self):
        # Arrange
        world = GenericWorld()  # Create an instance of the GenericWorld class
        coin = Coin()  # Create a Coin instance
        agent = Agent()  # Create an Agent instance
        
        # Set the necessary properties for the coin and agent
        coin.collectable = True
        coin.x = agent.x
        coin.y = agent.y
        agent.score = 0
        agent.events = []
        agent.trophies = []
        
        # Add the coin and agent to the world
        world.coins = [coin]
        world.active_agents = [agent]
        
        expected_log = f"Agent <{agent.name}> picked up coin at {(agent.x, agent.y)} and receives 1 point"
        
        # Act
        world.collect_coins()  # Call the collect_coins method
        
        # Assert
        self.assertFalse(coin.collectable)  # Check that the 'collectable' property of the coin is set to False
        self.assertEqual(agent.score, 1)  # Check that the agent's score has been updated to 1
        self.assertIn(e.COIN_COLLECTED, agent.events)  # Check that the COIN_COLLECTED event has been added to the agent's events
        self.assertIn(Trophy.coin_trophy, agent.trophies)  # Check that the coin_trophy has been added to the agent's trophies
        self.assertIn(expected_log, world.logger.info.call_args[0][0])  # Check that the expected log message has been logged

if __name__ == '__main__':
    unittest.main()