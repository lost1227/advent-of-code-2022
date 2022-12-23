from pathlib import Path

USE_SAMPLE_INPUT = False
in_path = Path.cwd() / 'input.txt'

sample_input = """
        ...#
        .#..
        #...
        ....
...#.......#
........#...
..#....#....
..........#.
        ...#....
        .....#..
        .#......
        ......#.

10R5L5R10L4R5L5
"""

if USE_SAMPLE_INPUT:
    input = sample_input.strip('\n')
else:
    with in_path.open("r") as inf:
        input = inf.read().strip('\n')

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

class Board:
    def __init__(self, grid: 'list[list[str]]'):
        self.grid = grid

    @staticmethod
    def from_str(instr: str) -> 'Board':
        split_str = instr.split('\n')
        height = len(split_str)
        width = max([len(s) for s in split_str])

        grid = [ [' ' for _ in range(width)] for _ in range(height)]
        for i, line in enumerate(split_str):
            for j, c in enumerate(line):
                grid[i][j] = c

        return Board(grid)

    def get_char(self, pos: Vector2) -> str:
        return self.grid[pos.y][pos.x]

    def get_size(self):
        return Vector2(len(self.grid[0]), len(self.grid))

    def __str__(self):
        return '\n'.join([''.join(row) for row in self.grid])

left_rotations = {
    Vector2(1, 0): Vector2(0, -1),
    Vector2(0, -1): Vector2(-1, 0),
    Vector2(-1, 0): Vector2(0, 1),
    Vector2(0, 1): Vector2(1, 0)
}

right_rotations = {
    Vector2(1, 0): Vector2(0, 1),
    Vector2(0, 1): Vector2(-1, 0),
    Vector2(-1, 0): Vector2(0, -1),
    Vector2(0, -1): Vector2(1, 0)
}

direction_markers = {
    Vector2(1, 0): '>',
    Vector2(0, -1): '^',
    Vector2(-1, 0): '<',
    Vector2(0, 1): 'v'
}

direction_ids = {
    Vector2(1, 0): 0,
    Vector2(0, -1): 3,
    Vector2(-1, 0): 2,
    Vector2(0, 1): 1
}

class StepBlocked(Exception):
    pass

class PathWalker:
    def __init__(self, board: Board):
        self.board = board

        start_x = -1
        for x, c in enumerate(board.grid[0]):
            if c == '.':
                start_x = x
                break

        self.pos = Vector2(start_x, 0)
        self.facing_dir = Vector2(1, 0)

        self.path = [[' ' for _ in range(len(board.grid[0]))] for _ in range(len(board.grid))]
        self._mark_pos()

    def _mark_pos(self):
        self.path[self.pos.y][self.pos.x] = direction_markers[self.facing_dir]

    def step(self):
        board_size = self.board.get_size()
        newpos = (self.pos + self.facing_dir) % board_size
        newpos_chr = self.board.get_char(newpos)
        while newpos_chr == ' ':
            newpos = (newpos + self.facing_dir) % board_size
            newpos_chr = self.board.get_char(newpos)

        if newpos_chr == '#':
            raise StepBlocked()

        assert newpos_chr == '.'

        self.pos = newpos

        self._mark_pos()

    def follow_path(self, path: str):
        pathparts = []
        curr_part = ''
        for c in path:
            try:
                int(c)
                curr_part += c
            except ValueError:
                pathparts.append(curr_part)
                curr_part = ''
                pathparts.append(c)
        if len(curr_part) > 0:
            pathparts.append(curr_part)

        for part in pathparts:
            if part == 'L':
                self.facing_dir = left_rotations[self.facing_dir]
                self._mark_pos()
            elif part == 'R':
                self.facing_dir = right_rotations[self.facing_dir]
                self._mark_pos()
            else:
                steps = int(part)
                try:
                    for _ in range(steps):
                        self.step()
                except StepBlocked:
                    pass
                if USE_SAMPLE_INPUT:
                    print(self)
                    print()
    def __str__(self):
        out = ""
        for i, row in enumerate(self.path):
            for j, c in enumerate(row):
                if i == self.pos.y and j == self.pos.x:
                    out += "\u001b[31m"
                if c == ' ':
                    out += self.board.grid[i][j]
                else:
                    out += c
                if i == self.pos.y and j == self.pos.x:
                    out += "\u001b[0m"
            out += '\n'
        return out

