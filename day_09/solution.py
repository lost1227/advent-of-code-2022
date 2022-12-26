from pathlib import Path

USE_SAMPLE_INPUT = False
in_path = Path.cwd() / 'input.txt'

sample_input = """
R 4
U 4
L 3
D 1
R 4
D 1
L 5
R 2
""".strip()

if USE_SAMPLE_INPUT:
    cmds = sample_input.split("\n")
else:
    with in_path.open('r') as inf:
        cmds = [line.strip() for line in inf.readlines()]

class Knot:
    def __init__(self):
        self.head_pos = (0, 0)
        self.tail_pos = (0, 0)
        self.tail_visited = set([self.tail_pos])

    def move_head(self, dir):
        assert abs(dir[0]) <= 1 and abs(dir[1]) <= 1
        self.head_pos = (self.head_pos[0] + dir[0], self.head_pos[1] + dir[1])

        self.update_tailpos()
        self.tail_visited.add(self.tail_pos)

    def update_tailpos(self):
        hx, hy = self.head_pos
        tx, ty = self.tail_pos

        if abs(hx - tx) <= 1 and abs(hy - ty) <= 1:
            return

        # If the head is ever two steps directly up, down, left, or right from the tail, the tail
        # must also move one step in that direction so it remains close enough:
        if hx == tx:
            if hy - ty < -1:
                # . T .    . . .
                # . . . -> . T .
                # . H .    . H .
                self.tail_pos = (tx, ty - 1)
                return
            if hy - ty > 1:
                # . H .    . H .
                # . . . -> . T .
                # . T .    . . .
                self.tail_pos = (tx, ty + 1)
                return
            return
        if hy == ty:
            if hx - tx > 1:
                # . . .    . . .
                # T . H -> . T H
                # . . .    . . .
                self.tail_pos = (tx + 1, ty)
                return
            if hx - tx < -1:
                # . . .    . . .
                # H . T -> H T .
                # . . .    . . .
                self.tail_pos = (tx - 1, ty)
                return
            return

        # Otherwise, if the head and tail aren't touching and aren't in the same row or column, the
        # tail always moves one step diagonally to keep up:
        if hx - tx > 1:
            if hy < ty:
                # T . .    . . .
                # . . H -> . T H
                # . . .    . . .
                self.tail_pos = (tx + 1, ty - 1)
                return
            if hy > ty:
                # . . .    . . .
                # . . H -> . T H
                # T . .    . . .
                self.tail_pos = (tx + 1, ty + 1)
                return
            return
        if hx - tx < -1:
            if hy < ty:
                # . . T    . . .
                # H . . -> H T .
                # . . .    . . .
                self.tail_pos = (tx - 1, ty - 1)
                return
            if hy > ty:
                # . . .    . . .
                # H . . -> H T .
                # . . T    . . .
                self.tail_pos = (tx - 1, ty + 1)
                return
            return
        if hy - ty < -1:
            if hx > tx:
                # T . .    . . .
                # . . . -> . T .
                # . H .    . H .
                self.tail_pos = (tx + 1, ty - 1)
                return
            if hx < tx:
                # . . T    . . .
                # . . . -> . T .
                # . H .    . H .
                self.tail_pos = (tx - 1, ty - 1)
                return
            return
        if hy - ty > 1:
            if hx > tx:
                # . H .    . H .
                # . . . -> . T .
                # T . .    . . .
                self.tail_pos = (tx + 1, ty + 1)
                return
            if hx < tx:
                # . H .    . H .
                # . . . -> . T .
                # . . T    . . .
                self.tail_pos = (tx - 1, ty + 1)
                return
            return

    def plot_visited(self, size, start):
        out = ''
        for i in range(size[1]):
            y = size[1] - i - 1
            for j in range(size[0]):
                x = j
                if (x + start[0], y + start[1]) in self.tail_visited:
                    out += '#'
                else:
                    out += '.'
            out += '\n'
        return out

class Rope:
    def __init__(self, length):
        self.length = length
        self.knots = [Knot() for i in range(length)]

    def step(self, dir):
        if dir == 'U':
            diff = (0, 1)
        elif dir == 'D':
            diff = (0, -1)
        elif dir == 'L':
            diff = (-1, 0)
        elif dir == 'R':
            diff = (1, 0)

        self.knots[0].move_head(diff)
        for i in range(1, len(self.knots)):
            prev = self.knots[i-1]
            curr = self.knots[i]
            diff = (prev.tail_pos[0] - curr.head_pos[0], prev.tail_pos[1] - curr.head_pos[1])
            curr.move_head(diff)


    def plot(self, size, start):
        out = ''
        for i in range(size[1]):
            y = (size[1] - i - 1) + start[1]
            for j in range(size[0]):
                x = j + start[0]
                if (x, y) == self.knots[0].head_pos:
                    out += 'H'
                else:
                    is_knot = False
                    for i, knot in enumerate(self.knots):
                        if knot.tail_pos == (x, y):
                            out += str(i+1)
                            is_knot = True
                            break
                    if not is_knot:
                        if x == 0 and y == 0:
                            out += 's'
                        else:
                            out += '.'
            out += '\n'
        return out

rope = Rope(1)

if USE_SAMPLE_INPUT:
    print("== Initial State ==")
    print(rope.plot((6, 5), (0, 0)))

for cmd in cmds:
    if USE_SAMPLE_INPUT:
        print(f"== {cmd} ==", end="\n\n")

    dir, count = cmd.split()
    count = int(count)
    for i in range(count):
        rope.step(dir)
        if USE_SAMPLE_INPUT:
            print(rope.plot((6, 5), (0, 0)))

if USE_SAMPLE_INPUT:
    print("\n")
    print(rope.knots[0].plot_visited((6, 5), (0, 0)))

print("Part 1:", len(rope.knots[0].tail_visited))

# Part 2

if USE_SAMPLE_INPUT:
    cmds = """
    R 5
    U 8
    L 8
    D 3
    R 17
    D 10
    L 25
    U 20
    """.strip().split('\n')

rope = Rope(9)
if USE_SAMPLE_INPUT:
    print("== Initial State ==")
    print(rope.plot((26, 21), (-11, -5)))

for cmd in cmds:
    if USE_SAMPLE_INPUT:
        print(f"== {cmd} ==", end="\n\n")

    dir, count = cmd.split()
    count = int(count)
    for i in range(count):
        rope.step(dir)
    if USE_SAMPLE_INPUT:
        print(rope.plot((26, 21), (-11, -5)))

if USE_SAMPLE_INPUT:
    print("\n")
    print(rope.knots[-1].plot_visited((26, 21), (-11, -5)))

print("Part 2:", len(rope.knots[-1].tail_visited))
