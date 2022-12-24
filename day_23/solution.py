from pathlib import Path

USE_SAMPLE_INPUT = False
in_path = Path.cwd() / 'input.txt'

sample_input = """
....#..
..###.#
#...#.#
.#...##
#.###..
##.#.##
.#..#..
"""

if USE_SAMPLE_INPUT:
    input = sample_input.strip()
else:
    with in_path.open("r") as inf:
        input = inf.read().strip()


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

class Direction:
    N = Vector2(0, -1)
    NE = Vector2(1, -1)
    E = Vector2(1, 0)
    SE = Vector2(1, 1)
    S = Vector2(0, 1)
    SW = Vector2(-1, 1)
    W = Vector2(-1, 0)
    NW = Vector2(-1, -1)

    @staticmethod
    def all():
        return (Direction.N, Direction.NE, Direction.E, Direction.SE, Direction.S, Direction.SW, Direction.W, Direction.NW)

class Step:
    def __init__(self, result: Vector2, checks: 'set(Vector2)'):
        self.result = result
        self.checks = checks

class ElfDone(Exception):
    pass

class Board:
    def __init__(self, elves: 'set[Vector2]'):
        self.elves = elves

        self.steps = [
            Step(Direction.N, set([Direction.N, Direction.NE, Direction.NW])),
            Step(Direction.S, set([Direction.S, Direction.SE, Direction.SW])),
            Step(Direction.W, set([Direction.W, Direction.NW, Direction.SW])),
            Step(Direction.E, set([Direction.E, Direction.NE, Direction.SE]))
        ]
        self.first_step_idx = 0
        self.step_count = 0

    @staticmethod
    def from_str(input_str: str) -> 'Board':
        split_str = input_str.split('\n')
        elves = set()
        for y, row in enumerate(split_str):
            for x, c in enumerate(row):
                if c == '#':
                    elves.add(Vector2(x, y))

        return Board(elves)

    def step(self) -> bool:
        # FIRST HALF
        proposed_elf_positions: 'dict[Vector2, set[Vector2]]' = {}
        for elf in self.elves:
            try:
                no_adjacent_elves = True
                for delta in Direction.all():
                    if elf + delta in self.elves:
                        no_adjacent_elves = False
                        break
                if no_adjacent_elves:
                    raise ElfDone()

                for i in range(0, 4):
                    curr_step_idx = (self.first_step_idx + i) % len(self.steps)
                    step = self.steps[curr_step_idx]
                    step_is_valid = True
                    for delta in step.checks:
                        newpos = elf + delta
                        if newpos in self.elves:
                            step_is_valid = False
                            break
                    if step_is_valid:
                        respos = elf + step.result
                        if respos not in proposed_elf_positions:
                            proposed_elf_positions[respos] = set([elf])
                        else:
                            proposed_elf_positions[respos].add(elf)
                        raise ElfDone()
            except ElfDone:
                pass

        # SECOND HALF
        elf_did_move = False
        for position, elves in proposed_elf_positions.items():
            if len(elves) == 1:
                elf_did_move = True
                elf = next(iter(elves))
                self.elves.remove(elf)
                self.elves.add(position)

        self.first_step_idx = (self.first_step_idx + 1) % len(self.steps)

        self.step_count += 1

        return elf_did_move

    @property
    def bounds(self) -> 'tuple[Vector2, Vector2]':
        minx = maxx = 0
        miny = maxy = 0

        for elf in self.elves:
            minx = min(minx, elf.x)
            miny = min(miny, elf.y)
            maxx = max(maxx, elf.x)
            maxy = max(maxy, elf.y)

        origin = Vector2(minx, miny)
        size = Vector2(maxx - minx + 1, maxy - miny + 1)

        return (origin, size)

    def empty_tile_count(self):
        _, size = self.bounds
        count = size.y * size.x - len(self.elves)
        return count

    def __str__(self):
        origin, size = self.bounds

        # origin -= Vector2(3, 3)
        # size += Vector2(7, 7)

        grid = [ ['.' for _ in range(size.x)] for _ in range(size.y)]

        for elf in self.elves:
            pos = elf - origin
            grid[pos.y][pos.x] = '#'

        out = ""
        if origin.x <= 0:
            out += (' ' * (-origin.x) + '0' + '\n')
        for i, row in enumerate(grid):
            if origin.y + i == 0:
                out += "0 "
            else:
                out += "  "
            out += ''.join(row)
            out += '\n'
        return out

board = Board.from_str(input)

print("== Initial State ==")
print(board)
print()

for i in range(10):
    board.step()
    print(f"== End of Round {i+1} ==")
    print(board)
    print()

print("Part 1", board.empty_tile_count())

# PART 2
print('\n\n')
while board.step():
    pass

print(board)

print("Part 2", board.step_count)
