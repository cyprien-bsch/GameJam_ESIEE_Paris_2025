import arcade
from enum import Enum
from core.game_phases import GamePhase
from utils.dialogue import Dialogue

class GameScene(Enum):
    NONE = 0
    TUTORIAL_LESSON = 1      # Scène 1: La première leçon
    ENEMY_ARRIVAL = 2        # Scène 2: L'arrivée des ennemis
    TUTORIAL_CLEANING = 3    # Scène 3: Le grand nettoyage
    NIGHT_SURVIVAL = 4       # Scène 4: L'épreuve de la nuit
    LORD_INCIDENT = 5        # Scène 5: L'incident du seigneur
    MONSTER_CAMP = 6         # Scène 6: Le campement des monstres
    FINAL_BATTLE = 7         # Scène 7: Le chaos final
    CONCLUSION = 8           # Scène 8: La conclusion

class SceneManager:
    def __init__(self, window, dialogue_manager: Dialogue):
        self.window = window
        self.dialogue_manager = dialogue_manager
        self.current_scene = GameScene.NONE
        self.scene_progress = 0  # Progression à l'intérieur d'une scène (0-100%)
        self.scene_completed = {scene: False for scene in GameScene}
        self.scene_triggers = {}  # Points de déclenchement pour chaque scène
        self.knight_positions = []  # Historique des positions du chevalier
        self.scene_objectives = self._init_objectives()
        self.collected_items = set()  # Items collectés par le joueur
        self._previous_scene = GameScene.NONE  # Pour suivre les transitions
        self._init_dialogues()
        
    def _init_dialogues(self):
        """Initialise les dialogues pour chaque scène directement dans le dialogue_manager."""
        # Initialiser les dialogues pour chaque scène
        scene_dialogues = {
            GameScene.TUTORIAL_LESSON: [
                "Chevalier: Enfin! Tu arrives trop tard, le dragon est déjà vaincu. Ramasse tout ce désordre!",
                "Écuyer: Mon maître... j'ai essayé d'arriver à temps, mais c'était déjà terminé..."
            ],
            GameScene.ENEMY_ARRIVAL: [
                "Ennemi 1: Nous savons qui a tué notre dragon...",
                "Ennemi 2: Oui, c'est ce chevalier arrogant!",
                "Chevalier: Hmph, vous arrivez trop tard, jeunes imprudents!"
            ],
            GameScene.TUTORIAL_CLEANING: [
                "Chevalier: Regarde-moi ce désordre déshonorant! Nettoie tout ça!",
                "Écuyer: Toujours la même chose... je me demande si j'arriverai un jour à tout remettre en ordre."
            ],
            GameScene.NIGHT_SURVIVAL: [
                "Chevalier: Je suis épuisé par ma victoire. Je vais me reposer ici.",
                "Écuyer: Et moi je vais devoir monter la garde, comme d'habitude."
            ],
            GameScene.LORD_INCIDENT: [
                "Chevalier: Ce seigneur m'a provoqué! Je l'ai vaincu en duel!",
                "Écuyer: Il vous avait juste demandé l'heure...",
                "Écuyer: Et maintenant nous avons une nouvelle guerre sur les bras."
            ],
            GameScene.MONSTER_CAMP: [
                "Chevalier: Ces animaux ont l'air inoffensifs. Installons notre camp ici.",
                "Écuyer: Ce sont des monstres, pas des animaux..."
            ],
            GameScene.FINAL_BATTLE: [
                "Chevalier: Cette bataille n'en finit jamais! Je vais m'occuper de tout ça moi-même!",
                "Écuyer: Non, attendez! Vous allez empirer les choses!"
            ],
            GameScene.CONCLUSION: [
                "Chevalier: Encore une victoire pour moi! Quelle bravoure!",
                "Écuyer: Un jour, ce sera moi le héros... mais pas aujourd'hui."
            ]
        }

        
        # Ajouter les dialogues directement au dialogue_manager
        for scene, dialogues in scene_dialogues.items():
            scene_key = f"scene_{scene.name.lower()}"
            self.dialogue_manager.dialogues[scene_key] = dialogues
    
    def _init_objectives(self):
        """Initialise les objectifs pour chaque scène."""
        return {
            GameScene.TUTORIAL_LESSON: "Ramassez les restes de l'ennemi vaincu pour récupérer de l'équipement.",
            GameScene.TUTORIAL_CLEANING: "Nettoyez la zone avec votre balai magique.",
            GameScene.NIGHT_SURVIVAL: "Survivez pendant que le chevalier dort. Attention aux créatures!",
            GameScene.LORD_INCIDENT: "Récupérez le sceau royal sur le corps du seigneur sans vous faire repérer.",
            GameScene.MONSTER_CAMP: "Préparez le campement tout en évitant les monstres.",
            GameScene.FINAL_BATTLE: "Survivez au chaos de la bataille finale et influencez son issue.",
            GameScene.CONCLUSION: "Écoutez le discours du chevalier et acceptez votre destin... pour l'instant."
        }
    
    def update(self, delta_time):
        """Met à jour l'état de la scène actuelle."""
        # Si nous sommes dans une phase de jeu active
        if self.window.phase != GamePhase.MENU and self.window.phase != GamePhase.GAME_OVER:
            # Vérifier si nous devons passer à une nouvelle scène
            self._check_scene_triggers()
            
            # Mettre à jour la progression de la scène actuelle
            self._update_scene_progress(delta_time)
    
    def _check_scene_triggers(self):
        """Vérifie si les conditions sont remplies pour déclencher une nouvelle scène."""
        knight = self.window.knight[0] if len(self.window.knight) > 0 else None
        
        if knight is None:
            return
        
        # Enregistrer la position du chevalier pour suivre son déplacement
        self.knight_positions.append((knight.center_x, knight.center_y))
        if len(self.knight_positions) > 100:  # Limiter la taille de l'historique
            self.knight_positions.pop(0)
        
        # Progression des scènes basée uniquement sur la progression de position
        # Les scènes ne changent que quand la progression atteint 100%
        
        if self.current_scene == GameScene.NONE:
            self._start_scene(GameScene.TUTORIAL_LESSON)
        elif self.scene_progress >= 100 and not self.scene_completed[self.current_scene]:
            # Marquer la scène actuelle comme terminée
            self.scene_completed[self.current_scene] = True
            
            # Passer à la scène suivante
            if self.current_scene == GameScene.TUTORIAL_LESSON:
                self._start_scene(GameScene.TUTORIAL_CLEANING)
            elif self.current_scene == GameScene.TUTORIAL_CLEANING:
                self._start_scene(GameScene.DRAGON_BATTLE)
            elif self.current_scene == GameScene.DRAGON_BATTLE:
                self._start_scene(GameScene.LORD_INCIDENT)
            elif self.current_scene == GameScene.LORD_INCIDENT:
                self._start_scene(GameScene.NIGHT_SURVIVAL)
            elif self.current_scene == GameScene.NIGHT_SURVIVAL:
                self._start_scene(GameScene.MONSTER_CAMP)
            elif self.current_scene == GameScene.MONSTER_CAMP:
                self._start_scene(GameScene.FINAL_BATTLE)
            elif self.current_scene == GameScene.FINAL_BATTLE:
                self._start_scene(GameScene.CONCLUSION)
    
    def _update_scene_progress(self, delta_time):
        """Met à jour la progression de la scène actuelle basée sur la position Y du chevalier."""
        if self.current_scene == GameScene.NONE:
            return
        
        # Obtenir la position du chevalier et les dimensions de la carte
        knight = self.window.knight[0] if len(self.window.knight) > 0 else None
        if not knight:
            return
            
        # Obtenir les dimensions de la carte
        map_height = getattr(self.window, 'total_map_height_px', 19200)  # 300 tiles * 64px par défaut
        
        # Calculer la progression basée sur la position Y du chevalier
        # Plus le chevalier monte (Y plus élevé), plus la progression augmente
        knight_y = knight.center_y
        
        # Debug: afficher les valeurs pour comprendre le problème
        # print(f"DEBUG: Knight Y: {knight_y}, Map height: {map_height}, Current scene: {self.current_scene}")
        
        # Diviser la carte en sections pour chaque scène
        # La carte fait 19200px de haut, on divise en 8 sections (une par scène)
        section_height = map_height / 8
        
        # Déterminer dans quelle section le chevalier se trouve
        if self.current_scene == GameScene.TUTORIAL_LESSON:
            # Section du bas (0-12.5% de la carte)
            section_start = 0
            section_end = section_height
        elif self.current_scene == GameScene.TUTORIAL_CLEANING:
            # Section 2 (12.5-25% de la carte)
            section_start = section_height
            section_end = section_height * 2
        elif self.current_scene == GameScene.DRAGON_BATTLE:
            # Section 3 (25-37.5% de la carte)
            section_start = section_height * 2
            section_end = section_height * 3
        elif self.current_scene == GameScene.LORD_INCIDENT:
            # Section 4 (37.5-50% de la carte)
            section_start = section_height * 3
            section_end = section_height * 4
        elif self.current_scene == GameScene.NIGHT_SURVIVAL:
            # Section 5 (50-62.5% de la carte)
            section_start = section_height * 4
            section_end = section_height * 5
        elif self.current_scene == GameScene.MONSTER_CAMP:
            # Section 6 (62.5-75% de la carte)
            section_start = section_height * 5
            section_end = section_height * 6
        elif self.current_scene == GameScene.FINAL_BATTLE:
            # Section 7 (75-87.5% de la carte)
            section_start = section_height * 6
            section_end = section_height * 7
        elif self.current_scene == GameScene.CONCLUSION:
            # Section du haut (87.5-100% de la carte)
            section_start = section_height * 7
            section_end = map_height
        else:
            return
        
        # Calculer le pourcentage de progression dans la section actuelle
        if knight_y <= section_start:
            self.scene_progress = 0
        elif knight_y >= section_end:
            self.scene_progress = 100
        else:
            # Progression linéaire dans la section
            progress_in_section = (knight_y - section_start) / (section_end - section_start)
            self.scene_progress = min(100, max(0, progress_in_section * 100))
        
        # Debug: afficher les calculs de progression
        # print(f"DEBUG: Section start: {section_start}, Section end: {section_end}, Progress: {self.scene_progress}%")
        
        # Marquer la scène comme terminée si la progression atteint 100%
        # Note: Ne pas marquer ici car c'est fait dans _check_scene_triggers
        # if self.scene_progress >= 100:
        #     self.scene_completed[self.current_scene] = True
    
    def _start_scene(self, scene: GameScene):
        """Démarre une nouvelle scène."""
        self.current_scene = scene
        self.scene_progress = 0  # Réinitialiser la progression pour la nouvelle scène
        
        # Marquer la scène précédente comme terminée si elle existe
        if hasattr(self, '_previous_scene') and self._previous_scene != GameScene.NONE:
            self.scene_completed[self._previous_scene] = True
        
        self._previous_scene = scene
        
        # Démarrer le dialogue associé à la scène
        scene_key = f"scene_{scene.name.lower()}"
        if scene_key in self.dialogue_manager.dialogues:
            self.dialogue_manager.start(scene_key)
        
        # print(f"DEBUG: Started scene {scene} with progress reset to 0%")
    
    def get_current_objective(self):
        """Retourne l'objectif actuel de la scène."""
        if self.current_scene in self.scene_objectives:
            return self.scene_objectives[self.current_scene]
        return ""
    
    def add_collected_item(self, item_name):
        """Ajoute un item à la liste des objets collectés."""
        self.collected_items.add(item_name)
    
    def draw_objective(self, window_width, window_height):
        """Affiche l'objectif actuel à l'écran."""
        if self.current_scene != GameScene.NONE:
            objective = self.get_current_objective()
            # Nouvelle position : en bas à droite
            margin = 20
            text = f"Objectif: {objective}"
            progress = f"Progression: {int(self.scene_progress)}%"
            # Calculer la largeur du texte pour l'aligner à droite
            text_obj = arcade.Text(text, 0, 0, arcade.color.WHITE, 14)
            progress_obj = arcade.Text(progress, 0, 0, arcade.color.WHITE, 14)
            text_width = text_obj.content_width
            progress_width = progress_obj.content_width
            x_obj = window_width - text_width - margin
            x_prog = window_width - progress_width - margin
            y_obj = margin + 40
            y_prog = margin + 20
            arcade.draw_text(text, x_obj, y_obj, arcade.color.WHITE, 14)
            arcade.draw_text(progress, x_prog, y_prog, arcade.color.WHITE, 14)