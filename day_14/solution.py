from pathlib import Path
import time

USE_SAMPLE_INPUT = False
in_path = Path.cwd() / 'input.txt'

sample_input = """
498,4 -> 498,6 -> 496,6
503,4 -> 502,4 -> 502,9 -> 494,9
""".strip()

if USE_SAMPLE_INPUT:
    input = sample_input.split('\n')
else:
    with in_path.open("r") as inf:
        input = inf.read().strip().split('\n')

lines = []
for row in input:
    line = []
    for point in row.split(' -> '):
        x, y = point.split(',')
        line.append((int(x), int(y)))
    lines.append(line)


class Cave:
    def __init__(self, lines, sand_point=(500,0)):
        self.lines = lines
        self.bounds = None

        self.sand_point = sand_point

        self._calculate_grid()

    def _calculate_bounds(self):
        if self.bounds is not None:
            return self.bounds
        min_x = max_x = 500
        min_y = max_y = 0
        for line in self.lines:
            for x, y in line:
                min_x = min(x, min_x)
                max_x = max(x, max_x)
                min_y = min(y, min_y)
                max_y = max(y, max_y)

        self.bounds = ((min_x, max_x), (min_y, max_y))
        self.origin = (self.bounds[0][0], self.bounds[1][0])
        self.rel_sand_point = (self.sand_point[0] - self.origin[0], self.sand_point[1] - self.origin[1])
        return self.bounds

    def _calculate_grid(self):
        bounds = self._calculate_bounds()
        origin = (bounds[0][0], bounds[1][0])
        size = (bounds[0][1] - bounds[0][0] + 1, bounds[1][1] - bounds[1][0] + 1)

        self.grid = [ ['.' for _ in range(size[0])] for _ in range(size[1])]
        for line in self.lines:
            for i in range(1, len(line)):
                curr_point = line[i]
                prev_point = line[i-1]

                cx = curr_point[0] - origin[0]
                cy = curr_point[1] - origin[1]
                px = prev_point[0] - origin[0]
                py = prev_point[1] - origin[1]

                dx = cx - px
                dy = cy - py

                if dx != 0:
                    linelen = abs(dx)
                    assert dy == 0
                    if dx > 0:
                        dx = 1
                    else:
                        dx = -1
                else:
                    linelen = abs(dy)
                    assert dy != 0
                    if dy > 0:
                        dy = 1
                    else:
                        dy = -1
                for _ in range(linelen+1):
                    self.grid[py][px] = '#'
                    py += dy
                    px += dx
        self.grid[self.sand_point[1] - origin[1]][self.sand_point[0] - origin[0]] = '+'

    def add_floor(self):
        half_width = (len(self.grid) + 2)
        self.bounds = ((self.sand_point[0] - half_width, self.sand_point[0] + half_width), (self.sand_point[1], len(self.grid) + 1))
        self.origin = (self.bounds[0][0], self.bounds[1][0])
        self.rel_sand_point = (self.sand_point[0] - self.origin[0], self.sand_point[1] - self.origin[1])
        self._calculate_grid()
        for i in range(len(self.grid[-1])):
            self.grid[-1][i] = '#'

    def simulate_sand_drop(self, show=False):
        curr_sand = self.rel_sand_point
        while True:
            if show:
                print(self)
                time.sleep(0.005)
                for _ in range(len(self.grid) + 4):
                    print("\u001b[1F\u001b[2K", end="")
            if curr_sand[0] == self.rel_sand_point[0] and curr_sand[1] == self.rel_sand_point[1]:
                self.grid[curr_sand[1]][curr_sand[0]] = '+'
            else:
                self.grid[curr_sand[1]][curr_sand[0]] = '.'

            test_point = (curr_sand[0], curr_sand[1]+1)
            if test_point[1] == len(self.grid):
                return False
            if self.grid[test_point[1]][test_point[0]] == '.':
                curr_sand = test_point
                self.grid[test_point[1]][test_point[0]] = 'o'
                continue

            test_point = (curr_sand[0]-1, curr_sand[1]+1)
            if test_point[0] < 0:
                return False
            if self.grid[test_point[1]][test_point[0]] == '.':
                curr_sand = test_point
                self.grid[test_point[1]][test_point[0]] = 'o'
                continue

            test_point = (curr_sand[0]+1, curr_sand[1]+1)
            if test_point[0] == len(self.grid[0]):
                return False
            if self.grid[test_point[1]][test_point[0]] == '.':
                curr_sand = test_point
                self.grid[test_point[1]][test_point[0]] = 'o'
                continue
            self.grid[curr_sand[1]][curr_sand[0]] = 'o'
            return True

    def _recursive_fill(self, point):
        try:
            if self.grid[point[1]][point[0]] == '.':
                self.sand_count += 1
                self.grid[point[1]][point[0]] = 'o'
                self._recursive_fill((point[0], point[1]+1))
                self._recursive_fill((point[0]-1, point[1]+1))
                self._recursive_fill((point[0]+1, point[1]+1))
        except IndexError:
            pass

    def recursive_fill(self):
        self.grid[self.rel_sand_point[1]][self.rel_sand_point[0]] = '.'
        self.sand_count = 0
        self._recursive_fill(self.rel_sand_point)

    def __str__(self):
        bounds = self._calculate_bounds()
        out = ""
        values = sorted([bounds[0][0], 500, bounds[0][1]])
        for i in range(3):
            digit = 2-i
            out += "    "
            out += str((values[0] // (10 ** digit))%10)
            out += " " * (values[1] - values[0] - 1)
            out += str((values[1] // (10 ** digit))%10)
            out += " " * (values[2] - values[1] - 1)
            out += str((values[2] // (10 ** digit))%10)
            out += "\n"
        for i in range(len(self.grid)):
            curr_row = self.grid[i]
            out += f"{i:3d} {''.join(curr_row)}\n"
        return out

c = Cave(lines)
sand_count = 0
while c.simulate_sand_drop():
    sand_count += 1

print(c)
print("Part 1:", sand_count)

print('\n\n')

# Part 2
c.add_floor()

c.recursive_fill()

print(c)

print("Part 2:", c.sand_count)

