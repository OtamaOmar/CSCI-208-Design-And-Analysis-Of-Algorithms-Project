import tkinter as tk
import random, heapq
from collections import deque
from time import perf_counter

random.seed()  # Ensures different maze every time the app launches

class Maze:
    def __init__(self, width, height, mode):
        self.width = width
        self.height = height
        self.grid = self.create_grid(width, height)
        # ~25% of cells are "mud" and cost 5 to enter; the rest cost 1
        self.cost = [[random.choice([1, 1, 1, 5]) for _ in range(width)] for _ in range(height)]
        if mode == 0:
            self.generate_dfs()
        else:
            self.generate_prim()
        self.add_loops(0.10)

    def create_grid(self, width, height):
        return [[[True, True, True, True] for _ in range(width)] for _ in range(height)]

    def generate_dfs(self):
        stack = [(0, 0)]
        visited = {(0, 0)}
        dirs = [(-1, 0, 0, 2), (0, 1, 1, 3), (1, 0, 2, 0), (0, -1, 3, 1)]

        while stack:
            y, x = stack[-1]
            neighbors = []
            for dy, dx, w1, w2 in dirs:
                ny, nx = y + dy, x + dx
                if 0 <= ny < self.height and 0 <= nx < self.width and (ny, nx) not in visited:
                    neighbors.append((ny, nx, w1, w2))
            if neighbors:
                ny, nx, w1, w2 = random.choice(neighbors)
                self.grid[y][x][w1] = False
                self.grid[ny][nx][w2] = False
                visited.add((ny, nx))
                stack.append((ny, nx))
            else:
                stack.pop()

    def generate_prim(self):
        dirs = [(-1, 0, 0, 2), (0, 1, 1, 3), (1, 0, 2, 0), (0, -1, 3, 1)]
        visited = {(0, 0)}
        frontier = []  # walls (y, x, ny, nx, w1, w2) between a visited cell and a neighbor

        def add_walls(y, x):
            for dy, dx, w1, w2 in dirs:
                ny, nx = y + dy, x + dx
                if 0 <= ny < self.height and 0 <= nx < self.width and (ny, nx) not in visited:
                    frontier.append((y, x, ny, nx, w1, w2))

        add_walls(0, 0)
        while frontier:
            # O(1) random removal: swap a random wall with the last one, then pop
            i = random.randrange(len(frontier))
            frontier[i], frontier[-1] = frontier[-1], frontier[i]
            y, x, ny, nx, w1, w2 = frontier.pop()
            if (ny, nx) in visited:
                continue
            self.grid[y][x][w1] = False
            self.grid[ny][nx][w2] = False
            visited.add((ny, nx))
            add_walls(ny, nx)

    def add_loops(self, chance):
        # Remove some extra walls so there are several routes to the goal.
        # Only right and down walls are checked, so each wall gets one chance.
        for y in range(self.height):
            for x in range(self.width):
                if x + 1 < self.width and random.random() < chance:
                    self.grid[y][x][1] = False
                    self.grid[y][x + 1][3] = False
                if y + 1 < self.height and random.random() < chance:
                    self.grid[y][x][2] = False
                    self.grid[y + 1][x][0] = False

class MazeSolver:
    def __init__(self, maze, mode):
        self.grid = maze.grid
        self.height = maze.height
        self.width = maze.width
        self.cost = maze.cost
        self.mode = mode

    def solve(self):
        if self.mode == 0:
            return self.bfs()
        if self.mode == 1:
            return self.dijkstra()
        return self.astar()

    def bfs(self):
        queue = deque([(0, 0)])
        visited = {(0, 0)}
        parent = {}

        while queue:
            y, x = queue.popleft()
            if (y, x) == (self.height - 1, self.width - 1):
                return self.reconstruct_path(parent, (y, x))
            for dy, dx, wall in [(-1, 0, 0), (0, 1, 1), (1, 0, 2), (0, -1, 3)]:
                ny, nx = y + dy, x + dx
                if 0 <= ny < self.height and 0 <= nx < self.width and not self.grid[y][x][wall]:
                    if (ny, nx) not in visited:
                        visited.add((ny, nx))
                        parent[(ny, nx)] = (y, x)
                        queue.append((ny, nx))
        return []

    def dijkstra(self):
        dist = [[float('inf')] * self.width for _ in range(self.height)]
        dist[0][0] = 0
        parent = {}
        heap = [(0, 0, 0)]

        while heap:
            d, y, x = heapq.heappop(heap)
            if d > dist[y][x]:
                continue  # stale entry, skip
            if (y, x) == (self.height - 1, self.width - 1):
                return self.reconstruct_path(parent, (y, x))
            for dy, dx, wall in [(-1, 0, 0), (0, 1, 1), (1, 0, 2), (0, -1, 3)]:
                ny, nx = y + dy, x + dx
                if 0 <= ny < self.height and 0 <= nx < self.width and not self.grid[y][x][wall]:
                    new_dist = dist[y][x] + self.cost[ny][nx]
                    if dist[ny][nx] > new_dist:
                        dist[ny][nx] = new_dist
                        parent[(ny, nx)] = (y, x)
                        heapq.heappush(heap, (dist[ny][nx], ny, nx))
        return []

    def astar(self):
        # Manhattan distance never overestimates because every cell costs at least 1,
        # so A* still returns the cheapest path.
        dist = [[float('inf')] * self.width for _ in range(self.height)]
        dist[0][0] = 0
        parent = {}
        heap = [(0, 0, 0, 0)]  # (priority, real distance, y, x)

        while heap:
            _, d, y, x = heapq.heappop(heap)
            if d > dist[y][x]:
                continue  # stale entry, skip
            if (y, x) == (self.height - 1, self.width - 1):
                return self.reconstruct_path(parent, (y, x))
            for dy, dx, wall in [(-1, 0, 0), (0, 1, 1), (1, 0, 2), (0, -1, 3)]:
                ny, nx = y + dy, x + dx
                if 0 <= ny < self.height and 0 <= nx < self.width and not self.grid[y][x][wall]:
                    new_dist = dist[y][x] + self.cost[ny][nx]
                    if dist[ny][nx] > new_dist:
                        dist[ny][nx] = new_dist
                        parent[(ny, nx)] = (y, x)
                        h = abs(ny - (self.height - 1)) + abs(nx - (self.width - 1))
                        heapq.heappush(heap, (dist[ny][nx] + h, dist[ny][nx], ny, nx))
        return []

    def reconstruct_path(self, parent, end):
        path = []
        current = end
        while current != (0, 0):
            path.append(current)
            current = parent.get(current, (-1, -1))
        path.append((0, 0))
        return path[::-1]

