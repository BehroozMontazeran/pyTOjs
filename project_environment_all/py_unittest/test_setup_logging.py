import logging
import unittest
from environment_all import GenericWorld

class TestGenericWorld(unittest.TestCase):
    def setUp(self):
        self.generic_world = GenericWorld()

    def tearDown(self):
        # Clean up any resources used by the test
        logging.shutdown()

    def test_setup_logging(self):
        # Call the method under test
        self.generic_world.setup_logging()

        # Check that the logger has been configured correctly
        logger = logging.getLogger('BombeRLeWorld')
        self.assertEqual(logger.level, logging.DEBUG)

        # Check that the logger has the expected handlers
        self.assertTrue(any(isinstance(handler, logging.FileHandler) for handler in logger.handlers))

        # Check that the logger's formatter is set correctly
        for handler in logger.handlers:
            if isinstance(handler, logging.FileHandler):
                formatter = handler.formatter
                self.assertEqual(formatter._fmt, '%(asctime)s [%(name)s] %(levelname)s: %(message)s')

        # Check that the logger has logged the expected message
        self.assertIn('Initializing game world', self.generic_world.logger.messages)

if __name__ == '__main__':
    unittest.main()