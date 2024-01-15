const BombeRLeWorld = require('./environment_all');

class TestBombeRLeWorld {
  test_setup_agents() {
    const world = new BombeRLeWorld();
    const agents = [["agent1", true], ["agent2", false]];

    world.setup_agents(agents);

    assert.equal(world.agents.length, agents.length);
    assert.equal(world.agents[0].agent_dir, agents[0][0]);
    assert.equal(world.agents[0].name, agents[0][0]);
    assert.equal(world.agents[0].train, agents[0][1]);
    assert.equal(world.agents[1].agent_dir, agents[1][0]);
    assert.equal(world.agents[1].name, agents[1][0]);
    assert.equal(world.agents[1].train, agents[1][1]);
  }
}

const test = new TestBombeRLeWorld();
test.test_setup_agents();