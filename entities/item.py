import arcade

class Item(arcade.Sprite):
    def __init__(self, image_path: str, x: float, y: float):
        super().__init__(image_path, 1.0)
        self.center_x = x
        self.center_y = y
