const GUI = require('./environment_all').GUI;

test('render_text should render text with expected parameters', () => {
  // Arrange
  const gui = new GUI();
  const expected_text = "Hello, World!";
  const expected_x = 100;
  const expected_y = 200;
  const expected_color = [255, 255, 255];
  const expected_halign = 'left';
  const expected_valign = 'top';
  const expected_size = 'medium';
  const expected_aa = false;

  // Act
  gui.render_text(
    expected_text, 
    expected_x, 
    expected_y, 
    expected_color, 
    expected_halign, 
    expected_valign, 
    expected_size, 
    expected_aa
  );

  // Assert
  // Add your assertions here to verify the expected behavior of the render_text method
});