import unittest
from environment_all import GUI

class GUITest(unittest.TestCase):

    def setUp(self):
        self.gui = GUI()  # Instantiate the GUI object

    def test_make_video(self):
        self.gui.world.args.make_video = True
        self.gui.world.round_id = 1
        self.gui.world.logger = MockLogger()  # Create a mock logger object

        # Call the make_video method
        self.gui.make_video()

        # Assert that the videos are created
        expected_files = self.gui.screenshot_dir / '1_video.mp4', self.gui.screenshot_dir / '1_video.webm'
        for file in expected_files:
            self.assertTrue(file.exists(), f"Video file {file} was not created.")

        # Assert that the log messages are correct
        self.assertEqual(self.gui.world.logger.debug_calls[0], "Turning screenshots into video")
        self.assertEqual(self.gui.world.logger.info_calls[0], "Done writing videos.")

        # Assert that the screenshot files are deleted
        for file in self.gui.screenshot_dir.glob('1_*.png'):
            self.assertFalse(file.exists(), f"Screenshot file {file} was not deleted.")

class MockLogger:
    def __init__(self):
        self.debug_calls = []
        self.info_calls = []

    def debug(self, msg):
        self.debug_calls.append(msg)

    def info(self, msg):
        self.info_calls.append(msg)

if __name__ == '__main__':
    unittest.main()