board, path = input.split('\n\n')
board = Board.from_str(board)
walker = PathWalker(board)

# path = "10"

walker.follow_path(path)
print(walker)

password = (1000 * (walker.pos.y+1)) + (4 * (walker.pos.x+1)) + direction_ids[walker.facing_dir]
print("Part 1:", password)

# PART 2
print('\n\n')

class Direction:
    LEFT = Vector2(-1, 0)
    RIGHT = Vector2(1, 0)
    UP = Vector2(0, -1)
    DOWN = Vector2(0, 1)

direction_opposites = {
    Direction.LEFT: Direction.RIGHT,
    Direction.RIGHT: Direction.LEFT,
    Direction.UP: Direction.DOWN,
    Direction.DOWN: Direction.UP
}

def in_range(rangeStart: Vector2, rangeEnd: Vector2, test: Vector2) -> bool:
    if rangeStart.x == rangeEnd.x:
        if test.x != rangeStart.x:
            return False
        if rangeStart.y > rangeEnd.y:
            return test.y <= rangeStart.y and test.y > rangeEnd.y
        else:
            return test.y >= rangeStart.y and test.y < rangeEnd.y
    else:
        assert rangeStart.y == rangeEnd.y
        if test.y != rangeStart.y:
            return False
        if rangeStart.x > rangeEnd.x:
            return test.x <= rangeStart.x and test.x > rangeEnd.x
        else:
            return test.x >= rangeStart.x and test.x < rangeEnd.x

class CubeEdge:
    def __init__(self, origin: Vector2, edge_length: int, cube_direction: Vector2):
        if cube_direction in (Direction.DOWN, Direction.RIGHT):
            origin -= cube_direction
        if cube_direction in (Direction.UP, Direction.RIGHT):
            origin += left_rotations[cube_direction]
        self.origin = origin
        self.edge_length = edge_length
        self.cube_direction = cube_direction
        self.end = self.origin_dist_to_point(self.edge_length)

        assert self.origin.x == self.end.x or self.origin.y == self.end.y

        assert cube_direction in (Direction.LEFT, Direction.RIGHT, Direction.UP, Direction.DOWN)

    def point_in_edge(self, test_point: Vector2) -> bool:
        return in_range(self.origin, self.end, test_point)

    def facing_towards_edge(self, facing_direction: Vector2) -> bool:
        return self.cube_direction == direction_opposites[facing_direction]

    def point_to_origin_dist(self, point: Vector2) -> int:
        assert self.point_in_edge(point)
        if self.cube_direction in (Direction.UP, Direction.DOWN):
            return abs(point.x - self.origin.x)
        else:
            return abs(point.y - self.origin.y)

    def origin_dist_to_point(self, origin_dist: int) -> Vector2:
        if self.cube_direction == Direction.DOWN:
            return Vector2(self.origin.x + origin_dist, self.origin.y)
        if self.cube_direction == Direction.RIGHT:
            return Vector2(self.origin.x, self.origin.y - origin_dist)
        if self.cube_direction == Direction.LEFT:
            return Vector2(self.origin.x, self.origin.y + origin_dist)
        if self.cube_direction == Direction.UP:
            return Vector2(self.origin.x - origin_dist, self.origin.y)

        assert False

EDGE_LENGTH = 0
edge_pairs: 'list[tuple[CubeEdge, CubeEdge]]' = []

