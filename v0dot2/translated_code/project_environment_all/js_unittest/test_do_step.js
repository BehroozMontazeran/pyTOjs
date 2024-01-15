const GenericWorld = require('./environment_all.js');

class GenericWorldTestCase {
    setUp() {
        this.world = new GenericWorld();
    }

    test_do_step() {
        // Test initial values
        assert(this.world.running);
        assert.strictEqual(this.world.step, 0);
        assert.strictEqual(this.world.user_input, '');

        // Call the do_step method with a specific user_input
        this.world.do_step('MOVE_LEFT');

        // Assert that the step count and user_input are updated correctly
        assert.strictEqual(this.world.step, 1);
        assert.strictEqual(this.world.user_input, 'MOVE_LEFT');

        // Assert that additional methods are called
        assert(this.world.poll_and_run_agents_called);
        assert(this.world.collect_coins_called);
        assert(this.world.update_explosions_called);
        assert(this.world.update_bombs_called);
        assert(this.world.evaluate_explosions_called);
        assert(this.world.send_game_events_called);

        // Assert that the end_round method is not called
        assert(!this.world.end_round_called);
    }

    test_do_step_default_input() {
        // Call the do_step method with default user_input (WAIT)
        this.world.do_step();

        // Assert that the user_input is updated correctly
        assert.strictEqual(this.world.user_input, 'WAIT');
    }

    tearDown() {
        this.world = null;
    }
}

if (require.main === module) {
    const test = new GenericWorldTestCase();
    test.setUp();
    test.test_do_step();
    test.test_do_step_default_input();
    test.tearDown();
}