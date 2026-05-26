import random
from ai.aiPlayer import AIPlayer, AIMove
from game.pathFinding import find_shortest_path, has_valid_path
from util.constants import BOARD_SIZE


class MediumAI(AIPlayer):
    
    def __init__(self, player_id):
        self.player_id = player_id
    
    def get_move(self, game_state):
        player = game_state.players[self.player_id]
        opponent = game_state.players[1 - self.player_id]
        
        # Calculate path lengths
        my_path = find_shortest_path(game_state.board, player.x, player.y, player.goals)
        opp_path = find_shortest_path(game_state.board, opponent.x, opponent.y, opponent.goals)
        
        # If opponent is closer and we have walls, try to place a wall
        if player.walls_remaining > 0 and opp_path < my_path and random.random() < 0.5:
            wall_move = self._get_strategic_wall(game_state)
            if wall_move:
                return wall_move
        
        # Otherwise, move toward goal
        return self._get_best_move(game_state)
    
    def _get_best_move(self, game_state):
        player = game_state.players[self.player_id]
        valid_moves = game_state.get_valid_moves(player)
        
        if not valid_moves:
            return None
        
        # Choose move that minimizes distance to goal
        best_move = None
        best_distance = float('inf')
        
        for move in valid_moves:
            distance = abs(move.y - player.goals)
            if distance < best_distance:
                best_distance = distance
                best_move = move
        
        return AIMove(best_move.x, best_move.y)
    
    def _get_strategic_wall(self, game_state):
        player = game_state.players[self.player_id]
        opponent = game_state.players[1 - self.player_id]
        
        if player.walls_remaining <= 0:
            return None
        
        current_opp_length = find_shortest_path(
            game_state.board, opponent.x, opponent.y, opponent.goals
        )
        
        best_wall = None
        best_increase = 0
        
        # Try walls near opponent
        opp_x, opp_y = opponent.x, opponent.y
        
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                x = opp_x + dx
                y = opp_y + dy
                
                if not (0 <= x < BOARD_SIZE - 1 and 0 <= y < BOARD_SIZE - 1):
                    continue
                
                for is_horizontal in [True, False]:
                    if not game_state.board.can_place_wall(x, y, is_horizontal):
                        continue
                    
                    # Temporarily place wall
                    game_state.board.place_wall(x, y, is_horizontal)
                    
                    # Check if paths are valid
                    valid = True
                    for p in game_state.players:
                        if not has_valid_path(game_state.board, p.x, p.y, p.goals):
                            valid = False
                            break
                    
                    if valid:
                        new_opp_length = find_shortest_path(
                            game_state.board, opponent.x, opponent.y, opponent.goals
                        )
                        increase = new_opp_length - current_opp_length
                        
                        if increase > best_increase:
                            best_increase = increase
                            best_wall = AIMove(x, y, is_horizontal)
                    
                    # Remove temporary wall
                    game_state.board.remove_wall(x, y, is_horizontal)
        
        return best_wall if best_increase > 0 else None
