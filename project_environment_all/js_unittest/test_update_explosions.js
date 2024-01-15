const GenericWorld = require('./environment_all').GenericWorld;

class GenericWorldTestCase {
    test_update_explosions() {
        const world = new GenericWorld();
        const explosion1 = new Explosion();
        explosion1.timer = 5;
        explosion1.stage = 1;
        world.explosions.push(explosion1);
        const explosion2 = new Explosion();
        explosion2.timer = 0;
        explosion2.stage = null;
        world.explosions.push(explosion2);
        const explosion3 = new Explosion();
        explosion3.timer = 2;
        explosion3.stage = 2;
        world.explosions.push(explosion3);

        world.update_explosions();

        expect(world.explosions.length).toBe(2);
        expect(world.explosions[0].timer).toBe(4);
        expect(world.explosions[0].stage).toBe(1);
        expect(world.explosions[1].timer).toBe(1);
        expect(world.explosions[1].stage).toBe(2);
    }
}

const testCase = new GenericWorldTestCase();
testCase.test_update_explosions();