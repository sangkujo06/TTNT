def dfs(matrix, st, en):

    r = len(matrix)
    c = len(matrix[0])
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    stack = [st]
    parent = {st: None}

    while stack:
        cur = stack.pop()

        if cur == en:
            path = []
            while cur is not None:
                path.append(cur)
                cur = parent[cur]
            return path[::-1]

        for dx, dy in dirs:
            nb = (cur[0] + dx, cur[1] + dy)
            if (0 <= nb[0] < r and 0 <= nb[1] < c
                    and matrix[nb[0]][nb[1]] == 0
                    and nb not in parent):
                parent[nb] = cur
                stack.append(nb)

    return None