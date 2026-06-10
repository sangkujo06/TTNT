def get_neighbors(state,matrix):
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


def dfs(start, goal, get_neighbors):
    to_visit = [start]
    discover = set([start])
    parent = {start: None}
    while to_visit:
        vertex = to_visit.pop()
        if vertex == goal:
            path = []
            while vertex is not None:
                path.insert(0, vertex)
                vertex = parent[vertex]
            return path
        for neighbor in get_neighbors(vertex,matrix):
            if neighbor not in discover:
                discover.add(neighbor)
                parent[neighbor] = vertex
                to_visit.append(neighbor)
    return None
