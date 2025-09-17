from enum import Enum

class GamePhase(Enum):
    MENU = 1
    REST = 2
    WAR_START = 3
    IN_WAR = 4
    WAR_END = 5
    GAME_OVER = 0

def phase_length(phase: GamePhase) -> int:
    if phase == GamePhase.REST:
        return 1
    if phase == GamePhase.WAR_START:
        return 5
    if phase == GamePhase.IN_WAR:
        return 30
    return 0