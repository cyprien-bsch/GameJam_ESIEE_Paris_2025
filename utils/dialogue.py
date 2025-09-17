import arcade

class Dialogue:
    def __init__(self):
        self.dialogues = {
            "knight_intro": [
                "Chevalier: cc sava? ah nan j'men fou",
            ]
        }
        self.current_dialogue = None
        self.dialogue_index = 0
        self.char_index = 0        # Pour l'effet machine à écrire
        self.char_timer = 0.0      # Temps écoulé depuis le dernier caractère
        self.char_speed = 0.05     # Temps entre chaque lettre (en secondes)

    def start(self, key: str):
        """Démarre un dialogue à partir d'une clé."""
        self.current_dialogue = self.dialogues.get(key, [])
        self.dialogue_index = 0
        self.char_index = 0
        self.char_timer = 0.0

    def advance(self):
        """Passe à la prochaine ligne de dialogue ou termine le dialogue."""
        if self.current_dialogue:
            if self.char_index < len(self.current_dialogue[self.dialogue_index]):
                # Si la ligne n’est pas encore terminée, afficher tout d’un coup
                self.char_index = len(self.current_dialogue[self.dialogue_index])
            else:
                # Sinon passer à la ligne suivante
                self.dialogue_index += 1
                self.char_index = 0
                self.char_timer = 0.0
                if self.dialogue_index >= len(self.current_dialogue):
                    self.current_dialogue = None
                    self.dialogue_index = 0

    def is_active(self):
        """Retourne True si un dialogue est actif."""
        return self.current_dialogue is not None

    def update(self, delta_time: float):
        """Met à jour l’affichage des lettres."""
        if not self.is_active():
            return

        self.char_timer += delta_time
        if self.char_timer >= self.char_speed:
            self.char_index += 1
            self.char_timer = 0.0
            # Ne pas dépasser la longueur de la ligne
            if self.char_index > len(self.current_dialogue[self.dialogue_index]):
                self.char_index = len(self.current_dialogue[self.dialogue_index])

    def draw(self, window_width, window_height):
        """Dessine le dialogue à l'écran."""
        if not self.is_active():
            return

        padding = 20
        box_height = 120
        box_width = window_width - 2 * padding

        # Coordonnées du rectangle (left, right, bottom, top)
        left = padding
        right = window_width - padding
        top = window_height - padding
        bottom = top - box_height  # bottom < top

        # Fond blanc cassé
        arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, (245, 245, 220))
        # Bord noir
        arcade.draw_lrbt_rectangle_outline(left, right, bottom, top, arcade.color.BLACK, 3)

        # Texte en noir (affiche seulement les caractères déjà “tapés”)
        text_x = left + 10
        text_y = top - 30
        text_to_display = self.current_dialogue[self.dialogue_index][:self.char_index]
        arcade.draw_text(
            text_to_display,
            text_x,
            text_y,
            arcade.color.BLACK,
            16,
            width=box_width - 20,
            align="left"
        )
