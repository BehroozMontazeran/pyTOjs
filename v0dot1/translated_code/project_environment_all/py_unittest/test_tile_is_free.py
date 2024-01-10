from ..project_environment_all.environment_all import GenericWorld
import unittest

class TestGenericWorld(unittest.TestCase):
    def test_tile_is_free(self):
        # Arrange
        world = GenericWorld()  # Create an instance of the GenericWorld class
        world.arena = {
            (0, 0): 0,
            (0, 1): 1,
            (1, 0): 1,
            (1, 1): 0
        }  # Set up the arena dictionary with some values
        
        world.bombs = [
            Bomb(1, 0),
            Bomb(0, 1)
        ]  # Set up the bombs list with some values
        
        world.active_agents = [
            Agent(0, 0),
            Agent(1, 1)
        ]  # Set up the active_agents list with some values

        # Act
        result1 = world.tile_is_free(0, 0)  # Calling tile_is_free method with different inputs
        result2 = world.tile_is_free(0, 1)
        result3 = world.tile_is_free(1, 0)
        result4 = world.tile_is_free(1, 1)
        
        # Assert
        self.assertTrue(result1)  # assert that the result1 is True
        self.assertFalse(result2)  # assert that the result2 is False
        self.assertFalse(result3)  # assert that the result3 is False
        self.assertTrue(result4)  # assert that the result4 is True
        
class Bomb:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
class Agent:
    def __init__(self, x, y):
        self.x = x
        self.y = y

unittest.main()