JavaScript Unit Test:

const BombeRLeWorld = require('./environment_all');
const Agent = require('./agent');

test('test_get_state_for_agent', () => {
    // Setup
    const world = new BombeRLeWorld();
    const agent = new Agent(); // Assuming Agent class is defined

    // Exercise
    const state = world.get_state_for_agent(agent);

    // Verify
    expect(state).toBeDefined();
    expect(typeof state).toBe('object');
    expect(state).toHaveProperty('round');
    expect(state).toHaveProperty('step');
    expect(state).toHaveProperty('field');
    expect(state).toHaveProperty('self');
    expect(state).toHaveProperty('others');
    expect(state).toHaveProperty('bombs');
    expect(state).toHaveProperty('coins');
    expect(state).toHaveProperty('user_input');
    expect(state).toHaveProperty('explosion_map');

    const explosion_map = state['explosion_map'];
    expect(explosion_map).toBeInstanceOf(Array);
    expect(explosion_map.length).toBe(world.arena.length);
});