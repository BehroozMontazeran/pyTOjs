Javascript unit test:

import { GenericWorld } from './environment_all';

class TestGenericWorld {
  test_send_game_events() {
    // Initialize GenericWorld instance
    let world = new GenericWorld();

    // Add agents to the world
    world.agents = ['agent1', 'agent2'];

    // Add active agents to the world
    world.active_agents = ['agent2'];

    // Set agent1 parameters
    let agent1 = 'agent1';  // Replace with actual agent object
    agent1.train = true;
    agent1.dead = false;

    // Set agent2 parameters
    let agent2 = 'agent2';  // Replace with actual agent object
    agent2.train = true;
    agent2.dead = false;

    // Stub process_game_events and wait_for_game_event_processing methods
    function process_game_events(state) {
      // Do nothing
    }

    function wait_for_game_event_processing() {
      // Do nothing
    }

    // Replace agent methods with stubs
    agent1.process_game_events = process_game_events;
    agent1.wait_for_game_event_processing = wait_for_game_event_processing;

    agent2.process_game_events = process_game_events;
    agent2.wait_for_game_event_processing = wait_for_game_event_processing;

    // Call the send_game_events method
    world.send_game_events();

    // Assert that process_game_events and wait_for_game_event_processing are called for agent1
    if (agent1.process_game_events.call_count !== 1) {
      console.error('Test failed: process_game_events should be called once for agent1');
    }

    if (agent1.wait_for_game_event_processing.call_count !== 1) {
      console.error('Test failed: wait_for_game_event_processing should be called once for agent1');
    }

    // Assert that process_game_events and wait_for_game_event_processing are not called for agent2
    if (agent2.process_game_events.call_count !== 0) {
      console.error('Test failed: process_game_events should not be called for agent2');
    }

    if (agent2.wait_for_game_event_processing.call_count !== 0) {
      console.error('Test failed: wait_for_game_event_processing should not be called for agent2');
    }
  }
}

let test = new TestGenericWorld();
test.test_send_game_events();