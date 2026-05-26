import random
from ai.aiPlayer import AIPlayer, AIMove
from game.pathFinding import has_valid_path
from util.constants import BOARD_SIZE


class EasyAI(AIPlayer):
    
    def __init__(self, player_id):
        self.player_id = player_id
    
    def get_move(self, game_state):
        player = game_state.players[self.player_id]

        # 30% chance to place a wall if available
        if player.walls_remaining > 0 and random.random() < 0.3:
            wall_move = self._try_random_wall(game_state)
            if wall_move:
                return wall_move
        
        # Move pawn
        valid_moves = game_state.get_valid_moves(player)
        if valid_moves:
            move = random.choice(valid_moves)
            return AIMove(move.x, move.y)
        
        # Fallback: try wall again
        wall_move = self._try_random_wall(game_state)
        if wall_move:
            return wall_move
        
        # Last resort: first valid move
        if valid_moves:
            move = valid_moves[0]
            return AIMove(move.x, move.y)
        
        return None
    
    def _try_random_wall(self, game_state):
        player = game_state.players[self.player_id]
        
        if player.walls_remaining <= 0:
            return None
        
        # Try 20 random wall placements
        for _ in range(20):
            x = random.randint(0, BOARD_SIZE - 2)
            y = random.randint(0, BOARD_SIZE - 2)
            is_horizontal = random.choice([True, False])
            
            if game_state.board.can_place_wall(x, y, is_horizontal):
                # Temporarily place wall
                game_state.board.place_wall(x, y, is_horizontal)
                
                # Check if both players have valid paths
                valid = True
                for p in game_state.players:
                    if not has_valid_path(game_state.board, p.x, p.y, p.goals):
                        valid = False
                        break
                
                # Remove temporary wall
                game_state.board.remove_wall(x, y, is_horizontal)
                
                if valid:
                    return AIMove(x, y, is_horizontal)
        
        return None
