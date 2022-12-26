from pathlib import Path
import heapq

USE_SAMPLE_INPUT = False
in_path = Path.cwd() / 'input.txt'

sample_input_1 = """
#.#####
#.....#
#>....#
#.....#
#...v.#
#.....#
#####.#
"""

sample_input_2 = """
#.######
#>>.<^<#
#.<..<<#
#>v.><>#
#<^v^^>#
######.#
"""

if USE_SAMPLE_INPUT:
    input = sample_input_2.strip()
else:
    with in_path.open("r") as inf:
        input = inf.read().strip()

def lcm(a, b):
    curr = max(a, b)
    while True:
        if curr % a == 0 and curr % b == 0:
            return curr
        curr += 1

class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return f'({self.x}, {self.y})'

    def __repr__(self):
        return f'Vector2({self.x}, {self.y})'

    def __eq__(self, other):
        if not isinstance(other, Vector2):
            return False

        return other.x == self.x and other.y == self.y

    def __hash__(self):
        return (self.x, self.y).__hash__()

    def __add__(self, other):
        if not isinstance(other, Vector2):
            raise TypeError(f"Can only add Vector2 (not \"{ other.__class__.__name__ }\") to Vector2")
        return Vector2(self.x + other.x, self.y + other.y)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if not isinstance(other, Vector2):
            raise TypeError(f"Can only subtract Vector2 (not \"{ other.__class__.__name__ }\") from Vector2")
        return Vector2(self.x - other.x, self.y - other.y)

    def __rsub__(self, other):
        return self.__sub__(other)

    def __mod__(self, other):
        if not isinstance(other, Vector2):
            raise TypeError(f"Can only modulo Vector2 (not \"{ other.__class__.__name__ }\") from Vector2")
        return Vector2(self.x % other.x, self.y % other.y)

    def __mul__(self, other):
        if not isinstance(other, int):
            raise TypeError(f"Can only multiply int (not \"{ other.__class__.__name__ }\") with Vector2")
        return Vector2(self.x * other, self.y * other)

    def __rmul__(self, other):
        return self.__mul__(other)

class Blizzard:
    def __init__(self, initial_position: Vector2, direction: Vector2):
        self.initial_position = initial_position
        self.direction = direction

dirs = {
    '^': Vector2(0, -1),
    'v': Vector2(0, 1),
    '<': Vector2(-1, 0),
    '>': Vector2(1, 0)
}

dirstrs = {
    Vector2(0, -1): '^',
    Vector2(0, 1): 'v',
    Vector2(-1, 0): '<',
    Vector2(1, 0): '>'
}

class Valley:
    def __init__(self, blizzards: 'list[Blizzard]', size: Vector2):
        self.blizzards = blizzards
        self.size = size

        self.__calculate_blizzards()

    @staticmethod
    def from_str(inputstr: str) -> 'Valley':
        valley_str = [ s[1:-1] for s in inputstr.split('\n')][1:-1]

        blizzards = []

        for y, line in enumerate(valley_str):
            for x, c in enumerate(line):
                if c in dirs:
                    blizzards.append(Blizzard(Vector2(x, y), dirs[c]))

        return Valley(blizzards, Vector2(len(valley_str[0]), len(valley_str)))

    def __blizzards_at_t(self, t):
        grid = [ ['.' for _ in range(self.size.x)] for _ in range(self.size.y)]
        for blizzard in self.blizzards:
            pos = (blizzard.initial_position + (blizzard.direction * t)) % self.size
            if grid[pos.y][pos.x] == '.':
                grid[pos.y][pos.x] = dirstrs[blizzard.direction]
            elif grid[pos.y][pos.x] in "^v><":
                grid[pos.y][pos.x] = "2"
            else:
                grid[pos.y][pos.x] = str(int(grid[pos.y][pos.x]) + 1)

        return grid


    def __calculate_blizzards(self):
        configuration_count = lcm(self.size.x, self.size.y)
        self.blizzards_in_time = []
        for t in range(configuration_count):
            self.blizzards_in_time.append(self.__blizzards_at_t(t))

    def point_in_blizzard(self, point: Vector2, when: int) -> bool:
        if point.x < 0 or point.x >= self.size.x or point.y < 0 or point.y >= self.size.y:
            return False
        return self.blizzards_in_time[when % len(self.blizzards_in_time)][point.y][point.x] != '.'

    def str_at_t(self, t: int) -> str:
        return "\n".join([''.join(s) for s in self.blizzards_in_time[t % len(self.blizzards_in_time)]])

    def __str__(self):
        return self.str_at_t(0)

class AStarNode:
    def __init__(self, prev: 'AStarNode', pos: Vector2, when: int, total_cost: int):
        self.prev = prev
        self.pos = pos
        self.when = when
        self.total_cost = total_cost

    def __lt__(self, other):
        assert isinstance(other, AStarNode)
        return self.total_cost < other.total_cost

    def __eq__(self, other):
        if not isinstance(other, AStarNode):
            return False
        return self.pos == other.pos and self.when == other.when

    def __hash__(self):
        return (self.pos, self.when).__hash__()

def estimate_cost(at: Vector2, goal: Vector2) -> float:
    return ( ((goal.x - at.x)**2) + ((goal.y - at.y)**2) )**0.5

v = Valley.from_str(input)
for i in range(10):
    print(f"== Minute {i} ==")
    print(v.str_at_t(i))
    print()

def find_path(from_pt: Vector2, to_pt: Vector2, start_t: int = 0) -> AStarNode:
    open_set = [AStarNode(None, from_pt, start_t, start_t + estimate_cost(Vector2(0, -1), to_pt))]
    seen = set()

    dirs = [Vector2(0, -1), Vector2(0, 1), Vector2(-1, 0), Vector2(1, 0), Vector2(0, 0)]

    solution = None

    extra_spots = set([from_pt, to_pt])

    while len(open_set) > 0:
        curr = heapq.heappop(open_set)
        if curr.pos == to_pt:
            solution = curr
            break
        for dir in dirs:
            next = AStarNode(curr, curr.pos + dir, curr.when + 1, curr.when + 1 + estimate_cost(curr.pos + dir, to_pt))
            if next in seen:
                continue
            seen.add(next)
            if v.point_in_blizzard(next.pos, next.when):
                continue
            if next.pos not in extra_spots:
                if next.pos.x < 0 or next.pos.x >= v.size.x or next.pos.y < 0 or next.pos.y >= v.size.y:
                    continue
            heapq.heappush(open_set, next)

    return solution

solution = find_path(Vector2(0, -1), Vector2(v.size.x - 1, v.size.y))

if USE_SAMPLE_INPUT:
    path = []
    curr = solution
    while curr is not None:
        path.append(curr)
        curr = curr.prev

    for node in path[::-1]:
        print(f"== Minute {node.when} ==")
        valley_at_t = v.blizzards_in_time[node.when % len(v.blizzards_in_time)]
        for y, row in enumerate(valley_at_t):
            for x, c in enumerate(row):
                if Vector2(x, y) == node.pos:
                    print("E", end="")
                else:
                    print(c, end="")
            print()

print("Part 1:", solution.when)

## PART 2
print('\n\n')

start = Vector2(0, -1)
end = Vector2(v.size.x - 1, v.size.y)

cross1 = solution
print(f"cross1: t=0 to t={cross1.when}")
cross2 = find_path(end, start, start_t=cross1.when)
print(f"cross2: t={cross1.when} to t={cross2.when}")
cross3 = find_path(start, end, start_t=cross2.when)
print(f"cross3: t={cross2.when} to t={cross3.when}")
print()

print("Part 2:", cross3.when)
