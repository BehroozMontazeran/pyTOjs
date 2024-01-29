const log = require('logging');
const GenericWorld = require('environment_all');

class TestGenericWorld {
    setUp() {
        this.generic_world = new GenericWorld();
    }

    tearDown() {
        // Clean up any resources used by the test
        log.shutdown();
    }

    test_setup_logging() {
        // Call the method under test
        this.generic_world.setup_logging();

        // Check that the logger has been configured correctly
        const logger = log.getLogger('BombeRLeWorld');
        assert.equal(logger.level, log.DEBUG);

        // Check that the logger has the expected handlers
        assert.ok(logger.handlers.some(handler => handler instanceof log.FileHandler));

        // Check that the logger's formatter is set correctly
        for (const handler of logger.handlers) {
            if (handler instanceof log.FileHandler) {
                const formatter = handler.formatter;
                assert.equal(formatter._fmt, '%(asctime)s [%(name)s] %(levelname)s: %(message)s');
            }
        }

        // Check that the logger has logged the expected message
        assert.include(this.generic_world.logger.messages, 'Initializing game world');
    }
}

if (require.main === module) {
    const test = new TestGenericWorld();
    test.setUp();
    test.test_setup_logging();
}