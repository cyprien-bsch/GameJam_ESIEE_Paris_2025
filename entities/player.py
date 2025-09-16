import arcade

class Player(arcade.Sprite):
    def __init__(self, x: float, y: float, solid_decorations: arcade.SpriteList = None):
        super().__init__(":resources:images/animated_characters/female_person/femalePerson_idle.png", 1.0)
        self.center_x = x
        self.center_y = y
        self.change_x = 0
        self.change_y = 0
        self.speed = 200
        self.solid_decorations = solid_decorations if solid_decorations is not None else arcade.SpriteList()

    def update(self, delta_time = None):
        move_x = self.change_x * (delta_time if delta_time else 1/60)

        already_collided = arcade.check_for_collision_with_list(self, self.solid_decorations)

        self.center_x += move_x
        if arcade.check_for_collision_with_list(self, self.solid_decorations) and not already_collided:
            self.center_x -= move_x

        move_y = self.change_y * (delta_time if delta_time else 1/60)

        self.center_y += move_y
        if arcade.check_for_collision_with_list(self, self.solid_decorations) and not already_collided:
            self.center_y -= move_y

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.UP:
            if self.change_y == 0:
                self.change_y = self.speed
            else:
                self.change_y = 0
        elif symbol == arcade.key.DOWN:
            if self.change_y == 0:
                self.change_y = -self.speed
            else:
                self.change_y = 0
        elif symbol == arcade.key.LEFT:
            if self.change_x == 0:
                self.change_x = -self.speed
            else:
                self.change_x = 0
        elif symbol == arcade.key.RIGHT:
            if self.change_x == 0:
                self.change_x = self.speed
            else:
                self.change_x = 0

    def on_key_release(self, symbol, modifiers):
        if symbol == arcade.key.UP:
            if self.change_y == self.speed:
                self.change_y = 0
            else:
                self.change_y = -self.speed
        elif symbol == arcade.key.DOWN:
            if self.change_y == -self.speed:
                self.change_y = 0
            else:
                self.change_y = self.speed
        elif symbol == arcade.key.LEFT:
            if self.change_x == -self.speed:
                self.change_x = 0
            else:
                self.change_x = self.speed
        elif symbol == arcade.key.RIGHT:
            if self.change_x == self.speed:
                self.change_x = 0
            else:
                self.change_x = -self.speed
