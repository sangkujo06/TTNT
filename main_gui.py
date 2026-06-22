"""
main_gui.py
-----------
Giao diện đồ hoạ chính bằng Tkinter.

Chức năng:
  • Tạo mê cung ngẫu nhiên (kích thước tuỳ chọn)
  • Chọn thuật toán: DFS / BFS / A*
  • Chạy tìm đường và hiển thị kết quả ngay trên Canvas
  • Nút "So sánh Pygame" mở cửa sổ Pygame so sánh 3 thuật toán
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import subprocess
import sys
import os

from maze_engine import Maze
from algorithms  import dfs, bfs, astar


# ======================================================================
# Hằng số giao diện
# ======================================================================
CELL_PX     = 36          # Pixel mỗi ô (phần trắng bên trong)
WALL_W      = 5           # Độ dày tường (pixel) — đủ dày để thấy rõ
ANIM_DELAY  = 30          # ms giữa mỗi bước hoạt ảnh

# Màu
CLR_BG       = "#1e1e2e"
CLR_PANEL    = "#2a2a3e"
CLR_ACCENT   = "#7aa2f7"
CLR_BTN      = "#3d59a1"
CLR_BTN_HOV  = "#4e6fa8"
CLR_TEXT     = "#cdd6f4"
CLR_SUBTEXT  = "#a6adc8"

CLR_CELL     = "#f0f0f0"   # Ô trắng sáng
CLR_WALL     = "#2c2c54"   # Tường xanh đậm — tương phản rõ với ô trắng
CLR_VISITED  = "#90caf9"
CLR_PATH     = "#ffd700"
CLR_START    = "#50fa7b"
CLR_END      = "#ff5555"

ALGO_MAP = {
    "DFS  (Depth-First Search)":   dfs,
    "BFS  (Breadth-First Search)": bfs,
    "A*   (A-Star + Manhattan)":   astar,
}


# ======================================================================
# Lớp ứng dụng
# ======================================================================
class MazeApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Tìm Đường Trong Mê Cung — DFS / BFS / A*")
        self.configure(bg=CLR_BG)
        self.resizable(False, False)

        self.maze      = None
        self._anim_id  = None
        self._running  = False

        self._build_ui()
        self._new_maze()

    # ------------------------------------------------------------------
    # Xây dựng giao diện
    # ------------------------------------------------------------------
    def _build_ui(self):
        # ── Thanh điều khiển bên trái ──
        ctrl = tk.Frame(self, bg=CLR_PANEL, padx=16, pady=16)
        ctrl.pack(side=tk.LEFT, fill=tk.Y)

        # Tiêu đề
        tk.Label(ctrl, text="🧩 Mê Cung", font=("Segoe UI", 16, "bold"),
                 bg=CLR_PANEL, fg=CLR_ACCENT).pack(pady=(0, 16))

        # Kích thước
        tk.Label(ctrl, text="Kích thước mê cung:", bg=CLR_PANEL,
                 fg=CLR_TEXT, font=("Segoe UI", 10)).pack(anchor="w")
        size_frame = tk.Frame(ctrl, bg=CLR_PANEL)
        size_frame.pack(fill="x", pady=4)
        self._size_var = tk.IntVar(value=12)
        tk.Scale(size_frame, from_=5, to=25, orient=tk.HORIZONTAL,
                 variable=self._size_var, bg=CLR_PANEL, fg=CLR_TEXT,
                 highlightthickness=0, troughcolor=CLR_BG,
                 activebackground=CLR_ACCENT, length=180).pack()

        tk.Label(ctrl, text="Seed (0 = ngẫu nhiên):", bg=CLR_PANEL,
                 fg=CLR_TEXT, font=("Segoe UI", 10)).pack(anchor="w", pady=(8, 0))
        self._seed_var = tk.IntVar(value=0)
        tk.Entry(ctrl, textvariable=self._seed_var, width=10,
                 bg=CLR_BG, fg=CLR_TEXT, insertbackground=CLR_TEXT,
                 relief="flat", font=("Segoe UI", 10)).pack(anchor="w", pady=4)

        # Nút tạo mê cung
        self._make_btn(ctrl, "🔄 Tạo mê cung mới",
                       self._new_maze).pack(fill="x", pady=4)

        ttk.Separator(ctrl, orient="horizontal").pack(fill="x", pady=12)

        # Chọn thuật toán
        tk.Label(ctrl, text="Chọn thuật toán:", bg=CLR_PANEL,
                 fg=CLR_TEXT, font=("Segoe UI", 10)).pack(anchor="w")
        self._algo_var = tk.StringVar(value=list(ALGO_MAP.keys())[0])
        for name in ALGO_MAP:
            tk.Radiobutton(ctrl, text=name, variable=self._algo_var,
                           value=name, bg=CLR_PANEL, fg=CLR_TEXT,
                           selectcolor=CLR_BG, activebackground=CLR_PANEL,
                           activeforeground=CLR_ACCENT,
                           font=("Segoe UI", 9)).pack(anchor="w", pady=2)

        ttk.Separator(ctrl, orient="horizontal").pack(fill="x", pady=12)

        # Nút chạy
        self._make_btn(ctrl, "▶  Chạy tìm đường",
                       self._run_algo, accent=True).pack(fill="x", pady=4)
        self._make_btn(ctrl, "⏹  Dừng hoạt ảnh",
                       self._stop_anim).pack(fill="x", pady=2)

        ttk.Separator(ctrl, orient="horizontal").pack(fill="x", pady=12)

        # Nút Pygame
        self._make_btn(ctrl, "🎮 So sánh Pygame",
                       self._open_pygame).pack(fill="x", pady=4)

        ttk.Separator(ctrl, orient="horizontal").pack(fill="x", pady=12)

        # Bảng thống kê
        tk.Label(ctrl, text="Thống kê:", bg=CLR_PANEL,
                 fg=CLR_SUBTEXT, font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self._stat_visited = tk.StringVar(value="Ô đã duyệt : —")
        self._stat_path    = tk.StringVar(value="Độ dài đường: —")
        self._stat_time    = tk.StringVar(value="Thời gian   : —")
        for sv in (self._stat_visited, self._stat_path, self._stat_time):
            tk.Label(ctrl, textvariable=sv, bg=CLR_PANEL, fg=CLR_TEXT,
                     font=("Courier New", 9), justify="left").pack(anchor="w")

        # Chú thích màu
        tk.Label(ctrl, text="\nChú thích:", bg=CLR_PANEL,
                 fg=CLR_SUBTEXT, font=("Segoe UI", 9, "bold")).pack(anchor="w")
        legends = [
            (CLR_START,   "Ô xuất phát"),
            (CLR_END,     "Ô đích"),
            (CLR_VISITED, "Ô đã duyệt"),
            (CLR_PATH,    "Đường đi"),
        ]
        for color, label in legends:
            f = tk.Frame(ctrl, bg=CLR_PANEL)
            f.pack(anchor="w", pady=1)
            tk.Label(f, bg=color, width=3, height=1).pack(side=tk.LEFT)
            tk.Label(f, text=f"  {label}", bg=CLR_PANEL, fg=CLR_TEXT,
                     font=("Segoe UI", 9)).pack(side=tk.LEFT)

        # ── Canvas mê cung ──
        right = tk.Frame(self, bg=CLR_BG, padx=16, pady=16)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._canvas = tk.Canvas(right, bg=CLR_BG, highlightthickness=0)
        self._canvas.pack()

    def _make_btn(self, parent, text, cmd, accent=False):
        bg = CLR_ACCENT if accent else CLR_BTN
        b = tk.Button(parent, text=text, command=cmd,
                      bg=bg, fg="#ffffff" if accent else CLR_TEXT,
                      activebackground=CLR_BTN_HOV, activeforeground="#ffffff",
                      relief="flat", font=("Segoe UI", 10),
                      padx=8, pady=6, cursor="hand2")
        return b

    # ------------------------------------------------------------------
    # Tạo mê cung mới
    # ------------------------------------------------------------------
    def _new_maze(self):
        self._stop_anim()
        n = self._size_var.get()
        seed_val = self._seed_var.get()
        seed = seed_val if seed_val != 0 else None
        self.maze = Maze(n, n, seed=seed)
        self._draw_maze()
        self._reset_stats()

    def _draw_maze(self):
        """
        Vẽ mê cung theo phong cách pixel-block:
          - Mỗi ô chiếm STEP×STEP pixel (ô trắng + tường bao quanh)
          - Nền tổng thể màu tường đậm, ô trắng nổi bật bên trong
        """
        maze  = self.maze
        n     = maze.rows
        STEP  = CELL_PX + WALL_W
        W     = n * STEP + WALL_W
        self._canvas.config(width=W, height=W)
        self._canvas.delete("all")

        # Nền = màu tường (fill toàn bộ canvas trước)
        self._canvas.create_rectangle(0, 0, W, W, fill=CLR_WALL, outline="")

        for r in range(1, n + 1):
            for c in range(1, n + 1):
                cell = maze.grid[(r, c)]
                x0 = (c - 1) * STEP + WALL_W
                y0 = (r - 1) * STEP + WALL_W
                x1 = x0 + CELL_PX
                y1 = y0 + CELL_PX

                # Vẽ phần nội thất ô (trắng)
                self._canvas.create_rectangle(
                    x0, y0, x1, y1,
                    fill=CLR_CELL, outline="",
                    tags=f"cell_{r}_{c}")

                # Phá tường Đông → lấp khoảng tường bên phải bằng CLR_CELL
                if cell['E'] and c < n:
                    self._canvas.create_rectangle(
                        x1, y0, x1 + WALL_W, y1,
                        fill=CLR_CELL, outline="")

                # Phá tường Nam → lấp khoảng tường bên dưới bằng CLR_CELL
                if cell['S'] and r < n:
                    self._canvas.create_rectangle(
                        x0, y1, x1, y1 + WALL_W,
                        fill=CLR_CELL, outline="")

        # Start & End
        self._color_cell(*maze.start(), CLR_START)
        self._color_cell(*maze.end(),   CLR_END)

    # ------------------------------------------------------------------
    # Tô màu ô
    # ------------------------------------------------------------------
    def _color_cell(self, r, c, color):
        x = (c - 1) * CELL_PX
        y = (r - 1) * CELL_PX
        tag = f"cell_{r}_{c}"
        self._canvas.itemconfig(tag, fill=color)

    # ------------------------------------------------------------------
    # Chạy thuật toán + hoạt ảnh
    # ------------------------------------------------------------------
    def _run_algo(self):
        if self.maze is None:
            return
        self._stop_anim()
        self._draw_maze()

        algo_name = self._algo_var.get()
        algo_fn   = ALGO_MAP[algo_name]
        st, en    = self.maze.start(), self.maze.end()

        t0  = time.perf_counter()
        res = algo_fn(self.maze, st, en)
        t1  = time.perf_counter()

        visited = res['visited']
        path    = res['path'] or []

        self._stat_visited.set(f"Ô đã duyệt : {len(visited)}")
        self._stat_path.set(   f"Độ dài đường: {len(path)} bước")
        self._stat_time.set(   f"Thời gian   : {(t1-t0)*1000:.3f} ms")

        self._running = True
        self._anim_step(visited, path, st, en, 0)

    def _anim_step(self, visited, path, st, en, idx):
        if not self._running:
            return
        if idx < len(visited):
            r, c = visited[idx]
            if (r, c) != st and (r, c) != en:
                self._color_cell(r, c, CLR_VISITED)
            self._anim_id = self.after(
                ANIM_DELAY,
                lambda: self._anim_step(visited, path, st, en, idx + 1))
        else:
            # Hiển thị đường đi
            for r, c in path:
                if (r, c) != st and (r, c) != en:
                    self._color_cell(r, c, CLR_PATH)
            # Vẽ lại start/end lên trên
            self._color_cell(*st, CLR_START)
            self._color_cell(*en, CLR_END)
            self._running = False

    def _stop_anim(self):
        self._running = False
        if self._anim_id:
            self.after_cancel(self._anim_id)
            self._anim_id = None

    def _reset_stats(self):
        self._stat_visited.set("Ô đã duyệt : —")
        self._stat_path.set(   "Độ dài đường: —")
        self._stat_time.set(   "Thời gian   : —")

    # ------------------------------------------------------------------
    # Mở Pygame
    # ------------------------------------------------------------------
    def _open_pygame(self):
        script = os.path.join(os.path.dirname(__file__), "visualize_pygame.py")
        try:
            subprocess.Popen([sys.executable, script])
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không mở được Pygame:\n{e}")


# ======================================================================
# Entry point
# ======================================================================
if __name__ == "__main__":
    app = MazeApp()
    app.mainloop()