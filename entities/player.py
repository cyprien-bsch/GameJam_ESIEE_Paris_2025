import arcade

class Player(arcade.Sprite):
    def __init__(self, x: float, y: float):
        super().__init__(":resources:images/animated_characters/female_person/femalePerson_idle.png", 1.0)
        self.center_x = x
        self.center_y = y
        self.change_x = 0
        self.change_y = 0
        self.speed = 200

    def update(self, delta_time = None):
        self.center_x += self.change_x * (delta_time if delta_time else 1/60)
        self.center_y += self.change_y * (delta_time if delta_time else 1/60)

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.UP:
            self.change_y = self.speed
        elif symbol == arcade.key.DOWN:
            self.change_y = -self.speed
        elif symbol == arcade.key.LEFT:
            self.change_x = -self.speed
        elif symbol == arcade.key.RIGHT:
            self.change_x = self.speed

    def on_key_release(self, symbol, modifiers):
        if symbol in (arcade.key.UP, arcade.key.DOWN):
            self.change_y = 0
        elif symbol in (arcade.key.LEFT, arcade.key.RIGHT):
            self.change_x = 0
