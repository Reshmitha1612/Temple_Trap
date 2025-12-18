import heapq
import copy
from collections import deque

# ------------------ TILE DEFINITIONS ------------------

TILES = {
    'A': {'top': {'I','II'}, 'ground': set(), 'hole': False, 'stairs': set()},
    'B': {'top': {'I','II'}, 'ground': set(), 'hole': False, 'stairs': set()},
    'C': {'top': {'II','IV'}, 'ground': set(), 'hole': False, 'stairs': set()},
    'D': {'top': {'IV'}, 'ground': {'II'}, 'hole': True, 'stairs': {'IV'}},
    'E': {'top': {'IV'}, 'ground': {'II'}, 'hole': True, 'stairs': {'IV'}},
    'F': {'top': set(), 'ground': {'I','II'}, 'hole': True, 'stairs': set()},
    'G': {'top': set(), 'ground': {'I','II'}, 'hole': True, 'stairs': set()},
    'H': {'top': set(), 'ground': {'I','II'}, 'hole': True, 'stairs': set()},
    '#': {'top': set(), 'ground': set(), 'hole': False, 'stairs': set()}
}

sign={'=':'A','[]':'B','+':'C','<>':'D','*':'E','>':'F','X':'G','O':'H', '-':'#'}

INDEX_TO_RC = {i: [i//3, i%3] for i in range(9)}
RC_TO_INDEX = {(r, c): r * 3 + c for r in range(3) for c in range(3)}

side = ['I','II','III','IV']

number_to_side={1:'I',2:'II',3:'III',4:'IV'}
side_to_number={'I':1,'II':2,'III':3,'IV':4}

# ------------------ STATE REPRESENTATION ------------------

class State:
    def __init__(self, puzzle, pawn_position, pawn_floor, blank):
        self.puzzle = puzzle
        self.pawn_position = pawn_position
        self.pawn_floor = pawn_floor
        self.blank = blank
        self.f = 0
        self.g = 0
        self.parent = None
        self.action = None
        self.movements=[(-1, 0), (0, 1), (1, 0), (0, -1)]

    def __lt__(self, other):
        return self.f < other.f

    def __eq__(self, other):
        return (
            isinstance(other, State)
            and tuple(tuple(row) for row in self.puzzle) == tuple(tuple(row) for row in other.puzzle)
            and self.pawn_position == other.pawn_position
            and self.pawn_floor == other.pawn_floor
            and self.blank == other.blank
        )

    def __hash__(self):
        return hash((tuple(tuple(row) for row in self.puzzle), self.pawn_position, self.pawn_floor, self.blank))
    
# ------------------ HEURISTIC FUNCTION------------------

def h(state: State):
    pawn_r, pawn_c = divmod(state.pawn_position, 3)
    hole_positions = [
        (r, c)
        for r in range(3)
        for c in range(3)
        if TILES[sign[state.puzzle[r][c]]]['hole']
    ]
    min_dist = float('inf')
    for hr, hc in hole_positions:
        d = abs(pawn_r - hr) + abs(pawn_c - hc)
        if d < min_dist:
            min_dist = d
    return min_dist


# ------------------ PAWN REACHABLE ------------------

def new_state(state, row, col, floor, cost):
    puzzle_copy = [r.copy() for r in state.puzzle]
    new = State(puzzle_copy, row * 3 + col, floor, state.blank)
    new.g = state.g + cost + 1
    new.parent = state
    new.action = f"pawn from {state.pawn_position} to {row*3 + col} ({floor})"
    return new

def pawn_reachable(TILES, state: State):
    reachable = []
    start_pos = (state.pawn_position, state.pawn_floor)
    queue = deque([(start_pos, 0)])
    visited = set([start_pos])

    blank_row, blank_col = INDEX_TO_RC[state.blank]
            
    while queue:
        
        (cell, floor), dist = queue.popleft()
        row, col = INDEX_TO_RC[cell]
        src_tile = TILES[sign[state.puzzle[row][col]]]

        for i, (dr, dc) in enumerate(state.movements):
            R, C = row + dr, col + dc
            if not (R in [0,1,2] and C in [0,1,2]):
                continue
            if (R, C) == (blank_row, blank_col):
                continue
            dst_tile = TILES[sign[state.puzzle[R][C]]]
            side_dir = side[i]
            opposite_dir = side[(i + 2) % 4]
            moves = []
            if floor == 'ground':
                if side_dir in src_tile['ground']:
                    if opposite_dir in dst_tile['ground']:
                        moves.append('ground')
                    if opposite_dir in dst_tile['top']:
                        moves.append('top')
                if side_dir in src_tile['stairs']:
                    if opposite_dir in dst_tile['top']:
                        moves.append('top')
            elif floor == 'top':
                if side_dir in src_tile['top']:
                    if opposite_dir in dst_tile['top']:
                        moves.append('top')
                    if opposite_dir in dst_tile['stairs']:
                        moves.append('ground')
            for next_floor in moves:
                next_pos = (R * 3 + C, next_floor)
                if next_pos not in visited:
                    visited.add(next_pos)
                    queue.append((next_pos, dist + 1))
                    if dst_tile['hole']:
                        reachable.append(new_state(state, R, C, next_floor, dist))
    return reachable

# ------------------ TILE SWAP WITH BLANK ------------------

def tile_swap_blank(TILES, state: State):
    blank_row, blank_col = INDEX_TO_RC[state.blank]
    pawn_row, pawn_col = INDEX_TO_RC[state.pawn_position]
    blank_reach = []
    for dr, dc in state.movements:
        r, c = blank_row + dr, blank_col + dc
        if (r in [0,1,2] and c in [0,1,2]):
            if(r == pawn_row and c == pawn_col):
                continue
            new_puzzle = [row.copy() for row in state.puzzle]
            new_puzzle[blank_row][blank_col], new_puzzle[r][c] = new_puzzle[r][c], new_puzzle[blank_row][blank_col]
            new_state_obj = State(new_puzzle, state.pawn_position, state.pawn_floor, r * 3 + c)
            new_state_obj.g = state.g + 1
            new_state_obj.f = new_state_obj.g + h(new_state_obj)
            new_state_obj.parent = state
            new_state_obj.action = f"Swap tile {state.puzzle[r][c]} from {r*3 + c} with blank {state.blank}"

            blank_reach.append(new_state_obj)

    return blank_reach


# ------------------ COMBINE MOVES ------------------

def combind_state(TILES, state: State):
    next_states = []
    for func in (pawn_reachable, tile_swap_blank):
        for s in func(TILES, state):
            next_states.append(s)
    return next_states

# ------------------ GET EXIT PATH ------------------

def exit_path(TILES, state: State):
    queue = deque([(state.pawn_position, state.pawn_floor, [])])
    visited = set([(state.pawn_position, state.pawn_floor)])
    blank_row, blank_col = INDEX_TO_RC[state.blank]
    while queue:
        pawn_pos, pawn_floor, path = queue.popleft()
        row, col = INDEX_TO_RC[pawn_pos]

        if pawn_pos == 0 and pawn_floor == "top" and 'IV' in TILES[sign[state.puzzle[0][0]]]['top']:
            return path + [(pawn_pos, pawn_floor, "EXIT")]
        
        if pawn_pos == 0 and pawn_floor == "ground" and 'IV' in TILES[sign[state.puzzle[0][0]]]['stairs']:
            return path + [(pawn_pos, pawn_floor, "EXIT")]

        curr_tile = TILES[sign[state.puzzle[row][col]]]

        for i, (dr, dc) in enumerate(state.movements):
            r, c = row + dr, col + dc
            if not (r in [0,1,2] and c in [0,1,2]):
                continue
            if (r, c) == (blank_row, blank_col):
                continue

            next_tile = TILES[sign[state.puzzle[r][c]]]
            side_dir = side[i]
            opp_dir = side[(i + 2) % 4]

            moves = []
            if pawn_floor == "ground":
                if side_dir in curr_tile['ground'] and opp_dir in next_tile['ground']:
                    moves.append(("ground", "move"))
                if side_dir in curr_tile['stairs'] and opp_dir in next_tile['top']:
                    moves.append(("top", "stairs up"))
            elif pawn_floor == "top":
                if side_dir in curr_tile['top'] and opp_dir in next_tile['top']:
                    moves.append(("top", "move"))
                if side_dir in curr_tile['top'] and opp_dir in next_tile['stairs']:
                    moves.append(("ground", "stairs down"))

            for next_floor, action in moves:
                next_state = (r * 3 + c, next_floor)
                if next_state not in visited:
                    visited.add(next_state)
                    queue.append((r * 3 + c, next_floor, path + [(r * 3 + c, next_floor, action)]))

    return None

# ------------------ A* SEARCH ------------------

def astar(TILES, initial_state: State):
    heap = []
    initial_state.f = initial_state.g + h(initial_state)
    heapq.heappush(heap, initial_state)
    visited = set()
    nodes_explored = 0
    max_iterations = 100000  # Safety limit

    while heap and nodes_explored < max_iterations:
        s = heapq.heappop(heap)
        
        if s in visited:
            continue
            
        visited.add(s)
        nodes_explored += 1
        
        # Progress indicator
        if nodes_explored % 1000 == 0:
            print(f"Explored {nodes_explored} nodes, queue size: {len(heap)}, g={s.g}, f={s.f}")
        
        exit_moves = exit_path(TILES, s)
        if exit_moves:
            print(f"\nSolution found after exploring {nodes_explored} nodes!")
            return s, exit_moves
        
        for state_next in combind_state(TILES, s):
            if state_next not in visited:
                state_next.f = state_next.g + h(state_next)
                heapq.heappush(heap, state_next)
    
    if nodes_explored >= max_iterations:
        print(f"\nReached maximum iterations ({max_iterations}). No solution found.")
    else:
        print(f"\nExplored all {nodes_explored} reachable states. No solution exists.")
    
    return None, None

# ------------------ PRINT SOLUTION ------------------

def display_solution(final_state, pawn_exit_path):
    
    if not final_state:
        print("No solution found.")
        return

    def reconstruct_path(state):
        path = []
        while state:
            path.insert(0, state)
            state = state.parent
        return path

    def show_state(step_index, state):
        print(f"Step {step_index}")
        print(f"Action: {state.action or 'Initial state'}")
        print(f"Pawn Position: {state.pawn_position} ({state.pawn_floor}) | Blank Position: {state.blank}")
        print("Puzzle Layout:")
        for row in state.puzzle:
            print("  " + " ".join(row))
        print(f"g = {state.g}, f = {state.f}")
        print("-" * 60)

    def show_pawn_exit(start_index, exit_path):
        print("\n==== PAWN EXIT PATH ====")
        exit_cost = 0
        for i, (cell, floor, move) in enumerate(exit_path, start=start_index):
            print(f"Step {i}: Pawn at Cell {cell} ({floor}) - {move}")
            exit_cost += 1
        return exit_cost

    path_to_goal = reconstruct_path(final_state)
    print(f"\nSOLUTION FOUND IN {len(path_to_goal)} MOVES")
    print("=" * 60)

    for i, state in enumerate(path_to_goal):
        show_state(i, state)

    exit_cost = show_pawn_exit(len(path_to_goal), pawn_exit_path) if pawn_exit_path else 0
    total_cost = final_state.g + exit_cost

    print("\n#### FINAL STATISTICS ####")
    print(f"Cost to reach goal configuration: {final_state.g}")
    print(f"Cost for pawn to exit: {exit_cost}")
    print(f"Total cost for pawn to escape: {total_cost}")

# ------------------ ORIENTATION UPDATER ------------------

def rotate_tile(v, moves):
    return (v + moves - 1) % 4 + 1  

def rotation_tiles(base_tiles, orientation, board):
    oriented_tiles = copy.deepcopy(base_tiles)
    for i, tile_sign in enumerate(board):
        if tile_sign == '-' or tile_sign == '#':
            continue
        moves = orientation[i]
        cell = sign[tile_sign]
        tile = base_tiles[cell]
        oriented_tiles[cell]['top'] = {number_to_side[rotate_tile(side_to_number[s], moves)] for s in tile['top']}
        oriented_tiles[cell]['ground'] = {number_to_side[rotate_tile(side_to_number[s], moves)] for s in tile['ground']}
        oriented_tiles[cell]['stairs'] = {number_to_side[rotate_tile(side_to_number[s], moves)] for s in tile['stairs']}
        oriented_tiles[cell]['hole'] = tile['hole']
    return oriented_tiles

# ------------------ INPUT BOARD WITH YOUR METHOD ------------------

def convert_angle_to_rotations(angle):
    """Convert angle (0, 90, 180, 270) to number of 90-degree rotations"""
    return (angle // 90) % 4

def input_board():
    """Input board using your input method"""
    board_flat = []
    orientations = []
    pawn_tile_symbol = None
    pawn_pos = None
    blank_pos = None
    
    print("\nBase Tiles:")
    print("A (=): top sides I,II")
    print("B ([]): top sides I,II") 
    print("C (+): top sides II,IV")
    print("D (<>): top IV, ground II, hole, stairs IV")
    print("E (*): top IV, ground II, hole, stairs IV")
    print("F (>): ground I,II, hole")
    print("G (X): ground I,II, hole")
    print("H (O): ground I,II, hole")
    print("\nDirections: I=North, II=East, III=South, IV=West")
    print("\nEnter tile and orientation (CW degrees: 0, 90, 180, 270) for each cell.")
    print("Use 'Blank' for empty tile.")
    print("Tiles: A, B, C, D, E, F, G, H")
    print()
    
    for r in range(3):
        for c in range(3):
            while True:
                try:
                    inp = input(f"Tile at ({r},{c}): ").strip().split()
                    if len(inp) == 0:
                        raise ValueError("Empty input")
                    
                    tile_id = inp[0].upper()
                    
                    if tile_id in ('BLANK', '-'):
                        # This is the blank position
                        board_flat.append('-')
                        orientations.append(0)
                        blank_pos = r * 3 + c
                        break
                    
                    if tile_id not in TILES or tile_id == '#':
                        raise ValueError(f"Invalid tile '{tile_id}'. Use A-H or Blank")
                    
                    angle = int(inp[1]) if len(inp) > 1 else 0
                    if angle not in [0, 90, 180, 270]:
                        raise ValueError(f"Invalid angle '{angle}'. Use 0, 90, 180, or 270")
                    
                    # Convert tile ID to symbol
                    tile_symbol = [k for k, v in sign.items() if v == tile_id][0]
                    board_flat.append(tile_symbol)
                    orientations.append(convert_angle_to_rotations(angle))
                    break
                    
                except Exception as e:
                    print(f"Invalid input: {e}. Try again.")
    
    # Get pawn tile
    while True:
        try:
            pawn_tile = input("\nEnter pawn tile (A-H): ").strip().upper()
            if pawn_tile not in TILES or pawn_tile == '#':
                raise ValueError(f"Invalid tile '{pawn_tile}'")
            
            # Find pawn position
            pawn_symbol = [k for k, v in sign.items() if v == pawn_tile][0]
            found = False
            for i, tile in enumerate(board_flat):
                if tile == pawn_symbol:
                    pawn_pos = i
                    pawn_tile_symbol = pawn_symbol
                    found = True
                    break
            
            if not found:
                raise ValueError(f"Pawn tile '{pawn_tile}' not found on board")
            break
        except Exception as e:
            print(f"Invalid input: {e}. Try again.")
    
    # Get pawn floor
    while True:
        pawn_floor = input("Enter pawn floor (ground/top) [default: ground]: ").strip().lower()
        if pawn_floor == '':
            pawn_floor = 'ground'
        if pawn_floor in ['ground', 'top']:
            break
        print("Invalid floor. Use 'ground' or 'top'.")
    
    return board_flat, orientations, pawn_pos, blank_pos, pawn_floor


# ------------------ MAIN ------------------

if __name__ == "__main__":
    print("=" * 60)
    print("PUZZLE SOLVER - Interactive Input Mode")
    print("=" * 60)
    
    # Input board
    board_flat, orientations, pawn_pos, blank_pos, pawn_floor = input_board()
    
    # Convert flat board to 3x3 grid
    start_puzzle = [board_flat[i:i+3] for i in range(0, 9, 3)]
    
    # Apply rotations to tiles
    tiles_oriented = rotation_tiles(TILES, orientations, board_flat)
    
    # Create initial state
    start_state = State(
        puzzle=start_puzzle,
        pawn_position=pawn_pos,
        pawn_floor=pawn_floor,
        blank=blank_pos
    )
    
    print("\n" + "=" * 60)
    print("INITIAL STATE")
    print("=" * 60)
    print(f"Pawn Position: {pawn_pos} ({pawn_floor})")
    print(f"Blank Position: {blank_pos}")
    print("Board:")
    for row in start_puzzle:
        print("  " + " ".join(row))
    
    # Show oriented tiles for debugging
    print("\nOriented Tile Properties:")
    for r in range(3):
        for c in range(3):
            tile_sym = start_puzzle[r][c]
            if tile_sym == '-':
                print(f"  ({r},{c}) BLANK")
            else:
                tile_id = sign[tile_sym]
                tile_props = tiles_oriented[tile_id]
                print(f"  ({r},{c}) {tile_sym} ({tile_id}): top={tile_props['top']}, ground={tile_props['ground']}, stairs={tile_props['stairs']}, hole={tile_props['hole']}")
    print()
    
    # Solve puzzle
    print("Searching for solution...")
    final_state, exit_moves = astar(tiles_oriented, start_state)
    
    # Display solution
    print("\n" + "=" * 60)
    display_solution(final_state, exit_moves)
