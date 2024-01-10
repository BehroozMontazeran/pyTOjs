import unittest

from environment_all import GenericWorld

class TestGenericWorld(unittest.TestCase):
    def test_setup_logging(self):
        # Create an instance of GenericWorld
        world = GenericWorld()
        
        # Call the setup_logging method
        world.setup_logging()
        
        # Assert that logger is created and set to the correct level
        self.assertIsNotNone(world.logger)
        self.assertEqual(world.logger.level, logging.DEBUG)
        
        # Assert that the logger has the correct handler and formatter
        handlers = world.logger.handlers
        self.assertEqual(len(handlers), 1)
        handler = handlers[0]
        self.assertIsInstance(handler, logging.FileHandler)
        self.assertEqual(handler.level, logging.DEBUG)
        formatter = handler.formatter
        self.assertIsInstance(formatter, logging.Formatter)
        self.assertEqual(formatter._fmt, '%(asctime)s [%(name)s] %(levelname)s: %(message)s')
        
        # Assert that the logger has the correct log directory and log file
        self.assertEqual(world.args.log_dir, 'your_log_directory')
        self.assertEqual(handler.baseFilename, 'your_log_directory/game.log')
        
        # Assert that an info log message is logged
        logs = handler.stream.getvalue()
        self.assertIn('Initializing game world', logs)


if __name__ == '__main__':
    unittest.main()