class MazeApp:
    def __init__(self, master, width=15, height=15, cell_size=30):
        self.master = master
        self.width = width
        self.height = height
        self.cell_size = cell_size

        self.canvas = tk.Canvas(master, width=width * cell_size, height=height * cell_size, bg='white')
        self.canvas.pack()

        self.info_label = tk.Label(master, text="Choose a maze generation method.")
        self.info_label.pack()

        self.button_frame = tk.Frame(master)
        self.button_frame.pack()

        self.button_dfs = tk.Button(self.button_frame, text="Generate with DFS", command=lambda: self.generate(0))
        self.button_dfs.pack(side=tk.LEFT)

        self.button_prim = tk.Button(self.button_frame, text="Generate with Prim's", command=lambda: self.generate(1))
        self.button_prim.pack(side=tk.LEFT)

    def generate(self, mode):
        self.clear_canvas()
        start_time = perf_counter()
        self.maze = Maze(self.width, self.height, mode)
        elapsed = perf_counter() - start_time

        self.draw_maze()
        name = "DFS" if mode == 0 else "Prim's"
        self.info_label.config(text=f"Maze generated using {name} in {elapsed:.4f} seconds.")

        self.button_dfs.pack_forget()
        self.button_prim.pack_forget()

        self.solve_frame = tk.Frame(self.master)
        self.solve_frame.pack()

        self.button_bfs = tk.Button(self.solve_frame, text="Solve with BFS", command=lambda: self.solve(0))
        self.button_bfs.pack(side=tk.LEFT)

        self.button_dijkstra = tk.Button(self.solve_frame, text="Solve with Dijkstra", command=lambda: self.solve(1))
        self.button_dijkstra.pack(side=tk.LEFT)

    def solve(self, mode):
        start_time = perf_counter()
        solver = MazeSolver(self.maze, mode)
        path = solver.solve()
        elapsed = perf_counter() - start_time

        if not path:
            self.info_label.config(text="No solution found!")
        else:
            self.draw_path(path)
            self.info_label.config(text=f"Solved using {'BFS' if mode == 0 else 'Dijkstra'} in {elapsed:.4f} seconds.")

        self.button_bfs.pack_forget()
        self.button_dijkstra.pack_forget()

    def draw_maze(self):
        for y in range(self.height):
            for x in range(self.width):
                cell = self.maze.grid[y][x]
                x1 = x * self.cell_size
                y1 = y * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                if self.maze.cost[y][x] > 1:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill='#d9c7a3', outline='')
                if cell[0]: self.canvas.create_line(x1, y1, x2, y1)
                if cell[1]: self.canvas.create_line(x2, y1, x2, y2)
                if cell[2]: self.canvas.create_line(x1, y2, x2, y2)
                if cell[3]: self.canvas.create_line(x1, y1, x1, y2)

    def draw_path(self, path):
        for y, x in path:
            cx = x * self.cell_size + self.cell_size // 2
            cy = y * self.cell_size + self.cell_size // 2
            r = self.cell_size // 4
            self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill='blue')

    def clear_canvas(self):
        self.canvas.delete("all")
        if hasattr(self, 'solve_frame'):
            self.solve_frame.pack_forget()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Maze Generator & Solver")
    app = MazeApp(root)
    root.mainloop()
