from pathlib import Path
import itertools
from queue import SimpleQueue

from tqdm import trange, tqdm

USE_SAMPLE_INPUT = False
in_path = Path.cwd() / 'input.txt'

if USE_SAMPLE_INPUT:
    input = ">>><<><>><<<>><>>><<<>>><<<><<<>><>><<>>"
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


class Block:
    def __init__(self, points: 'list[Vector2]'):
        self.points = points
        self.__normalize()

    def __normalize(self):
        maxx = minx = self.points[0].x
        maxy = miny = self.points[0].y
        for point in self.points:
            maxx = max(maxx, point.x)
            minx = min(minx, point.x)
            maxy = max(maxy, point.y)
            miny = min(miny, point.y)

        origin = Vector2(minx, maxy)
        self.points = [point - origin for point in self.points]

        self.size = Vector2(maxx - minx + 1, maxy - miny + 1)

    @staticmethod
    def from_str(in_str: str) -> 'Block':
        points: 'list[Vector2]' = []
        splitstr = in_str.split('\n')
        for r, line in enumerate(splitstr):
            y = len(splitstr) - r - 1
            for x, c in enumerate(line):
                if c == '#':
                    points.append(Vector2(x, y))
        return Block(points)

    def __str__(self):
        grid = [ ["." for _ in range(self.size.x)] for _ in range(self.size.y)]
        for point in self.points:
            grid[-point.y][point.x] = '#'
        return '\n'.join([''.join(row) for row in grid])



class Chamber:
    def __init__(self, jet_pattern: str, width: int = 7):
        self.width = width
        self.jet_pattern = jet_pattern
        self.next_jet_idx = 0
        self.filled_points: 'set(Vector2)' = set()
        self.correction = 0
        self.highest_y = -1

    def __point_collision(self, point) -> bool:
        if point in self.filled_points:
            return True
        if point.x < 0 or point.x >= self.width:
            return True
        if point.y < 0:
            return True
        return False

    def __check_collision(self, block: Block, pos: Vector2) -> bool:
        block_points = [point + pos for point in block.points]
        for point in block_points:
            if self.__point_collision(point):
                return True
        return False

    def simulate_block(self, block: Block):
        self.__trim()
        block_pos = Vector2(2, self.highest_y + block.size.y + 3)
        assert not self.__check_collision(block, block_pos)
        #self.__print_progress(block, block_pos)
        while True:
            jet = self.jet_pattern[self.next_jet_idx]
            self.next_jet_idx = (self.next_jet_idx + 1) % len(self.jet_pattern)
            if jet == '<':
                try_pos = block_pos + Vector2(-1, 0)
            else:
                assert jet == '>'
                try_pos = block_pos + Vector2(1, 0)
            if not self.__check_collision(block, try_pos):
                block_pos = try_pos

            #self.__print_progress(block, block_pos)

            try_pos = block_pos + Vector2(0, -1)
            if self.__check_collision(block, try_pos):
                break
            block_pos = try_pos

            #self.__print_progress(block, block_pos)

        self.highest_y = max(self.highest_y, block_pos.y)
        for point in block.points:
            point += block_pos
            assert not point in self.filled_points
            self.filled_points.add(point)

        #self.__trim()

    def __trim(self):
        seen = set()
        to_visit = SimpleQueue()
        to_visit.put(Vector2(0, self.highest_y + 1))

        min_y = self.highest_y + 1

        while not to_visit.empty():
            curr = to_visit.get()
            if self.__point_collision(curr):
                min_y = min(min_y, curr.y)
                continue

            for dir in (Vector2(0, -1), Vector2(-1, 0), Vector2(1, 0)):
                next_point = curr + dir
                if next_point not in seen:
                    seen.add(next_point)
                    to_visit.put(next_point)

        new_floor = min_y + 1
        if new_floor <= 0:
            return
        #print("\n\n=============================")
        #print("Trimming", new_floor)
        #print(self)
        #print("\n")

        self.correction += new_floor
        trim = Vector2(0, new_floor)
        self.filled_points = set([point - trim for point in self.filled_points if point.y >= new_floor])
        self.highest_y -= new_floor

        #print(self)


    def __print_progress(self, falling_block, block_pos):
        max_height = max(self.highest_y, block_pos.y)
        grid = [ [ '.' for _ in range(self.width)] for _ in range(max_height+1)]

        for point in self.filled_points:
            grid[max_height - point.y][point.x] = '#'

        for point in falling_block.points:
            point += block_pos
            grid[max_height - point.y][point.x] = '@'

        for row in grid:
            print("|" + "".join(row) + "|")

        print("+" + ("-" * self.width) + "+")
        print()

    def max_height(self):
        return self.correction + self.highest_y + 1

    def __str__(self):
        out = ''
        for y in range(self.highest_y, -1, -1):
            out += '|'
            for x in range(self.width):
                if Vector2(x, y) in self.filled_points:
                    out += '#'
                else:
                    out += '.'
            out += '|\n'
        out += '+' + ('-' * self.width) + '+'
        out += f"\nMax height: {self.max_height()}"
        return out

