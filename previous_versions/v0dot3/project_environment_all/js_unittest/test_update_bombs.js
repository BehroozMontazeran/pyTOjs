const { TestGenericWorld } = require('./path/to/your/testFile');
const { GenericWorld } = require('./path/to/your/GenericWorld');
const { Bomb } = require('./path/to/your/Bomb');

describe('TestGenericWorld', () => {
  test('test_update_bombs', () => {
    // Arrange
    const world = new GenericWorld();
    world.bombs = [
      new Bomb(1, 1, 3),
      new Bomb(2, 2, 2),
      new Bomb(3, 3, 1)
    ];

    // Act
    world.update_bombs();

    // Assert
    expect(world.explosions.length).toBe(2);
    expect(world.explosions[0].coords).toEqual([[1, 1], [2, 2], [3, 3]]);
    expect(world.explosions[1].coords).toEqual([[2, 2], [3, 3]]);
    expect(world.explosions[0].screen_coords).toEqual([[21, 21], [22, 22], [23, 23]]);
    expect(world.explosions[1].screen_coords).toEqual([[22, 22], [23, 23]]);
    expect(world.explosions[0].owner).toBeNull();
    expect(world.explosions[1].owner).toBeNull();
    expect(world.bombs[0].active).toBeFalsy();
    expect(world.bombs[1].active).toBeFalsy();
    expect(world.bombs[2].active).toBeFalsy();
  });
});