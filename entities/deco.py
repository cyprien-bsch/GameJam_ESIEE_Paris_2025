import arcade

class Decoration(arcade.Sprite):
    def __init__(self, image_path: str, scale: float = 1.0, center_x: float = 0, center_y: float = 0):
        super().__init__(image_path, scale)
        self.center_x = center_x
        self.center_y = center_y

    def on_draw(self):
        self.draw()