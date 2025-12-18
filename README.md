# Puzzle Solver - A* Search Algorithm

A Python-based puzzle solver that uses the A* search algorithm to find optimal solutions for a tile-sliding puzzle game where a pawn must navigate through a 3x3 grid with multi-level tiles to reach the exit.

## Problem Description

This puzzle involves:
- A **3x3 grid** with 8 tiles and 1 blank space
- A **pawn** that can move on two levels: `ground` and `top`
- **8 different tile types** (A-H) with unique connectivity patterns
- **Tile rotations** in 90° increments
- **Special tiles** with holes, stairs, and multi-level connections
- **Goal**: Move the pawn to position (0,0) on the top level facing west to exit

### Tile Types

| Symbol | Tile | Top Connections | Ground Connections | Special Properties |
|--------|------|-----------------|--------------------|--------------------|
| `=` | A | North, East | - | - |
| `[]` | B | North, East | - | - |
| `+` | C | East, West | - | - |
| `<>` | D | West | East | Hole, Stairs (West) |
| `*` | E | West | East | Hole, Stairs (West) |
| `>` | F | - | North, East | Hole |
| `X` | G | - | North, East | Hole |
| `O` | H | - | North, East | Hole |

**Directions:**
- `I` = North (up)
- `II` = East (right)
- `III` = South (down)
- `IV` = West (left)

## 🚀 Features

- **A* Search Algorithm**: Optimal pathfinding with heuristic-based search
- **Interactive Input**: User-friendly tile-by-tile input system
- **Rotation Support**: Handle tiles rotated at 0°, 90°, 180°, or 270°
- **Multi-level Movement**: Track pawn movement on ground and top levels
- **Step-by-step Solution**: Detailed output showing each move
- **Progress Tracking**: Real-time progress indicators during search
- **Cost Calculation**: Displays movement costs and total solution cost

## 📋 Prerequisites

- Python 3.7 or higher
- No external dependencies (uses only standard library)

## 🔧 Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/puzzle-solver.git
cd puzzle-solver
```

2. Run the solver:
```bash
python puzzle_solver.py
```

## 💻 Usage

### Running the Program
```bash
python puzzle_solver.py
```

### Input Format

The program will prompt you for each cell in the 3x3 grid (positions 0,0 through 2,2):

1. **For each tile**: Enter `<TileID> <Rotation>`
   - `TileID`: A letter from A to H
   - `Rotation`: 0, 90, 180, or 270 (degrees clockwise)
   
2. **For blank space**: Enter `Blank`

3. **Pawn tile**: Enter the tile letter where the pawn starts

4. **Pawn floor**: Enter `ground` or `top` (default: ground)

### Example Input (Starter-1)
```
Tile at (0,0): C 0
Tile at (0,1): D 0
Tile at (0,2): G 180
Tile at (1,0): B 90
Tile at (1,1): Blank
Tile at (1,2): H 270
Tile at (2,0): A 0
Tile at (2,1): E 0
Tile at (2,2): F 180

Enter pawn tile (A-H): F
Enter pawn floor (ground/top) [default: ground]: ground
```

### Quick Test

Copy and paste this input sequence for a quick test:
```
C 0
D 0
G 180
B 90
Blank
H 270
A 0
E 0
F 180
F
ground
```

## 📊 Output

The program provides:

1. **Initial State**: Shows the starting configuration with tile properties
2. **Search Progress**: Updates every 1000 nodes explored
3. **Solution Path**: Step-by-step moves from start to goal
4. **Cost Analysis**: 
   - Cost to reach goal configuration
   - Cost for pawn to exit
   - Total cost for complete solution

### Example Output
```
============================================================
SOLUTION FOUND IN 15 MOVES
============================================================
Step 0
Action: Initial state
Pawn Position: 8 (ground) | Blank Position: 4
Puzzle Layout:
  + <> X
  [] - O
  = * >
g = 0, f = 2
------------------------------------------------------------
...
#### FINAL STATISTICS ####
Cost to reach goal configuration: 28
Cost for pawn to exit: 2
Total cost for pawn to escape: 30
```

## 🧮 Algorithm Details

### A* Search Implementation

- **Heuristic Function**: Manhattan distance from pawn to nearest hole tile
- **State Representation**: 
  - Board configuration (3x3 grid)
  - Pawn position (0-8)
  - Pawn floor level (ground/top)
  - Blank tile position
- **Move Types**:
  - Pawn movement (with BFS to find reachable positions)
  - Tile sliding (swapping adjacent tile with blank)

### Movement Rules

1. **Ground to Ground**: Requires matching ground connections on adjacent sides
2. **Ground to Top**: Can use stairs or matching connections
3. **Top to Top**: Requires matching top connections
4. **Top to Ground**: Must use stairs or matching connections
5. **Pawn can only move to tiles with holes**

## 🎯 Puzzle Levels

The original code includes 12 predefined levels:
- **Starter**: 4 beginner levels (starter-1 to starter-4)
- **Junior**: 4 intermediate levels (junior-1 to junior-4)
- **Expert**: 4 advanced levels (expert-1 to expert-4)

You can input any of these levels using the interactive input system.

## 🔍 Troubleshooting

### No Solution Found

If the solver reports "No solution exists":
- Verify all tile types are correct (A-H)
- Double-check rotation angles (must be 0, 90, 180, or 270)
- Ensure the pawn tile exists on the board
- Confirm one tile is marked as "Blank"

### Long Execution Time

- The solver explores up to 100,000 nodes maximum
- Complex puzzles may take 30-60 seconds
- Progress indicators show search is working
- If it exceeds the limit, the puzzle may be unsolvable

## 📝 Code Structure
```
puzzle_solver.py
├── Tile Definitions (TILES dictionary)
├── State Class (puzzle state representation)
├── Heuristic Function (h)
├── Pawn Reachable (BFS for pawn moves)
├── Tile Swap (blank tile movements)
├── Exit Path (final path to exit)
├── A* Search (main algorithm)
├── Rotation Handler (tile orientation)
└── Input/Output Functions
```

## 🎓 Algorithm Complexity

- **Time Complexity**: O(b^d) where b is branching factor, d is solution depth
- **Space Complexity**: O(b^d) for storing visited states
- **Typical Performance**: 
  - Simple puzzles: < 5,000 nodes
  - Complex puzzles: 20,000-50,000 nodes
  - Maximum limit: 100,000 nodes

