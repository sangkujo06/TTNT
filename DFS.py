def dfs(start, goal, matrix):
    stack = [start]
    visited = set()
    parent = {start: None}

    while stack:
        state = stack.pop()
        if state in visited:
            continue
        visited.add(state)

        if state == goal:
            return reconstruct_path(parent, start, goal), visited

        for neighbor in get_neighbors(state, matrix):
            if neighbor not in visited and neighbor not in parent:
                parent[neighbor] = state
                stack.append(neighbor)

    return None, visited


def reconstruct_path(parent, start, goal):
    path = []
    cur = goal
    while cur is not None:
        path.append(cur)
        cur = parent[cur]
    path.reverse()
    return path
