from collections import deque
from util.constants import BOARD_SIZE

class Position:
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __eq__(self, other):
        if not isinstance(other, Position):
            return False
        return self.x == other.x and self.y == other.y
    
    def __hash__(self):
        return hash((self.x, self.y))
    
    def __repr__(self):
        return f"Position({self.x}, {self.y})"
    
def get_neighbors(pos, board):
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    neighbors = []
    for dx, dy in directions:
        nx, ny = pos.x + dx, pos.y + dy
        
        if not board.is_valid_position(nx, ny):
            continue
        if board.is_path_blocked(pos.x, pos.y, nx, ny):
            continue

        neighbors.append(Position(nx, ny))

    return neighbors

# Breadth-First Search to check for valid path
def has_valid_path(board, start_x, start_y, goal_row):
    if start_y == goal_row:
        return True
    
    visited = set()
    queue = deque()
    start = Position(start_x, start_y)
    
    queue.append(start)
    visited.add(start)

    while queue:
        current = queue.popleft()
        
        if current.y == goal_row:
            return True
        
        for neighbor in get_neighbors(current, board):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    
    return False

def find_shortest_path(board, start_x, start_y, goal_row):
    if start_y == goal_row:
        return 0
    
    visited = set()
    queue = deque()
    distances = deque()
    start = Position(start_x, start_y)
    
    queue.append(start)
    distances.append(0)
    visited.add(start)

    while queue:
        current = queue.popleft()
        distance = distances.popleft()
        
        if current.y == goal_row:
            return distance
        
        for neighbor in get_neighbors(current, board):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
                distances.append(distance + 1)
    
    return float('inf') # No path found