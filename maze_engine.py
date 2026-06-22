"""
maze_engine.py
--------------
Thay thế thư viện pyamaze — tạo mê cung hoàn hảo (perfect maze)
bằng thuật toán Recursive Backtracker (DFS).

Cấu trúc dữ liệu:
    maze.grid[row][col] = dict với các khóa 'N','S','E','W'
    giá trị True  = tường bị phá (có thể đi qua)
    giá trị False = còn tường (không đi qua được)

Quy ước toạ độ: (row, col), bắt đầu từ (1,1) đến (rows, cols)
"""

import random


class Maze:
    """Mê cung hoàn hảo được tạo bằng Recursive Backtracker."""

    DIRECTIONS = {
        'N': (-1, 0),
        'S': (1,  0),
        'E': (0,  1),
        'W': (0, -1),
    }
    OPPOSITE = {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}

    def __init__(self, rows: int = 10, cols: int = 10, seed: int = None):
        self.rows = rows
        self.cols = cols
        self._seed = seed
        # grid[r][c] = {'N': bool, 'S': bool, 'E': bool, 'W': bool}
        self.grid = {}
        self._build()

    # ------------------------------------------------------------------
    # Khởi tạo
    # ------------------------------------------------------------------
    def _build(self):
        """Khởi tạo lưới kín rồi phá tường bằng DFS."""
        for r in range(1, self.rows + 1):
            for c in range(1, self.cols + 1):
                self.grid[(r, c)] = {'N': False, 'S': False,
                                     'E': False, 'W': False}
        rng = random.Random(self._seed)
        visited = set()
        self._dfs_carve(1, 1, visited, rng)

    def _dfs_carve(self, r: int, c: int, visited: set, rng: random.Random):
        visited.add((r, c))
        dirs = list(self.DIRECTIONS.keys())
        rng.shuffle(dirs)
        for d in dirs:
            dr, dc = self.DIRECTIONS[d]
            nr, nc = r + dr, c + dc
            if (1 <= nr <= self.rows and 1 <= nc <= self.cols
                    and (nr, nc) not in visited):
                # Phá tường giữa (r,c) và (nr,nc)
                self.grid[(r,  c)][d] = True
                self.grid[(nr, nc)][self.OPPOSITE[d]] = True
                self._dfs_carve(nr, nc, visited, rng)

    # ------------------------------------------------------------------
    # Truy vấn
    # ------------------------------------------------------------------
    def neighbors(self, r: int, c: int) -> list:
        """Trả về danh sách ô kề có thể đi tới (đã phá tường)."""
        result = []
        for d, (dr, dc) in self.DIRECTIONS.items():
            if self.grid[(r, c)][d]:
                result.append((r + dr, c + dc))
        return result

    def start(self):
        return (1, 1)

    def end(self):
        return (self.rows, self.cols)
