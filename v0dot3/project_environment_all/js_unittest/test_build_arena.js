const GenericWorld = require('./environment_all');

class TestGenericWorld {
    constructor() {
        this.generic_world = new GenericWorld();
    }

    test_build_arena() {
        let {arena, coins, active_agents} = this.generic_world.build_arena();

        // Assert that the expected variables are returned
        console.assert(Array.isArray(arena), 'Arena is not an array');
        console.assert(Array.isArray(coins), 'Coins is not an array');
        console.assert(Array.isArray(active_agents), 'Active agents is not an array');

        // Assert that the shape of the arena is correct
        console.assert(arena.length === s.COLS && arena[0].length === s.ROWS, 'Incorrect arena shape');

        // Assert that the values in the arena array are correct
        console.assert(arena.includes(WALL), 'Arena does not contain WALL');
        console.assert(arena.includes(FREE), 'Arena does not contain FREE');
        console.assert(arena.includes(CRATE), 'Arena does not contain CRATE');

        // Assert that the number of coins is as expected
        console.assert(coins.length === s.SCENARIOS[this.generic_world.args.scenario]['COIN_COUNT'], 'Incorrect number of coins');

        // Assert that the length of active_agents is correct
        console.assert(active_agents.length === this.generic_world.agents.length, 'Incorrect length of active agents');
    }
}

const test = new TestGenericWorld();
test.test_build_arena();