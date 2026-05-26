import json
import os
from enum import Enum

from game.board import Board
from game.player import Player
from game.pathFinding import Position, get_neighbors, has_valid_path
from util.constants import SAVE_DIR

class MoveType(Enum):
    PAWN = "pawn"
    WALL = "wall"

class Move:
    def __init__(self, move_type, player_id, **kwargs):
        self.type = move_type
        self.player_id = player_id
        
        if move_type == MoveType.PAWN:
            self.old_x = kwargs.get('old_x')
            self.old_y = kwargs.get('old_y')
            self.new_x = kwargs.get('new_x')
            self.new_y = kwargs.get('new_y')
            self.wall_x = None
            self.wall_y = None
            self.is_horizontal = None
        else:  # WALL
            self.wall_x = kwargs.get('wall_x')
            self.wall_y = kwargs.get('wall_y')
            self.is_horizontal = kwargs.get('is_horizontal')
            self.old_x = None
            self.old_y = None
            self.new_x = None
            self.new_y = None

class GameState:
    def __init__(self, mode="human_vs_human", ai_difficulty=None):
        self.board = Board()
        self.players = [Player(0), Player(1)]
        self.current_player_idx = 0
        self.mode = mode
        self.ai_difficulty = ai_difficulty
        self.winner = None
        self.message = "Player 1's turn"
        
        # Undo/Redo stacks
        self.move_history = []
        self.redo_stack = []
        
        # Set AI flag
        if mode == "human_vs_ai":
            self.players[1].is_ai = True
    
    def get_current_player(self):
        return self.players[self.current_player_idx]
    
    def get_opponent(self):
        return self.players[1 - self.current_player_idx]
    
    def switch_turn(self):
        self.current_player_idx = 1 - self.current_player_idx
        self.redo_stack.clear()  

    def get_valid_moves(self, player=None):
        if player is None:
            player = self.get_current_player()
        
        valid_moves = []
        opponent = self.players[1 - player.player_id]
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for dx, dy in directions:
            new_x = player.x + dx
            new_y = player.y + dy

            if not self.board.is_valid_position(new_x, new_y):
                continue

            if self.board.is_path_blocked(player.x, player.y, new_x, new_y):
                continue

            # Handle the unique moves
            if (new_x, new_y) == (opponent.x, opponent.y):
                jump_x = opponent.x + dx
                jump_y = opponent.y + dy

                if self.board.is_valid_position(jump_x, jump_y) and not self.board.is_path_blocked(opponent.x, opponent.y, jump_x, jump_y):
                    valid_moves.append(Position(jump_x, jump_y))
                else:
                    for side_dx, side_dy in [(-dy, dx), (dy, -dx)]:
                        side_x = opponent.x + side_dx
                        side_y = opponent.y + side_dy
                        if self.board.is_valid_position(side_x, side_y) and not self.board.is_path_blocked(opponent.x, opponent.y, side_x, side_y):
                            valid_moves.append(Position(side_x, side_y))
            else:
                valid_moves.append(Position(new_x, new_y))
        return valid_moves
    
    def move_pawn(self, new_x, new_y):
        player = self.get_current_player()
        valid_moves = self.get_valid_moves(player)

        target = Position(new_x, new_y)
        if target not in valid_moves:
            self.message = "Invalid move!"
            return False   
        
        # Record move for undo
        move = Move(MoveType.PAWN, player.player_id,
                   old_x=player.x, old_y=player.y,
                   new_x=new_x, new_y=new_y)
        self.move_history.append(move)

        player.move(new_x, new_y)

        # Check win condition
        if player.has_won():
            self.winner = player.player_id
            self.message = f"Player {player.player_id + 1} wins!"
            return True
        
        # Switch turn
        self.switch_turn()
        next_player = self.get_current_player()
        self.message = f"Player {next_player.player_id + 1}'s turn"
        
        return True

    def place_wall(self, wall_x, wall_y, is_horizontal):
        player = self.get_current_player()
        
        if player.walls_remaining <= 0:
            self.message = "No walls remaining!"
            return False
        
        if not self.board.can_place_wall(wall_x, wall_y, is_horizontal):
            self.message = "Invalid wall placement!"
            return False
        
        # Temporarily place the wall
        self.board.place_wall(wall_x, wall_y, is_horizontal)
        
        # Check for valid paths for both players
        valid = True
        for p in self.players:
            if not has_valid_path(self.board, p.x, p.y, p.goals):
                valid = False
                break
        
        if not valid:
            # Remove the wall since it blocks paths
            self.board.remove_wall(wall_x, wall_y, is_horizontal)
            self.message = "Wall placement blocks path!"
            return False
        
        player.place_wall()
        
        # Record move for undo
        move = Move(MoveType.WALL, player.player_id,
                   wall_x=wall_x, wall_y=wall_y,
                   is_horizontal=is_horizontal)
        self.move_history.append(move)

        # Switch turn
        self.switch_turn()
        next_player = self.get_current_player()
        self.message = f"Player {next_player.player_id + 1}'s turn"
        
        return True
    
    def save_game(self, filename):
        os.makedirs(SAVE_DIR, exist_ok=True)
        
        filepath = os.path.join(SAVE_DIR, filename)

        state = {
            'mode': self.mode,
            'ai_difficulty': self.ai_difficulty,
            'current_player_idx': self.current_player_idx,
            'winner': self.winner,
            'players': [
                {
                    'player_id': p.player_id,
                    'x': p.x,
                    'y': p.y,
                    'walls_remaining': p.walls_remaining,
                    'is_ai': p.is_ai
                }
                for p in self.players
            ],
            'horizontal_walls': self.board.horizontal_walls,
            'vertical_walls': self.board.vertical_walls,
            'move_history': [
                {
                    'type': m.type.value,
                    'player_id': m.player_id,
                    'old_x': m.old_x,
                    'old_y': m.old_y,
                    'new_x': m.new_x,
                    'new_y': m.new_y,
                    'wall_x': m.wall_x,
                    'wall_y': m.wall_y,
                    'is_horizontal': m.is_horizontal
                }
                for m in self.move_history
            ]
        }

        with open(filepath, 'w') as f:
            json.dump(state, f, indent=4)

        self.message = f"Game saved to {filename}"
        return True

    def load_game(self, filename):
        filepath = os.path.join(SAVE_DIR, filename)
        
        if not os.path.exists(filepath):
            self.message = f"Save file {filename} not found!"
            return False
        
        try:
            with open(filepath, 'r') as f:
                state_dict = json.load(f)
            
            # Restore game state
            self.mode = state_dict['mode']
            self.ai_difficulty = state_dict['ai_difficulty']
            self.current_player_idx = state_dict['current_player_idx']
            self.winner = state_dict['winner']
            
            # Restore players
            for i, p_data in enumerate(state_dict['players']):
                self.players[i].x = p_data['x']
                self.players[i].y = p_data['y']
                self.players[i].walls_remaining = p_data['walls_remaining']
                self.players[i].is_ai = p_data['is_ai']
            
            # Restore board
            self.board.horizontal_walls = state_dict['horizontal_walls']
            self.board.vertical_walls = state_dict['vertical_walls']
            
            # Restore move history
            self.move_history.clear()
            for m_data in state_dict['move_history']:
                move_type = MoveType(m_data['type'])
                if move_type == MoveType.PAWN:
                    move = Move(move_type, m_data['player_id'],
                               old_x=m_data['old_x'], old_y=m_data['old_y'],
                               new_x=m_data['new_x'], new_y=m_data['new_y'])
                else:
                    move = Move(move_type, m_data['player_id'],
                               wall_x=m_data['wall_x'], wall_y=m_data['wall_y'],
                               is_horizontal=m_data['is_horizontal'])
                self.move_history.append(move)
            
            self.redo_stack.clear()
            self.message = f"Game loaded from {filename}"
            return True
            
        except Exception as e:
            self.message = f"Error loading game: {str(e)}"
            return False
        
    def undo(self):
        if not self.move_history:
            self.message = "No moves to undo!"
            return False
        
        last_move = self.move_history.pop()
        self.redo_stack.append(last_move)

        # Switch turn back (without clearing redo stack)
        self.current_player_idx = 1 - self.current_player_idx
        
        if last_move.type == MoveType.PAWN:
            player = self.players[last_move.player_id]
            player.move(last_move.old_x, last_move.old_y)
        else:  
            self.board.remove_wall(last_move.wall_x, last_move.wall_y, last_move.is_horizontal)
            player = self.players[last_move.player_id]
            player.undo_place_wall()
        
        # Clear winner if set
        self.winner = None
        self.message = f"Player {self.current_player_idx + 1}'s turn"
        
        return True
    
    def redo(self):
        if not self.redo_stack:
            self.message = "Nothing to redo!"
            return False
        
        move = self.redo_stack.pop()
        self.move_history.append(move)
        
        # Switch turn to the player who made the move (without clearing redo stack)
        self.current_player_idx = 1 - self.current_player_idx
        
        if move.type == MoveType.PAWN:
            player = self.players[move.player_id]
            player.move(move.new_x, move.new_y)
            
            # Check win condition
            if player.has_won():
                self.winner = player.player_id
                self.message = f"Player {player.player_id + 1} wins!"
                return True
        else:  
            self.board.place_wall(move.wall_x, move.wall_y, move.is_horizontal)
            player = self.players[move.player_id]
            player.place_wall()
        
        if self.winner is None:
            self.message = f"Player {self.current_player_idx + 1}'s turn"
        
        return True
    
    def reset_game(self):
        self.board = Board()
        self.players = [Player(0), Player(1)]
        self.current_player_idx = 0
        self.winner = None
        self.message = "Player 1's turn"
        self.move_history.clear()
        self.redo_stack.clear()
        
        # Restore AI flag
        if self.mode == "human_vs_ai":
            self.players[1].is_ai = True
        