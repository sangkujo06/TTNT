def dfs(maze, start, end) -> dict:
    stack = [start]
    parent = {start: None}
    visited_order = []

    while stack:
        cur = stack.pop()
        visited_order.append(cur)

        if cur == end:
            return {'path': _reconstruct(parent, start, end), 'visited': visited_order}

        for nb in maze.neighbors(*cur):
            if nb not in parent:
                parent[nb] = cur
                stack.append(nb)

    return {'path': None, 'visited': visited_order}
