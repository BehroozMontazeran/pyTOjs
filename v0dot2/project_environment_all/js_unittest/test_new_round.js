const { DateTime } = require('luxon');
const GenericWorld = require('../path/to/GenericWorld');

describe('TestGenericWorld', () => {
  let genericWorld;

  beforeEach(() => {
    genericWorld = new GenericWorld();
  });

  test('test_new_round', () => {
    // Mock necessary dependencies
    genericWorld.logger = { warning: jest.fn() };
    genericWorld.build_arena = jest.fn().mockReturnValue([Array(5).fill(0), [], []]);
    genericWorld.active_agents = Array(2).fill().map(() => ({ start_round: jest.fn() }));

    // Call the method
    genericWorld.new_round();

    // Assertions on method behavior
    expect(genericWorld.running).toBe(false);
    expect(genericWorld.logger.warning).toHaveBeenCalledWith('New round requested while still running');
    expect(genericWorld.end_round).toHaveBeenCalledTimes(1);
    expect(genericWorld.round).toBe(1);
    expect(genericWorld.step).toBe(0);
    expect(genericWorld.bombs).toEqual([]);
    expect(genericWorld.explosions).toEqual([]);
    expect(genericWorld.round_id).toBe(`Round 01 (${DateTime.now().toFormat('yyyy-MM-dd HH-mm-ss')})`);
    expect(genericWorld.build_arena).toHaveBeenCalledTimes(1);
    genericWorld.active_agents.forEach(agent => {
      expect(agent.start_round).toHaveBeenCalledTimes(1);
    });
    expect(genericWorld.replay.round).toBe(1);
    expect(genericWorld.replay.arena).toEqual(Array(5).fill().map(() => Array(5).fill(0)));
    expect(genericWorld.replay.coins).toEqual([]);
    expect(genericWorld.replay.agents).toEqual([]);
    expect(genericWorld.replay.actions).toEqual({});
    expect(genericWorld.replay.permutations).toEqual([]);
  });
});