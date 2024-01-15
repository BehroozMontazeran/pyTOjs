const GenericWorld = require('./environment_all');

class TestGenericWorld {
    test_perform_agent_action() {
        const world = new GenericWorld(); // Create an instance of the GenericWorld class
        
        // Create a mock Agent object with required attributes and methods
        class MockAgent {
            constructor() {
                this.x = 0; // Initial x-coordinate of the agent
                this.y = 0; // Initial y-coordinate of the agent
                this.bombs_left = true;
                this.name = "Agent1";
                this.add_event = event => { }
            }
        }

        const agent = new MockAgent(); // Create an instance of the MockAgent class

        // Test the 'UP' action
        world.perform_agent_action(agent, 'UP');
        expect(agent.y).toBe(-1);
        expect(agent.add_event.mock.calls.length).toBe(1);

        // Test the 'DOWN' action
        agent.y = 0; // Reset the agent's y-coordinate
        world.perform_agent_action(agent, 'DOWN');
        expect(agent.y).toBe(1);
        expect(agent.add_event.mock.calls.length).toBe(2);

        // Test the 'LEFT' action
        agent.y = 0; // Reset the agent's y-coordinate
        world.perform_agent_action(agent, 'LEFT');
        expect(agent.x).toBe(-1);
        expect(agent.add_event.mock.calls.length).toBe(3);

        // Test the 'RIGHT' action
        agent.x = 0; // Reset the agent's x-coordinate
        world.perform_agent_action(agent, 'RIGHT');
        expect(agent.x).toBe(1);
        expect(agent.add_event.mock.calls.length).toBe(4);

        // Test the 'BOMB' action
        agent.bombs_left = true; // Reset the agent's bombs_left attribute
        world.perform_agent_action(agent, 'BOMB');
        expect(agent.bombs_left).toBeFalsy(); // Assert that bombs_left is False
        expect(agent.add_event.mock.calls.length).toBe(5);

        // Test the 'WAIT' action
        world.perform_agent_action(agent, 'WAIT');
        expect(agent.add_event.mock.calls.length).toBe(6);

        // Test an invalid action
        agent.add_event.mockReset(); // Reset the add_event mock
        world.perform_agent_action(agent, 'INVALID_ACTION');
        expect(agent.add_event.mock.calls.length).toBe(1);
    }
}

const test = new TestGenericWorld();
test.test_perform_agent_action();