def bfs(maze, start, end) -> dict:
    queue = deque([start])
    parent = {start: None}
    visited_order = []

    while queue:
        cur = queue.popleft()
        visited_order.append(cur)

        if cur == end:
            return {'path': _reconstruct(parent, start, end), 'visited': visited_order}

        for nb in maze.neighbors(*cur):
            if nb not in parent:
                parent[nb] = cur
                queue.append(nb)

    return {'path': None, 'visited': visited_order}