if USE_SAMPLE_INPUT:
    EDGE_LENGTH = 4
    edge_pairs = [
        (CubeEdge(Vector2(8,0), EDGE_LENGTH, Direction.DOWN), CubeEdge(Vector2(0, 4), EDGE_LENGTH, Direction.DOWN)), # PINK
        (CubeEdge(Vector2(8, 4), EDGE_LENGTH, Direction.RIGHT), CubeEdge(Vector2(4, 4), EDGE_LENGTH, Direction.DOWN)), # BROWN
        (CubeEdge(Vector2(12, 0), EDGE_LENGTH, Direction.LEFT), CubeEdge(Vector2(16, 8), EDGE_LENGTH, Direction.LEFT)), # RED
        (CubeEdge(Vector2(12, 4), EDGE_LENGTH, Direction.LEFT), CubeEdge(Vector2(12, 8), EDGE_LENGTH, Direction.DOWN)), # CYAN
        (CubeEdge(Vector2(4, 8), EDGE_LENGTH, Direction.UP), CubeEdge(Vector2(12, 12), EDGE_LENGTH, Direction.UP)), # GREEN
        (CubeEdge(Vector2(0, 8), EDGE_LENGTH, Direction.RIGHT), CubeEdge(Vector2(16, 12), EDGE_LENGTH, Direction.UP)), # PURPLE
        (CubeEdge(Vector2(8, 8), EDGE_LENGTH, Direction.UP), CubeEdge(Vector2(8, 12), EDGE_LENGTH, Direction.RIGHT)) # BLUE
    ]
else:
    EDGE_LENGTH = 50
    edge_pairs = [
        (CubeEdge(Vector2(50, 0), EDGE_LENGTH, Direction.DOWN), CubeEdge(Vector2(0, 200), EDGE_LENGTH, Direction.RIGHT)), # GREEN
        (CubeEdge(Vector2(100, 0), EDGE_LENGTH, Direction.DOWN), CubeEdge(Vector2(50, 200), EDGE_LENGTH, Direction.UP)), # PURPLE
        (CubeEdge(Vector2(50, 50), EDGE_LENGTH, Direction.RIGHT), CubeEdge(Vector2(0, 150), EDGE_LENGTH, Direction.RIGHT)), # PINK
        (CubeEdge(Vector2(150, 0), EDGE_LENGTH, Direction.LEFT), CubeEdge(Vector2(100, 100), EDGE_LENGTH, Direction.LEFT)), # CYAN
        (CubeEdge(Vector2(150, 50), EDGE_LENGTH, Direction.UP), CubeEdge(Vector2(100, 50), EDGE_LENGTH, Direction.LEFT)), # BLUE
        (CubeEdge(Vector2(50, 100), EDGE_LENGTH, Direction.RIGHT), CubeEdge(Vector2(0, 100), EDGE_LENGTH, Direction.DOWN)), # RED
        (CubeEdge(Vector2(100, 150), EDGE_LENGTH, Direction.UP), CubeEdge(Vector2(50, 150), EDGE_LENGTH, Direction.LEFT)), # BROWN
    ]

edge_pairs = edge_pairs + [(e2, e1) for e1, e2 in edge_pairs]

class PathWalker2(PathWalker):
    def step(self):
        newpos = (self.pos + self.facing_dir)
        newdir = self.facing_dir

        for edge1, edge2 in edge_pairs:
            if edge1.point_in_edge(newpos) and edge1.facing_towards_edge(newdir):
                edge_pos = edge1.point_to_origin_dist(newpos)
                assert edge_pos < EDGE_LENGTH
                newpos = edge2.origin_dist_to_point(EDGE_LENGTH - 1 - edge_pos) + edge2.cube_direction
                newdir = edge2.cube_direction
                break

        newpos_chr = self.board.get_char(newpos)
        if newpos_chr == '#':
            raise StepBlocked()

        assert newpos_chr == '.'

        self.pos = newpos
        self.facing_dir = newdir

        self._mark_pos()

board, path = input.split('\n\n')
board = Board.from_str(board)
walker = PathWalker2(board)

walker.follow_path(path)
print(walker)


password = (1000 * (walker.pos.y+1)) + (4 * (walker.pos.x+1)) + direction_ids[walker.facing_dir]
print("Part 2:", password)
