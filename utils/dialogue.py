import arcade

class Dialogue:
    def __init__(self):
        self.current_dialogue = []
        self.dialogue_index = 0
        self.char_index = 0        # Pour l'effet machine à écrire
        self.char_timer = 0.0      # Temps écoulé depuis le dernier caractère
        self.char_speed = 0.05     # Temps entre chaque lettre (en secondes)
        self.dialogues = {}        # Dictionnaire pour stocker les dialogues par scène

    def set_dialogue(self, dialogue_lines):
        """Définit le dialogue à afficher (liste de lignes)."""
        self.current_dialogue = dialogue_lines if dialogue_lines else []
        self.dialogue_index = 0
        self.char_index = 0
        self.char_timer = 0.0

    def start(self, key_or_lines):
        """Démarre un dialogue à partir d'une liste ou d'une clé (pour compatibilité)."""
        if isinstance(key_or_lines, list):
            self.set_dialogue(key_or_lines)
        elif isinstance(key_or_lines, str) and key_or_lines in self.dialogues:
            self.set_dialogue(self.dialogues[key_or_lines])
        else:
            self.set_dialogue([])

    def advance(self):
        """Passe à la prochaine ligne de dialogue ou termine le dialogue."""
        if self.current_dialogue:
            if self.char_index < len(self.current_dialogue[self.dialogue_index]):
                self.char_index = len(self.current_dialogue[self.dialogue_index])
            else:
                self.dialogue_index += 1
                self.char_index = 0
                self.char_timer = 0.0
                if self.dialogue_index >= len(self.current_dialogue):
                    self.current_dialogue = []
                    self.dialogue_index = 0

    def is_active(self):
        """Retourne True si un dialogue est actif."""
        return bool(self.current_dialogue)

    def update(self, delta_time: float):
        """Met à jour l’affichage des lettres."""
        if not self.is_active():
            return
        self.char_timer += delta_time
        if self.char_timer >= self.char_speed:
            self.char_index += 1
            self.char_timer = 0.0
            if self.char_index > len(self.current_dialogue[self.dialogue_index]):
                self.char_index = len(self.current_dialogue[self.dialogue_index])

    def _wrap_text(self, text, max_width, font_size):
        """Retourne le texte découpé en lignes pour ne pas dépasser la largeur max."""
        import arcade
        words = text.split(' ')
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            # Use arcade.Text to measure text width properly
            text_obj = arcade.Text(test_line, 0, 0, arcade.color.BLACK, font_size)
            width = text_obj.content_width
            if width > max_width and current_line:
                lines.append(current_line)
                current_line = word
            else:
                current_line = test_line
        if current_line:
            lines.append(current_line)
        return lines

    def draw(self, window_width, window_height):
        """Dessine le dialogue à l'écran avec retour à la ligne automatique."""
        if not self.is_active():
            return
        
        # Configuration du style Pokemon/jeux classiques
        padding = 20
        box_height = 120
        box_width = window_width - 2 * padding
        
        # Position en haut de l'écran (style Pokemon)
        left = padding
        right = window_width - padding
        top = window_height - padding
        bottom = top - box_height
        
        # Fond blanc avec bordure noire épaisse (style rétro)
        arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, arcade.color.WHITE)
        
        # Bordure extérieure noire épaisse
        arcade.draw_lrbt_rectangle_outline(left, right, bottom, top, arcade.color.BLACK, 4)
        
        # Bordure intérieure pour l'effet 3D
        inner_padding = 6
        arcade.draw_lrbt_rectangle_outline(
            left + inner_padding, 
            right - inner_padding, 
            bottom + inner_padding, 
            top - inner_padding, 
            arcade.color.DARK_GRAY, 
            2
        )
        
        # Zone de texte
        text_x = left + 15
        text_y = top - 25
        text_to_display = self.current_dialogue[self.dialogue_index][:self.char_index]
        wrapped_lines = self._wrap_text(text_to_display, box_width - 30, 16)
        
        # Affichage du texte en noir sur fond blanc
        for i, line in enumerate(wrapped_lines):
            arcade.draw_text(
                line,
                text_x,
                text_y - i * 22,
                arcade.color.BLACK,
                16,
                width=box_width - 30,
                align="left"
            )
        
        # Indicateur de continuation (petit triangle en bas à droite)
        if self.char_index >= len(self.current_dialogue[self.dialogue_index]):
            if self.dialogue_index < len(self.current_dialogue) - 1:
                # Triangle pour "continuer"
                triangle_x = right - 25
                triangle_y = bottom + 15
                arcade.draw_triangle_filled(
                    triangle_x, triangle_y,
                    triangle_x + 8, triangle_y + 5,
                    triangle_x, triangle_y + 10,
                    arcade.color.BLACK
                )
