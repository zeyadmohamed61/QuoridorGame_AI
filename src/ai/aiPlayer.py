from abc import ABC, abstractmethod
from enum import Enum


class MoveType(Enum):
    PAWN = "pawn"
    WALL = "wall"


class AIMove:
    
    def __init__(self, x, y, is_horizontal=None):
        if is_horizontal is None:
            # Pawn move
            self.type = MoveType.PAWN
            self.x = x
            self.y = y
            self.is_horizontal = False
        else:
            # Wall placement
            self.type = MoveType.WALL
            self.x = x
            self.y = y
            self.is_horizontal = is_horizontal


class AIPlayer(ABC):
    #Abstract base class for AI players.
    @abstractmethod
    def get_move(self, game_state):
        pass
