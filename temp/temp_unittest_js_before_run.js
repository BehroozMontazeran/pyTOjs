const GenericWorld = require('./environment_all');

describe('TestGenericWorld', () => {
    test('test_setup_logging', () => {
        // Create an instance of GenericWorld
        const world = new GenericWorld();
        
        // Call the setup_logging method
        world.setup_logging();
        
        // Assert that logger is created and set to the correct level
        expect(world.logger).toBeDefined();
        expect(world.logger.level).toBe(logging.DEBUG);
        
        // Assert that the logger has the correct handler and formatter
        const handlers = world.logger.handlers;
        expect(handlers.length).toBe(1);
        const handler = handlers[0];
        expect(handler).toBeInstanceOf(logging.FileHandler);
        expect(handler.level).toBe(logging.DEBUG);
        const formatter = handler.formatter;
        expect(formatter).toBeInstanceOf(logging.Formatter);
        expect(formatter._fmt).toBe('%(asctime)s [%(name)s] %(levelname)s: %(message)s');
        
        // Assert that the logger has the correct log directory and log file
        expect(world.args.log_dir).toBe('your_log_directory');
        expect(handler.baseFilename).toBe('your_log_directory/game.log');
        
        // Assert that an info log message is logged
        const logs = handler.stream.getvalue();
        expect(logs).toContain('Initializing game world');
    });
});