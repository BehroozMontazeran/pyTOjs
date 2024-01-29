const { GUI } = require('./environment_all.js');

class GUITest {
  constructor() {
    this.gui = new GUI();  // Instantiate the GUI object
  }

  setUp() {
    this.gui.world.args.make_video = true;
    this.gui.world.round_id = 1;
    this.gui.world.logger = new MockLogger();  // Create a mock logger object
  }

  test_make_video() {
    // Call the make_video method
    this.gui.make_video();

    // Assert that the videos are created
    const expected_files = [
      `${this.gui.screenshot_dir}/1_video.mp4`,
      `${this.gui.screenshot_dir}/1_video.webm`
    ];
    for (const file of expected_files) {
      console.assert(fs.existsSync(file), `Video file ${file} was not created.`);
    }

    // Assert that the log messages are correct
    console.assert(this.gui.world.logger.debug_calls[0] === "Turning screenshots into video");
    console.assert(this.gui.world.logger.info_calls[0] === "Done writing videos.");

    // Assert that the screenshot files are deleted
    const screenshot_files = fs.readdirSync(this.gui.screenshot_dir);
    for (const file of screenshot_files) {
      if (file.startsWith('1_') && file.endsWith('.png')) {
        console.assert(!fs.existsSync(`${this.gui.screenshot_dir}/${file}`), `Screenshot file ${file} was not deleted.`);
      }
    }
  }
}

class MockLogger {
  constructor() {
    this.debug_calls = [];
    this.info_calls = [];
  }

  debug(msg) {
    this.debug_calls.push(msg);
  }

  info(msg) {
    this.info_calls.push(msg);
  }
}

const guiTest = new GUITest();
guiTest.setUp();
guiTest.test_make_video();