from environment_all import GenericWorld
import unittest

class TestGenericWorld(unittest.TestCase):
    def setUp(self):
        self.world = GenericWorld()

    def test_tile_is_free(self):
        '''
        Test case to check if a tile is free.
        '''
        # Arrange
        self.world.arena = {
            (0, 0): 0,
            (1, 1): 1,
            (2, 2): 0
        }
        self.world.bombs = []
        self.world.active_agents = []

        # Act
        result_1 = self.world.tile_is_free(0, 0)  # Free tile
        result_2 = self.world.tile_is_free(1, 1)  # Occupied tile
        result_3 = self.world.tile_is_free(2, 2)  # Free tile

        # Assert
        self.assertTrue(result_1)
        self.assertFalse(result_2)
        self.assertTrue(result_3)

if __name__ == '__main__':
    unittest.main()