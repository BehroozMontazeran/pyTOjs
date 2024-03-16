const assert = require('assert');
const GenericWorld = require('./environment_all');

class TestGenericWorld {
  constructor() {
    this.world = new GenericWorld();
  }

  test_tile_is_free() {
    /*
    Test case to check if a tile is free.
    */
    // Arrange
    this.world.arena = {
      "0,0": 0,
      "1,1": 1,
      "2,2": 0
    };
    this.world.bombs = [];
    this.world.active_agents = [];

    // Act
    const result_1 = this.world.tile_is_free(0, 0);  // Free tile
    const result_2 = this.world.tile_is_free(1, 1);  // Occupied tile
    const result_3 = this.world.tile_is_free(2, 2);  // Free tile

    // Assert
    assert.strictEqual(result_1, true);
    assert.strictEqual(result_2, false);
    assert.strictEqual(result_3, true);
  }
}

const testObject = new TestGenericWorld();
testObject.test_tile_is_free();