import heapq


def get_neighbors(state , matrix):
    x, y = state
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    neighbors = []
    for dx, dy in dirs:
        nx = x + dx
        ny = y + dy
        if (0 <= nx < len(matrix)
                and 0 <= ny < len(matrix[0])
                and matrix[nx][ny] == 0):
            neighbors.append((nx, ny))
    return neighbors


def heuristic(a, b):
    # khoảng cách Manhattan
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(start, goal, get_neighbors):
    open_set = []
    heapq.heappush(open_set, (0, start))
    parent = {start: None}
    g_score = {start: 0}
    while open_set:
        _, current = heapq.heappop(open_set)
        if current == goal:
            path = []
            while current is not None:
                path.insert(0, current)
                current = parent[current]
            return path
        for neighbor in get_neighbors(current,matrix):
            tentative_g = g_score[current] + 1
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                g_score[neighbor] = tentative_g
                f_score = tentative_g + heuristic(neighbor, goal)
                heapq.heappush(open_set, (f_score, neighbor))
                parent[neighbor] = current
    return None
