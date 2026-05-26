from util.constants import PLAYER_STARTS, PLAYER_GOALS, WALLS_PER_PLAYER, COLOR_PLAYER1, COLOR_PLAYER2

class Player:
    def __init__(self, player_id):
        self.player_id = player_id
        self.x, self.y = PLAYER_STARTS[player_id]
        self.goals = PLAYER_GOALS[player_id]
        self.walls_remaining = WALLS_PER_PLAYER
        self.color = COLOR_PLAYER1 if player_id == 0 else COLOR_PLAYER2
        self.is_ai = False

    def move(self, new_x, new_y):
        self.x = new_x
        self.y = new_y

    def place_wall(self):
        if self.walls_remaining > 0:
            self.walls_remaining -= 1
    
    def has_won(self):
        return self.y == self.goals
    
    # for undo functionality
    def undo_place_wall(self):
        self.walls_remaining += 1

    def __str__(self):
        return f"Player {self.player_id + 1} at ({self.x}, {self.y}) with {self.walls_remaining} walls remaining"