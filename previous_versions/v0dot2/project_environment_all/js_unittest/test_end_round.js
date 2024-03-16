const { TestGenericWorld } = require('./environment_all');

test('TestGenericWorld - test_end_round', () => {
  // Mocking dependencies
  const mock_open = jest.fn();
  const mock_os = jest.fn();
  const mock_logger = jest.fn();
  const mock_agents = jest.fn();
  const mock_active_agents = jest.fn();
  
  // Setting up test data
  const world = new TestGenericWorld();
  world.round = 42;
  const agent1 = { score: 10, code_name: 'Agent1', train: true };
  const agent2 = { score: 15, code_name: 'Agent2', train: false };
  world.agents = [agent1, agent2];
  world.active_agents = [agent1, agent2];
  world.args = { save_replay: true };
  
  // Mocking object methods
  const mock_logger_info = jest.spyOn(world.logger, 'info');
  const mock_active_agents_add_event = jest.spyOn(world.active_agents[0], 'add_event');
  const mock_agents_round_ended = jest.spyOn(world.agents[0], 'round_ended');
  
  // Mocking built-in functions
  jest.spyOn(global, 'open').mockImplementation(mock_open);
  jest.spyOn(global, 'os').mockImplementation(mock_os);
  
  // Calling the method under test
  world.end_round();
  
  // Assertions
  expect(mock_logger_info).toHaveBeenCalledWith('WRAPPING UP ROUND #42');
  expect(mock_active_agents_add_event).toHaveBeenCalledWith('SURVIVED_ROUND');
  expect(mock_agents_round_ended).toHaveBeenCalled();
  expect(mock_open).toHaveBeenCalledWith('elo/elo.log', 'a');
  expect(mock_os).toHaveBeenCalledWith('elo');
  expect(mock_os().mkdir).toHaveBeenCalledWith('elo');
  expect(mock_os().mkdir).toHaveBeenCalledTimes(1);
  expect(mock_open().write).toHaveBeenCalledWith('Agent1 < Agent2\n');
  expect(mock_open().__exit__).toHaveBeenCalledTimes(1);
  expect(mock_os().__eqal__).toHaveBeenCalledTimes(1);
  
  // Resetting mocks
  mock_open.mockReset();
  mock_os.mockReset();
  mock_logger_info.mockReset();
  mock_agents_round_ended.mockReset();
  mock_active_agents_add_event.mockReset();
  
  // Testing with different score comparison
  agent1.score = 10;
  agent2.score = 10;
  world.end_round();
  
  // Assertions
  expect(mock_logger_info).toHaveBeenCalledWith('WRAPPING UP ROUND #42');
  expect(mock_active_agents_add_event).toHaveBeenCalledWith('SURVIVED_ROUND');
  expect(mock_agents_round_ended).toHaveBeenCalled();
  expect(mock_open).not.toHaveBeenCalled();
  expect(mock_os).not.toHaveBeenCalled();
  
  // Cleaning up patches
  mock_logger_info.mockRestore();
  mock_active_agents_add_event.mockRestore();
  mock_agents_round_ended.mockRestore();
  mock_open.mockRestore();
  mock_os.mockRestore();
});