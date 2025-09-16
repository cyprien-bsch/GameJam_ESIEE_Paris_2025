import arcade

class AnimationUtil:
    @staticmethod
    def load_textures_from_spritesheet(
        file_path: str,
        frame_width: int,
        frame_height: int,
        columns: int,
        types: list[str]
    ) -> dict[str, list[arcade.Texture]]:
        """
        Loads textures from a spritesheet and organizes them by direction.

        Args:
            file_path (str): Path to the spritesheet file.
            frame_width (int): Width of a single animation frame.
            frame_height (int): Height of a single animation frame.
            columns (int): Number of frames (columns) in each row of the spritesheet.
            types (list[str]): List of direction names, one for each row.

        Returns:
            A dictionary mapping types to lists of textures.
        """
        textures_by_type = {}
        sprite_sheet = arcade.SpriteSheet(file_path)

        for i, typ in enumerate(types):
            textures_by_type[typ] = []
            for col in range(columns):
                # Calculate the rectangle for each frame
                # Note: arcade.SpriteSheet.get_texture expects (x, y, width, height)
                # where (x, y) is the bottom-left corner.
                # The y-coordinate needs to be calculated from the top of the image.

                y =  (i + 0.5) * frame_height
                x = (col + 0.5) * frame_width
                
                rect = arcade.XYWH(x=x, y=y, width=frame_width, height=frame_height)
                texture = sprite_sheet.get_texture(rect)
                textures_by_type[typ].append(texture)

        return textures_by_type