import unittest
from environment_all import GenericWorld

class TestGenericWorld(unittest.TestCase):

    def test_update_bombs(self):
        # Arrange
        world = GenericWorld()
        world.bombs = [
            Bomb(1, 1, 3),
            Bomb(2, 2, 2),
            Bomb(3, 3, 1)
        ]

        # Act
        world.update_bombs()

        # Assert
        self.assertEqual(len(world.explosions), 2)
        self.assertEqual(world.explosions[0].coords, [(1, 1), (2, 2), (3, 3)])
        self.assertEqual(world.explosions[1].coords, [(2, 2), (3, 3)])
        self.assertEqual(world.explosions[0].screen_coords, [(21, 21), (22, 22), (23, 23)])
        self.assertEqual(world.explosions[1].screen_coords, [(22, 22), (23, 23)])
        self.assertEqual(world.explosions[0].owner, None)
        self.assertEqual(world.explosions[1].owner, None)
        self.assertFalse(world.bombs[0].active)
        self.assertFalse(world.bombs[1].active)
        self.assertFalse(world.bombs[2].active)


if __name__ == '__main__':
    unittest.main()