import arcade

class AnimationUtil:
    @staticmethod
    def load_textures_from_spritesheet(
        file_path: str,
        frame_width: int,
        frame_height: int,
        columns: int,
        directions: list[str]
    ) -> dict[str, list[arcade.Texture]]:
        """
        Loads textures from a spritesheet and organizes them by direction.

        Args:
            file_path (str): Path to the spritesheet file.
            frame_width (int): Width of a single animation frame.
            frame_height (int): Height of a single animation frame.
            columns (int): Number of frames (columns) in each row of the spritesheet.
            directions (list[str]): List of direction names, one for each row.

        Returns:
            A dictionary mapping directions to lists of textures.
        """
        textures_by_direction = {}
        sprite_sheet = arcade.SpriteSheet(file_path)

        for i, direction in enumerate(directions):
            textures_by_direction[direction] = []
            for col in range(columns):
                # Calculate the rectangle for each frame
                # Note: arcade.SpriteSheet.get_texture expects (x, y, width, height)
                # where (x, y) is the bottom-left corner.
                # Spritesheets are often indexed from top-left, so we might need to flip the y-coordinate.
                # Assuming the spritesheet rows match the order in `directions` from top to bottom.
                # The y-coordinate needs to be calculated from the top of the image.

                y = sprite_sheet.image.height - (i + 0.5) * frame_height
                x = (col + 0.5) * frame_width
                
                rect = arcade.XYWH(x=x, y=y, width=frame_width, height=frame_height)
                texture = sprite_sheet.get_texture(rect)
                textures_by_direction[direction].append(texture)
                
        return textures_by_direction