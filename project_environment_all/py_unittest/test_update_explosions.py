import unittest
from environment_all import GenericWorld

class GenericWorldTestCase(unittest.TestCase):
    def test_update_explosions(self):
        world = GenericWorld()
        explosion1 = Explosion()
        explosion1.timer = 5
        explosion1.stage = 1
        world.explosions.append(explosion1)
        explosion2 = Explosion()
        explosion2.timer = 0
        explosion2.stage = None
        world.explosions.append(explosion2)
        explosion3 = Explosion()
        explosion3.timer = 2
        explosion3.stage = 2
        world.explosions.append(explosion3)

        world.update_explosions()

        self.assertEqual(len(world.explosions), 2)
        self.assertEqual(world.explosions[0].timer, 4)
        self.assertEqual(world.explosions[0].stage, 1)
        self.assertEqual(world.explosions[1].timer, 1)
        self.assertEqual(world.explosions[1].stage, 2)

if __name__ == '__main__':
    unittest.main()