import tkinter as tk
import random
import time

random.seed()  # Ensures different maze every time the app launches

class Maze:
    def __init__(self, width, height, mode):
        self.width = width
        self.height = height
        self.grid = self.create_grid(width, height)
        if mode == 0:
            self.generate_dfs()
        else:
            self.generate_bellman_ford()

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

    def generate_bellman_ford(self):
        dist = [[float('inf')] * self.width for _ in range(self.height)]
        dist[0][0] = 0
        visited = {(0, 0)}
        dirs = [(-1, 0, 0, 2), (0, 1, 1, 3), (1, 0, 2, 0), (0, -1, 3, 1)]

        cells = [(y, x) for y in range(self.height) for x in range(self.width)]
        for _ in range(self.height * self.width):
            random.shuffle(cells)
            for y, x in cells:
                if (y, x) not in visited:
                    continue
                neighbors = []
                for dy, dx, w1, w2 in dirs:
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < self.height and 0 <= nx < self.width and (ny, nx) not in visited:
                        manhattan = abs(ny - (self.height - 1)) + abs(nx - (self.width - 1))
                        neighbors.append((manhattan, ny, nx, w1, w2))
                if neighbors:
                    if random.random() < 0.5 and len(neighbors) > 1:
                        _, ny, nx, w1, w2 = random.choice(neighbors)
                    else:
                        neighbors.sort()
                        _, ny, nx, w1, w2 = neighbors[0]
                    self.grid[y][x][w1] = False
                    self.grid[ny][nx][w2] = False
                    visited.add((ny, nx))
                    dist[ny][nx] = dist[y][x] + 1

        for y in range(self.height):
            for x in range(self.width):
                for dy, dx, w1, w2 in dirs:
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < self.height and 0 <= nx < self.width and random.random() < 0.25:
                        self.grid[y][x][w1] = False
                        self.grid[ny][nx][w2] = False

        self.ensure_path(dist)

    def ensure_path(self, dist):
        if dist[self.height - 1][self.width - 1] != float('inf'):
            return

        queue = [(self.height - 1, self.width - 1)]
        parent = {}
        visited = {(self.height - 1, self.width - 1)}
        dirs = [(-1, 0, 0, 2), (0, 1, 1, 3), (1, 0, 2, 0), (0, -1, 3, 1)]

        while queue:
            y, x = queue.pop(0)
            if dist[y][x] != float('inf'):
                current = (y, x)
                path = []
                while current in parent:
                    path.append(current)
                    current = parent[current]
                path.append(current)
                path.reverse()
                for i in range(len(path) - 1):
                    cy, cx = path[i]
                    ny, nx = path[i + 1]
                    for dy, dx, w1, w2 in dirs:
                        if cy + dy == ny and cx + dx == nx:
                            self.grid[cy][cx][w1] = False
                            self.grid[ny][nx][w2] = False
                            dist[ny][nx] = dist[cy][cx] + 1
                return
            for dy, dx, _, _ in dirs:
                ny, nx = y + dy, x + dx
                if 0 <= ny < self.height and 0 <= nx < self.width and (ny, nx) not in visited:
                    visited.add((ny, nx))
                    parent[(ny, nx)] = (y, x)
                    queue.append((ny, nx))

class MazeSolver:
    def __init__(self, maze, mode):
        self.grid = maze.grid
        self.height = maze.height
        self.width = maze.width
        self.mode = mode

    def solve(self):
        return self.bfs() if self.mode == 0 else self.dijkstra()

    def bfs(self):
        queue = [(0, 0)]
        visited = {(0, 0)}
        parent = {}

        while queue:
            y, x = queue.pop(0)
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
            d, y, x = heap.pop(0)
            if (y, x) == (self.height - 1, self.width - 1):
                return self.reconstruct_path(parent, (y, x))
            for dy, dx, wall in [(-1, 0, 0), (0, 1, 1), (1, 0, 2), (0, -1, 3)]:
                ny, nx = y + dy, x + dx
                if 0 <= ny < self.height and 0 <= nx < self.width and not self.grid[y][x][wall]:
                    if dist[ny][nx] > dist[y][x] + 1:
                        dist[ny][nx] = dist[y][x] + 1
                        parent[(ny, nx)] = (y, x)
                        heap.append((dist[ny][nx], ny, nx))
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

        self.button_bellman = tk.Button(self.button_frame, text="Generate with Bellman-Ford", command=lambda: self.generate(1))
        self.button_bellman.pack(side=tk.LEFT)

    def generate(self, mode):
        self.clear_canvas()
        start_time = time.time()
        self.maze = Maze(self.width, self.height, mode)
        elapsed = time.time() - start_time

        self.draw_maze()
        self.info_label.config(text=f"Maze generated using {'DFS' if mode == 0 else 'Bellman-Ford'} in {elapsed:.4f} seconds.")

        self.button_dfs.pack_forget()
        self.button_bellman.pack_forget()

        self.solve_frame = tk.Frame(self.master)
        self.solve_frame.pack()

        self.button_bfs = tk.Button(self.solve_frame, text="Solve with BFS", command=lambda: self.solve(0))
        self.button_bfs.pack(side=tk.LEFT)

        self.button_dijkstra = tk.Button(self.solve_frame, text="Solve with Dijkstra", command=lambda: self.solve(1))
        self.button_dijkstra.pack(side=tk.LEFT)

    def solve(self, mode):
        start_time = time.time()
        solver = MazeSolver(self.maze, mode)
        path = solver.solve()
        elapsed = time.time() - start_time

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
