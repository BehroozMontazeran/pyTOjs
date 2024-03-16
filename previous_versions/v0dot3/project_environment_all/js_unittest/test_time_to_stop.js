const assert = require('assert');
const GenericWorld = require('./environment_all').GenericWorld;

describe('TestGenericWorld', function() {
    it('test_time_to_stop', function() {
        let world = new GenericWorld();

        // Test case 1: No active agents
        world.active_agents = [];
        assert.strictEqual(world.time_to_stop(), true);

        // Test case 2: One active agent, no arena, no collectable coins, no bombs or explosions
        world.active_agents = [new Agent()];
        world.arena = new Array(10).fill(0).map(() => new Array(10).fill(0));
        world.coins = [new Coin(false), new Coin(false)];
        world.bombs = [];
        world.explosions = [];
        assert.strictEqual(world.time_to_stop(), true);

        // Test case 3: No training agent left alive
        world.active_agents = [new Agent(false)];
        assert.strictEqual(world.time_to_stop(), false);
        world.active_agents = [new Agent(true)];
        assert.strictEqual(world.time_to_stop(), false);

        // Test case 4: Maximum number of steps reached
        world.step = s.MAX_STEPS;
        assert.strictEqual(world.time_to_stop(), true);

        // Test case 5: Default case
        world.active_agents = [new Agent()];
        world.arena = new Array(10).fill(0).map(() => new Array(10).fill(1));
        world.coins = [new Coin(true)];
        world.bombs = [new Bomb()];
        world.explosions = [new Explosion()];
        assert.strictEqual(world.time_to_stop(), false);
    });
});