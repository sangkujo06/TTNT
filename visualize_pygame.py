"""
visualize_pygame.py
-------------------
So sánh trực quan ba thuật toán DFS / BFS / A* trên cùng một mê cung
bằng Pygame. Hiển thị ba panel cạnh nhau, mỗi panel minh hoạ quá trình
duyệt ô (visited) và đường đi cuối cùng (path) của từng thuật toán.

Màu sắc:
    Trắng  — ô trống
    Đen    — tường
    Xanh lá nhạt — ô đã duyệt (visited)
    Vàng   — đường đi tìm được
    Đỏ     — ô đích
    Xanh dương — ô xuất phát

Điều khiển:
    SPACE  — tạo mê cung mới & chạy lại
    ESC    — thoát
"""

import pygame
import sys
import time
import random

from maze_engine import Maze
from algorithms import dfs, bfs, astar

# ──────────────────────────────────────────────
# Hằng số giao diện
# ──────────────────────────────────────────────
ROWS, COLS   = 15, 15          # Kích thước mê cung
CELL         = 36              # Pixel mỗi ô
WALL         = 2               # Độ dày tường (pixel)
PANEL_PAD    = 20              # Khoảng cách giữa các panel
TOP_BAR      = 60              # Chiều cao thanh tiêu đề
BOTTOM_BAR   = 90              # Chiều cao thanh thống kê

PANEL_W = COLS * CELL
PANEL_H = ROWS * CELL
WIN_W   = PANEL_W * 3 + PANEL_PAD * 4
WIN_H   = TOP_BAR + PANEL_H + BOTTOM_BAR

FPS          = 60
ANIM_DELAY   = 0.015           # Giây giữa mỗi bước hoạt ảnh

# Màu sắc
BG          = (30,  30,  30)
WALL_COLOR  = (20,  20,  20)
CELL_EMPTY  = (245, 245, 245)
CELL_VISIT  = (144, 213, 255)   # Xanh nhạt — đã duyệt
CELL_PATH   = (255, 215,  0)    # Vàng — đường đi
CELL_START  = (50,  200,  50)   # Xanh lá — xuất phát
CELL_END    = (220,  60,  60)   # Đỏ — đích
TEXT_COLOR  = (230, 230, 230)
ACCENT      = (100, 180, 255)
PANEL_BG    = (45,  45,  45)

ALGO_NAMES  = ['DFS', 'BFS', 'A*']
ALGO_COLORS = [(255, 140, 80), (80, 200, 120), (120, 160, 255)]


# ======================================================================
# Vẽ một ô
# ======================================================================
def draw_cell(surface, r, c, ox, oy, color):
    x = ox + c * CELL
    y = oy + r * CELL
    pygame.draw.rect(surface, color,
                     (x + WALL, y + WALL,
                      CELL - WALL * 2, CELL - WALL * 2))


# ======================================================================
# Vẽ tường của mê cung
# ======================================================================
def draw_maze_walls(surface, maze, ox, oy):
    """Vẽ tường cho một panel."""
    # Nền panel
    pygame.draw.rect(surface, PANEL_BG, (ox, oy, PANEL_W, PANEL_H))

    for r in range(1, maze.rows + 1):
        for c in range(1, maze.cols + 1):
            cell = maze.grid[(r, c)]
            x = ox + (c - 1) * CELL
            y = oy + (r - 1) * CELL

            # Tô ô
            pygame.draw.rect(surface, CELL_EMPTY,
                             (x + WALL, y + WALL,
                              CELL - WALL * 2, CELL - WALL * 2))

            # Tường Bắc
            if not cell['N']:
                pygame.draw.rect(surface, WALL_COLOR,
                                 (x, y, CELL, WALL))
            # Tường Nam
            if not cell['S']:
                pygame.draw.rect(surface, WALL_COLOR,
                                 (x, y + CELL - WALL, CELL, WALL))
            # Tường Tây
            if not cell['W']:
                pygame.draw.rect(surface, WALL_COLOR,
                                 (x, y, WALL, CELL))
            # Tường Đông
            if not cell['E']:
                pygame.draw.rect(surface, WALL_COLOR,
                                 (x + CELL - WALL, y, WALL, CELL))

    # Viền ngoài
    pygame.draw.rect(surface, WALL_COLOR, (ox, oy, PANEL_W, PANEL_H), WALL)


# ======================================================================
# Chuyển toạ độ maze → pixel
# ======================================================================
def cell_to_pixel(r, c, ox, oy):
    """Trả về góc trên-trái pixel của ô (r,c) trong panel."""
    return ox + (c - 1) * CELL, oy + (r - 1) * CELL


