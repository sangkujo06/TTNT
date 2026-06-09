import heapq

def kc(a, b):
    # Khoảng cách Manhatta
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def tim_duong(matrix, st, en):
    r = len(matrix)
    c = len(matrix[0])

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    open_set = []
    heapq.heappush(open_set, (0, st))
    parent = {}
    g = {st: 0}
    f = {st: kc(st, en)}

    while open_set:
        _, cur = heapq.heappop(open_set)
        if cur == en:
            path = []
            while cur in parent:
                path.append(cur)
                cur = parent[cur]
            path.append(st)
            return path[::-1]

        for dx, dy in dirs:
            nb = (cur[0] + dx, cur[1] + dy)
            if 0 <= nb[0] < r and 0 <= nb[1] < c and matrix[nb[0]][nb[1]] == 0:
                tmp_g = g[cur] + 1
                if nb not in g or tmp_g < g[nb]:
                    parent[nb] = cur
                    g[nb] = tmp_g
                    f[nb] = tmp_g + kc(nb, en)
                    heapq.heappush(open_set, (f[nb], nb))
    return None