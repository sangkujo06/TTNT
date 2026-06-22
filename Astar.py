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
