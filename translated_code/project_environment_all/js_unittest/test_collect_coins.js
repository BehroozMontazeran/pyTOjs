JavaScript unit test:

const GenericWorld = require('./EnvironmentAll').GenericWorld;

describe('CollectCoins', () => {
    test('collect_coins', () => {
        // Arrange
        const world = new GenericWorld();  // Create an instance of the GenericWorld class
        const coin = new Coin();  // Create a Coin instance
        const agent = new Agent();  // Create an Agent instance
        
        // Set the necessary properties for the coin and agent
        coin.collectable = true;
        coin.x = agent.x;
        coin.y = agent.y;
        agent.score = 0;
        agent.events = [];
        agent.trophies = [];
        
        // Add the coin and agent to the world
        world.coins = [coin];
        world.active_agents = [agent];
        
        const expected_log = `Agent <${agent.name}> picked up coin at (${agent.x}, ${agent.y}) and receives 1 point`;
        
        // Act
        world.collect_coins();  // Call the collect_coins method
        
        // Assert
        expect(coin.collectable).toBe(false);  // Check that the 'collectable' property of the coin is set to false
        expect(agent.score).toBe(1);  // Check that the agent's score has been updated to 1
        expect(agent.events).toContain(e.COIN_COLLECTED);  // Check that the COIN_COLLECTED event has been added to the agent's events
        expect(agent.trophies).toContain(Trophy.coin_trophy);  // Check that the coin_trophy has been added to the agent's trophies
        expect(world.logger.info.mock.calls[0][0]).toContain(expected_log);  // Check that the expected log message has been logged
    });
});