import arcade
from utils.animation import AnimationUtil

class Item:
    value = 0
    texture = None

class Coin(Item):
    value = 1
    texture = "assets/images/MonedaD_solo.png"
    center_x = 0
    center_y = 0
    height = 0
    width = 0

    def draw(self):
        arcade.draw_texture_rect(
            self.texture,
            rect=arcade.LBWH(
                self.center_x - self.width / 2,
                self.center_y - self.height / 2,
                self.width,
                self.height
            ),
            angle=self.angle,
            alpha=255
        )
