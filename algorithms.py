import heapq
from collections import deque


# ======================================================================
# Hàm hỗ trợ chung
# ======================================================================

def _reconstruct(parent: dict, start, end) -> list:
    """Truy vết đường đi từ end về start qua dict parent."""
    path = []
    cur = end
    while cur is not None:
        path.append(cur)
        cur = parent[cur]
    path.reverse()
    return path if path[0] == start else None


def manhattan(a, b) -> int:
    """Khoảng cách Manhattan giữa hai ô."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


# ======================================================================
# DFS — Depth-First Search
# ======================================================================

def dfs(maze, start, end) -> dict:
    stack = [start]
    parent = {start: None}
    visited_order = []

    while stack:
        cur = stack.pop()
        visited_order.append(cur)

        if cur == end:
            return {
                'path': _reconstruct(parent, start, end),
                'visited': visited_order,
            }

        for nb in maze.neighbors(*cur):
            if nb not in parent:
                parent[nb] = cur
                stack.append(nb)

    return {'path': None, 'visited': visited_order}


# ======================================================================
# BFS — Breadth-First Search
# ======================================================================

def bfs(maze, start, end) -> dict:

    queue = deque([start])
    parent = {start: None}
    visited_order = []

    while queue:
        cur = queue.popleft()
        visited_order.append(cur)

        if cur == end:
            return {
                'path': _reconstruct(parent, start, end),
                'visited': visited_order,
            }

        for nb in maze.neighbors(*cur):
            if nb not in parent:
                parent[nb] = cur
                queue.append(nb)

    return {'path': None, 'visited': visited_order}


# ======================================================================
# A* — A-Star Search
# ======================================================================

def astar(maze, start, end) -> dict:

    open_list = []
    heapq.heappush(open_list, (manhattan(start, end), start))
    parent = {start: None}
    g = {start: 0}
    closed_set = set()
    visited_order = []

    while open_list:
        _, cur = heapq.heappop(open_list)

        if cur in closed_set:
            continue
        closed_set.add(cur)
        visited_order.append(cur)

        if cur == end:
            return {
                'path': _reconstruct(parent, start, end),
                'visited': visited_order,
            }

        for nb in maze.neighbors(*cur):
            if nb in closed_set:
                continue
            g_new = g[cur] + 1
            if nb not in g or g_new < g[nb]:
                g[nb] = g_new
                f_nb = g_new + manhattan(nb, end)
                parent[nb] = cur
                heapq.heappush(open_list, (f_nb, nb))

    return {'path': None, 'visited': visited_order}