def draw_overlay(surface, r, c, ox, oy, color, alpha=180):
    """Vẽ ô màu bán trong suốt."""
    x, y = cell_to_pixel(r, c, ox, oy)
    s = pygame.Surface((CELL - WALL * 2, CELL - WALL * 2), pygame.SRCALPHA)
    s.fill((*color, alpha))
    surface.blit(s, (x + WALL, y + WALL))


# ======================================================================
# Vòng lặp hoạt ảnh chính
# ======================================================================
def animate(screen, clock, maze, results, offsets, font_title, font_stat):
    """
    Chạy hoạt ảnh song song cho 3 thuật toán.
    results  : list của 3 dict {'path', 'visited'}
    offsets  : list của 3 tuple (ox, oy) — vị trí góc trên-trái panel
    """
    start = maze.start()
    end   = maze.end()

    # Snapshot bề mặt nền (mê cung đã vẽ)
    base_surface = pygame.Surface((WIN_W, WIN_H))
    base_surface.fill(BG)

    # Vẽ thanh tiêu đề
    title = font_title.render(
        "So sánh thuật toán tìm đường — DFS | BFS | A*", True, TEXT_COLOR)
    base_surface.blit(title, (WIN_W // 2 - title.get_width() // 2, 15))

    for i, (ox, oy) in enumerate(offsets):
        draw_maze_walls(base_surface, maze, ox, oy)
        lbl = font_title.render(ALGO_NAMES[i], True, ALGO_COLORS[i])
        base_surface.blit(lbl, (ox + PANEL_W // 2 - lbl.get_width() // 2,
                                oy - 30))

    # Số bước tối đa
    max_steps = max(len(r['visited']) for r in results)
    step = 0
    done = False
    last_time = time.time()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                if event.key == pygame.K_SPACE:
                    return   # Tạo mê cung mới

        now = time.time()
        if not done and now - last_time >= ANIM_DELAY:
            step = min(step + 1, max_steps)
            last_time = now
            if step == max_steps:
                done = True

        # Vẽ lại
        screen.blit(base_surface, (0, 0))

        for i, (ox, oy) in enumerate(offsets):
            res = results[i]
            visited = res['visited']
            path    = res['path'] or []

            # Các ô đã duyệt
            for j in range(min(step, len(visited))):
                r, c = visited[j]
                draw_overlay(screen, r, c, ox, oy, CELL_VISIT, 160)

            # Đường đi (chỉ hiện khi đã duyệt xong)
            if step >= len(visited):
                for r, c in path:
                    draw_overlay(screen, r, c, ox, oy, CELL_PATH, 210)

            # Start & End
            draw_overlay(screen, *start, ox, oy, CELL_START, 255)
            draw_overlay(screen, *end,   ox, oy, CELL_END,   255)

        # Thanh thống kê
        stat_y = TOP_BAR + PANEL_H + 8
        for i, (ox, oy) in enumerate(offsets):
            res = results[i]
            n_visited = len(res['visited'])
            n_path    = len(res['path']) if res['path'] else 0
            cur_step  = min(step, n_visited)

            line1 = font_stat.render(
                f"Đã duyệt: {cur_step}/{n_visited} ô", True, ALGO_COLORS[i])
            line2 = font_stat.render(
                f"Đường đi: {n_path} bước", True, TEXT_COLOR)

            screen.blit(line1, (ox + 4, stat_y))
            screen.blit(line2, (ox + 4, stat_y + 28))

        hint = font_stat.render(
            "SPACE = mê cung mới   |   ESC = thoát", True, (130, 130, 130))
        screen.blit(hint, (WIN_W // 2 - hint.get_width() // 2,
                           stat_y + 58))

        pygame.display.flip()
        clock.tick(FPS)


# ======================================================================
# Main
# ======================================================================
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption("So sánh DFS / BFS / A* — Mê Cung")
    clock = pygame.time.Clock()

    # Font (fallback sang SysFont nếu không có file TTF)
    try:
        font_title = pygame.font.SysFont("segoeui", 22, bold=True)
        font_stat  = pygame.font.SysFont("segoeui", 18)
    except Exception:
        font_title = pygame.font.Font(None, 24)
        font_stat  = pygame.font.Font(None, 20)

    # Tính offsets cho 3 panel
    offsets = []
    for i in range(3):
        ox = PANEL_PAD + i * (PANEL_W + PANEL_PAD)
        oy = TOP_BAR
        offsets.append((ox, oy))

    while True:
        # Tạo mê cung mới
        seed = random.randint(0, 99999)
        maze = Maze(ROWS, COLS, seed=seed)
        st, en = maze.start(), maze.end()

        # Chạy 3 thuật toán
        results = [
            dfs(maze, st, en),
            bfs(maze, st, en),
            astar(maze, st, en),
        ]

        animate(screen, clock, maze, results, offsets, font_title, font_stat)


if __name__ == '__main__':
    main()
