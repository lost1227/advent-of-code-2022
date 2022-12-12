from pathlib import Path
import heapq
import time

USE_SAMPLE_INPUT = False
in_path = Path.cwd() / 'input.txt'

sample_input = """
Sabqponm
abcryxxl
accszExk
acctuvwj
abdefghi
""".strip()

if USE_SAMPLE_INPUT:
    input = sample_input.split('\n')
else:
    with in_path.open("r") as inf:
        input = inf.read().strip().split('\n')

class GridNode:
    def __init__(self, height, gridPos):
        self.height = height
        self.gridPos = gridPos

    def set_reachable_nodes(self, nodes):
        self.neighbors = nodes

    def __eq__(self, other):
        if not isinstance(other, GridNode):
            return False
        return self.gridPos == other.gridPos

    def __repr__(self):
        return f"GridNode(height={self.height.__repr__()}, gridPos={self.gridPos.__repr__()})"

class AStarNode:
    def __init__(self, gridNode, prev, pathlen, totalcost):
        self.gridNode = gridNode
        self.prev = prev
        self.pathlen = pathlen
        self.totalcost = totalcost

    def __lt__(self, other):
        return self.totalcost < other.totalcost

start = None
goal = None

grid = []
for y, row in enumerate(input):
    curr = []
    for x, c in enumerate(row):
        if c == 'E':
            goal = GridNode(ord('z') - ord('a'), (x, y))
            curr.append(goal)
        elif c == 'S':
            start = GridNode(0, (x, y))
            curr.append(start)
        else:
            curr.append(GridNode(ord(c) - ord('a'), (x, y)))
    grid.append(curr)

for y, row in enumerate(grid):
    for x, node in enumerate(row):
        adjacent_nodes = []
        if y > 0:
            adjacent_nodes.append(grid[y-1][x])
        if y < len(grid)-1:
            adjacent_nodes.append(grid[y+1][x])
        if x > 0:
            adjacent_nodes.append(grid[y][x-1])
        if x < len(row)-1:
            adjacent_nodes.append(grid[y][x+1])

        reachable_nodes = []
        for candidate_node in adjacent_nodes:
            if candidate_node.height <= node.height + 1:
                reachable_nodes.append(candidate_node)
        node.set_reachable_nodes(reachable_nodes)

def estimate_cost(node) -> float:
    return ((node.gridPos[0] - goal.gridPos[0])**2 + (node.gridPos[1] - goal.gridPos[1])**2)**0.5

def get_dir_chr(fromPoint, toPoint):
    assert (fromPoint[0] == toPoint[0]) != (fromPoint[1] == toPoint[1])

    if fromPoint[0] == toPoint[0]:
        if fromPoint[1] < toPoint[1]:
            return 'V'
        else:
            return '^'
    else:
        if fromPoint[0] < toPoint[0]:
            return '>'
        else:
            return '<'

should_clear = False

def plot_progress(curr, openset, seen):
    global should_clear
    time.sleep(0.001)
    if should_clear:
        for _ in range(len(grid)):
            print("\u001b[1F\u001b[2K", end="")
    else:
        should_clear = True

    output = [ ['.' for _ in row] for row in grid]
    for x,y in seen:
        output[y][x] = 'X'
    for node in openset:
        output[node.gridNode.gridPos[1]][node.gridNode.gridPos[0]] = '?'

    output[curr.gridNode.gridPos[1]][curr.gridNode.gridPos[0]] = '!'

    # while curr.prev is not None:
    #     char = get_dir_chr(curr.prev.gridNode.gridPos, curr.gridNode.gridPos)
    #     output[curr.prev.gridNode.gridPos[1]][curr.prev.gridNode.gridPos[0]] = char
    #     curr = curr.prev

    for row in output:
        print(''.join(row))

def path_to_goal(start, plot=False):
    if not isinstance(start, list):
        start = [start]
    openset = [AStarNode(s, None, 0, estimate_cost(s)) for s in start]
    seen = set()

    path = []

    while len(openset) > 0:
        curr = heapq.heappop(openset)
        if plot:
            plot_progress(curr, openset, seen)

        if curr.gridNode == goal:
            while curr is not None:
                path.append(curr.gridNode)
                curr = curr.prev
            path.reverse()
            return path

        for gridNode in curr.gridNode.neighbors:
            if gridNode.gridPos in seen:
                continue
            seen.add(gridNode.gridPos)
            stepCost = 1
            newNode = AStarNode(gridNode, curr, curr.pathlen + 1, curr.pathlen + stepCost + estimate_cost(gridNode))
            heapq.heappush(openset, newNode)

    return None

def plot_path(path):
    output = [ ['.' for _ in row] for row in grid]
    for i in range(len(path) - 1):
        curr = path[i]
        next = path[i+1]

        output[curr.gridPos[1]][curr.gridPos[0]] = get_dir_chr(curr.gridPos, next.gridPos)

    output[goal.gridPos[1]][goal.gridPos[0]] = 'E'

    for row in output:
        print(''.join(row))

path = path_to_goal(start)
plot_path(path)

print("Part 1:", len(path)-1)

# PART 2

starts = []
for row in grid:
    for node in row:
        if node.height == 0:
            starts.append(node)

path = path_to_goal(starts)

plot_path(path)

print("Part 2:", len(path) - 1)