chamber = Chamber(input)

block_strs = """
####

.#.
###
.#.

..#
..#
###

#
#
#
#

##
##
""".strip().split("\n\n")

blocks = [Block.from_str(bstr) for bstr in block_strs]

# for block in blocks:
#     print(block)
#     print("===")
# exit()

block_repeat = itertools.cycle(blocks)
for _ in trange(2022):
    block = next(block_repeat)
    chamber.simulate_block(block)
    #print(chamber)
    #print("====================\n")

print("Part 1", chamber.max_height())

print("\n\n")

# PART 2

class ChamberState:
    def __init__(self, block_idx: int, jet_idx: int, filled_points: 'frozenset[Vector2]'):
        self.block_idx = block_idx
        self.jet_idx = jet_idx
        self.filled_points = filled_points

    def __eq__(self, other):
        if not isinstance(other, ChamberState):
            return False
        return other.block_idx == self.block_idx and other.jet_idx == self.jet_idx and other.filled_points == self.filled_points

    def __hash__(self):
        return (self.block_idx, self.jet_idx, self.filled_points).__hash__()

def simulate_without_cycles(num_iter):
    chamber = Chamber(input)
    block_repeat = itertools.cycle(blocks)
    for _ in range(num_iter):
        block = next(block_repeat)
        chamber.simulate_block(block)
    return chamber.max_height()

def simulate_with_cycles(num_iter):
    chamber = Chamber(input)
    next_block_idx = 0

    saved_states: 'dict[ChamberState, tuple[int, int]]' = {}

    found_cycle = False

    block_iter = 0
    while block_iter < num_iter:
        block = blocks[next_block_idx]
        next_block_idx = (next_block_idx + 1) % len(blocks)

        chamber.simulate_block(block)
        if not found_cycle:
            state = ChamberState(next_block_idx, chamber.next_jet_idx, frozenset(chamber.filled_points))
            if state in saved_states:
                found_cycle = True
                prev_block_iter, prev_height = saved_states[state]
                block_iter_diff = block_iter - prev_block_iter
                height_diff = chamber.max_height() - prev_height

                print(f"Found cycle! Iteration {prev_block_iter} matches iteration {block_iter}")
                print("Iter diff:", block_iter_diff)
                print("Height diff:", height_diff)

                assert block_iter_diff > 0
                assert height_diff > 0

                repeats = (num_iter - block_iter) // block_iter_diff
                block_iter += block_iter_diff * repeats
                chamber.correction += height_diff * repeats

            else:
                saved_states[state] = (block_iter, chamber.max_height())
        block_iter += 1
    return chamber.max_height()

print("Part 2", simulate_with_cycles(1000000000000))
