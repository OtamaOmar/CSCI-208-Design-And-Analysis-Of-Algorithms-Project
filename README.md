# Maze Generator and Solver

## Report

### Code structure

The application is one file, `Code/MazeSolverAndGenerator.py`, with three classes.

**`Maze`** builds the maze.

- `create_grid(width, height)`: every cell starts with four walls (top, right, bottom, left).
- `generate_dfs()`: randomized depth-first search (recursive backtracker) with an explicit stack.
- `generate_prim()`: randomized Prim's algorithm with a frontier list of walls.
- `add_loops(chance)`: removes extra walls after generation, so the maze has more than one route.
- `cost`: a per-cell weight. About 25% of cells are "mud" and cost 5 to enter; the rest cost 1.

**`MazeSolver`** finds a path from the top-left cell `(0, 0)` to the bottom-right cell.

- `bfs()`: breadth-first search with a `deque`.
- `dijkstra()`: Dijkstra's algorithm with a binary heap (`heapq`); stale heap entries are skipped.
- `astar()`: A* with the Manhattan-distance heuristic.
- Each solver returns `(path, explored)`, where `explored` counts the cells it expanded.

**`MazeApp`** is the Tkinter GUI. It draws walls as lines, mud cells in tan, and the path as blue dots.
All three solve buttons stay visible, so you can run each solver on the same maze.
The status label shows the algorithm, path length, path cost, nodes explored, and time.

### The mazes are not perfect mazes

DFS and Prim's on their own produce *perfect* mazes: exactly one path between any two cells.
This project then calls `add_loops(0.10)`, which removes each remaining interior wall with 10% probability.
This is deliberate. With only one route, every solver must return the same path and the comparison is meaningless.
With loops, there are several routes of different lengths and costs, so the solvers can disagree.

### Generation algorithms

**Randomized DFS.** Start at `(0, 0)`. Repeatedly move to a random unvisited neighbor and remove the wall between them.
Backtrack when the current cell has no unvisited neighbors. Produces long, winding corridors.
Time: O(N), where N = width × height.

**Randomized Prim's.** Start with `(0, 0)` visited and its walls in a frontier list.
Repeatedly remove a random wall from the frontier. If it leads to an unvisited cell, open the wall,
mark the cell visited, and add that cell's walls to the frontier.
A random item is removed in O(1) by swapping it with the last item and popping.
Produces many short dead ends and a "bushy" texture.
Time: O(N), because each wall enters the frontier at most twice.

`add_loops` is O(N) as well.

### Solving algorithms

Let V be the number of cells and E the number of open passages (E ≤ 2V on a grid).

**BFS.** Explores cells in order of number of steps from the start.
It finds the path with the fewest steps, but it ignores cell costs, so that path is not always the cheapest.
Time: O(V + E).

**Dijkstra.** Explores cells in order of total cost from the start, using a min-heap.
It always finds the cheapest path.
Time: O(E log V).

**A\*.** Like Dijkstra, but orders the heap by cost so far plus the Manhattan distance to the goal.
The minimum cell cost is 1, so the Manhattan distance never overestimates the remaining cost.
A* therefore finds a path with the same cost as Dijkstra, while usually expanding fewer cells.
Time: O(E log V) in the worst case.
