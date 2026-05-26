from util.constants import BOARD_SIZE

class Board:
    def __init__(self):
        self.horizontal_walls = [[False for _ in range(BOARD_SIZE - 1)] for _ in range(BOARD_SIZE - 1)]
        self.vertical_walls = [[False for _ in range(BOARD_SIZE - 1)] for _ in range(BOARD_SIZE - 1)] 
    
    def is_valid_position(self, x, y):
        return 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE
    
    def can_place_wall(self, x, y, is_horizontal):
        if not (0 <= x < BOARD_SIZE - 1 and 0 <= y < BOARD_SIZE - 1):
            return False
        
        if is_horizontal:

            #check if wall already exists
            if self.horizontal_walls[y][x]:
                return False
            
            #check for overlapping vertical walls
            if x > 0 and self.vertical_walls[y][x - 1]:
                return False
            if x < BOARD_SIZE - 2 and self.vertical_walls[y][x]:
                return False
            
            #check for adjacent horizontal walls
            if x > 0 and self.horizontal_walls[y][x - 1]:
                return False
            if x < BOARD_SIZE - 2 and self.horizontal_walls[y][x + 1]:
                return False
        else:
            #check if wall already exists
            if self.vertical_walls[y][x]:
                return False
            
            #check for overlapping horizontal walls
            if y > 0 and self.horizontal_walls[y - 1][x]:
                return False
            if y < BOARD_SIZE - 2 and self.horizontal_walls[y][x]:
                return False
            
            #check for adjacent vertical walls
            if y > 0 and self.vertical_walls[y - 1][x]:
                return False
            if y < BOARD_SIZE - 2 and self.vertical_walls[y + 1][x]:
                return False
        return True
    
    def place_wall(self, x, y, is_horizontal):
        if not self.can_place_wall(x, y, is_horizontal):
            return False
        
        if is_horizontal:
            self.horizontal_walls[y][x] = True
        else:
            self.vertical_walls[y][x] = True
        
        return True
    
    #For Undo Functionality
    def remove_wall(self, x, y, is_horizontal):
        if 0 <= x < BOARD_SIZE - 1 and 0 <= y < BOARD_SIZE - 1:
            if is_horizontal:
                self.horizontal_walls[y][x] = False
            else:
                self.vertical_walls[y][x] = False

    #Checks if path between two adjacent cells is blocked by a wall
    def is_path_blocked(self, x1, y1, x2, y2):
        # move right
        if x2 == x1 + 1 and y2 == y1:
            if x1 < BOARD_SIZE - 1:
                if y1 > 0 and self.vertical_walls[y1 - 1][x1]:
                    return True
                if y1 < BOARD_SIZE - 1 and self.vertical_walls[y1][x1]:
                    return True
        # move left
        elif x2 == x1 - 1 and y2 == y1:
            if x2 < BOARD_SIZE - 1:
                if y1 > 0 and self.vertical_walls[y1 - 1][x2]:
                    return True
                if y1 < BOARD_SIZE - 1 and self.vertical_walls[y1][x2]:
                    return True
        # move down
        elif x2 == x1 and y2 == y1 + 1:
            if y1 < BOARD_SIZE - 1:
                if x1 > 0 and self.horizontal_walls[y1][x1 - 1]:
                    return True
                if x1 < BOARD_SIZE - 1 and self.horizontal_walls[y1][x1]:
                    return True
        # move up
        elif x2 == x1 and y2 == y1 - 1:
            if y2 < BOARD_SIZE - 1:
                if x1 > 0 and self.horizontal_walls[y2][x1 - 1]:
                    return True
                if x1 < BOARD_SIZE - 1 and self.horizontal_walls[y2][x1]:
                    return True
        return False
