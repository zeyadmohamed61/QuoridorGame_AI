from ai.aiPlayer import AIPlayer, AIMove
from game.pathFinding import find_shortest_path, has_valid_path
from util.constants import BOARD_SIZE

# Hard AI using Minimax with Alpha-Beta Pruning
class HardAI(AIPlayer):
    
    def __init__(self, player_id, depth=3):
        self.player_id = player_id
        self.depth = depth
    
    def get_move(self, game_state):
        best_move = None
        best_score = float('-inf')
        alpha = float('-inf')
        beta = float('inf')
        
        possible_moves = self._get_all_possible_moves(game_state)
        
        for move in possible_moves:
            self._apply_move(game_state, move)
            score = self._minimax(game_state, self.depth - 1, alpha, beta, False)
            self._undo_move(game_state, move)
            
            if score > best_score:
                best_score = score
                best_move = move
            
            alpha = max(alpha, score)
        
        return best_move
    
    def _minimax(self, game_state, depth, alpha, beta, is_maximizing):
        if depth == 0 or game_state.winner is not None:
            return self._evaluate(game_state)
        
        possible_moves = self._get_all_possible_moves(game_state)
        
        if not possible_moves:
            return self._evaluate(game_state)
        
        if is_maximizing:
            max_eval = float('-inf')
            for move in possible_moves:
                self._apply_move(game_state, move)
                eval_score = self._minimax(game_state, depth - 1, alpha, beta, False)
                self._undo_move(game_state, move)
                
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in possible_moves:
                self._apply_move(game_state, move)
                eval_score = self._minimax(game_state, depth - 1, alpha, beta, True)
                self._undo_move(game_state, move)
                
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                
                if beta <= alpha:
                    break
            return min_eval
    
    def _evaluate(self, game_state):
        player = game_state.players[self.player_id]
        opponent = game_state.players[1 - self.player_id]
        
        if game_state.winner is not None:
            return 10000 if game_state.winner == self.player_id else -10000
        
        my_path = find_shortest_path(game_state.board, player.x, player.y, player.goals)
        opp_path = find_shortest_path(game_state.board, opponent.x, opponent.y, opponent.goals)
        
        # Primary factor: difference in shortest paths (opponent longer = better for us)
        path_diff = (opp_path - my_path) * 10
        # Secondary factor: wall count advantage (having more walls = more options)
        wall_advantage = (player.walls_remaining - opponent.walls_remaining) * 1
        
        return path_diff + wall_advantage
    
    def _get_all_possible_moves(self, game_state):
        moves = []
        player = game_state.get_current_player()
        
        # Add pawn moves
        valid_moves = game_state.get_valid_moves(player)
        for pos in valid_moves:
            moves.append(AIMove(pos.x, pos.y))
        
        # Add strategic wall placements (limited to reduce search space)
        if player.walls_remaining > 0:
            wall_moves = self._get_candidate_walls(game_state)
            moves.extend(wall_moves)  # Already ranked and capped inside
        
        return moves
    
    def _get_candidate_walls(self, game_state):
        walls = []
        opponent = game_state.players[1 - self.player_id]
        opp_x, opp_y = opponent.x, opponent.y

        current_opp_path = find_shortest_path(
            game_state.board, opponent.x, opponent.y, opponent.goals
        )
        
        # Only check walls near opponent
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                x = opp_x + dx
                y = opp_y + dy
                
                if not (0 <= x < BOARD_SIZE - 1 and 0 <= y < BOARD_SIZE - 1):
                    continue
                
                for is_horizontal in [True, False]:
                    if game_state.board.can_place_wall(x, y, is_horizontal):
                        game_state.board.place_wall(x, y, is_horizontal)
                        
                        valid = True
                        for p in game_state.players:
                            if not has_valid_path(game_state.board, p.x, p.y, p.goals):
                                valid = False
                                break
                        
                        if valid:
                            new_opp_path = find_shortest_path(
                                game_state.board, opponent.x, opponent.y, opponent.goals
                            )
                            path_increase = new_opp_path - current_opp_path
                            walls.append((path_increase, AIMove(x, y, is_horizontal)))
                        
                        game_state.board.remove_wall(x, y, is_horizontal)
        
        # Sort by how much they hurt the opponent (descending) and return top 10
        walls.sort(key=lambda w: w[0], reverse=True)
        return [w[1] for w in walls[:10]]
    
    def _apply_move(self, game_state, move):
        if move.type.value == "pawn":
            player = game_state.get_current_player()
            move.old_x = player.x
            move.old_y = player.y
            player.move(move.x, move.y)
            # Check and record winner without ending the search
            move.prev_winner = game_state.winner
            if player.has_won():
                game_state.winner = player.player_id
        else:  # wall
            game_state.board.place_wall(move.x, move.y, move.is_horizontal)
            game_state.get_current_player().place_wall()
            move.prev_winner = game_state.winner
        
        # Switch turn directly to avoid clearing redo_stack (which corrupts state)
        game_state.current_player_idx = 1 - game_state.current_player_idx
    
    def _undo_move(self, game_state, move):
        # Switch turn back directly
        game_state.current_player_idx = 1 - game_state.current_player_idx
        
        if move.type.value == "pawn":
            player = game_state.get_current_player()
            player.move(move.old_x, move.old_y)
        else:  # wall
            game_state.board.remove_wall(move.x, move.y, move.is_horizontal)
            game_state.get_current_player().undo_place_wall()
        
        # Restore winner state
        game_state.winner = move.prev_winner
