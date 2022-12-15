from pathlib import Path
import re

USE_SAMPLE_INPUT = False
in_path = Path.cwd() / 'input.txt'

sample_input = """
Sensor at x=2, y=18: closest beacon is at x=-2, y=15
Sensor at x=9, y=16: closest beacon is at x=10, y=16
Sensor at x=13, y=2: closest beacon is at x=15, y=3
Sensor at x=12, y=14: closest beacon is at x=10, y=16
Sensor at x=10, y=20: closest beacon is at x=10, y=16
Sensor at x=14, y=17: closest beacon is at x=10, y=16
Sensor at x=8, y=7: closest beacon is at x=2, y=10
Sensor at x=2, y=0: closest beacon is at x=2, y=10
Sensor at x=0, y=11: closest beacon is at x=2, y=10
Sensor at x=20, y=14: closest beacon is at x=25, y=17
Sensor at x=17, y=20: closest beacon is at x=21, y=22
Sensor at x=16, y=7: closest beacon is at x=15, y=3
Sensor at x=14, y=3: closest beacon is at x=15, y=3
Sensor at x=20, y=1: closest beacon is at x=15, y=3
""".strip()

if USE_SAMPLE_INPUT:
    input = sample_input
else:
    with in_path.open("r") as inf:
        input = inf.read().strip()

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def copy(self):
        return Point(self.x, self.y)

    def __str__(self):
        return f"({self.x}, {self.y})"

    def __repr__(self):
        return f"Point({self.x.__repr__()}, {self.y.__repr__()})"

    def __eq__(self, other):
        if not isinstance(other, Point):
            return False
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return (self.x, self.y).__hash__()

    def __add__(self, other):
        if not isinstance(other, Point):
            raise TypeError(f"Can only add Point (not \"{ other.__class__.__name__ }\") to Point")
        return Point(self.x + other.x, self.y + other.y)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if not isinstance(other, Point):
            raise TypeError(f"Can only add Point (not \"{ other.__class__.__name__ }\") to Point")
        return Point(self.x - other.x, self.y - other.y)

    def __rsub__(self, other):
        return self.__sub__(other)

class Sensor:
    FROM_STR_RE = re.compile(r'Sensor at x=(-?\d+), y=(-?\d+): closest beacon is at x=(-?\d+), y=(-?\d+)')

    def __init__(self, sensor: Point, beacon: Point):
        self.sensor = sensor
        self.beacon = beacon

        self.manhattan_distance = abs(self.beacon.x - self.sensor.x) + abs(self.beacon.y - self.sensor.y)

    @staticmethod
    def from_string(string) -> 'Sensor':
        match = Sensor.FROM_STR_RE.match(string)
        if match is None:
            raise ValueError(f"Invalid sensor input: \"{string}\"")
        sx = int(match.group(1))
        sy = int(match.group(2))
        bx = int(match.group(3))
        by = int(match.group(4))
        return Sensor(Point(sx, sy), Point(bx, by))

    def get_bounding_box(self):
        dist = Point(self.manhattan_distance, self.manhattan_distance)

        return (self.sensor - dist, self.sensor + dist)

    def point_in_range(self, test: Point):
        dist = abs(test.x - self.sensor.x) + abs(test.y - self.sensor.y)
        return dist <= self.manhattan_distance

    def get_xrange_for_row(self, row: int):
        dist = self.manhattan_distance - abs(self.sensor.y - row)
        if dist < 0:
            return None
        else:
            # range is inclusive
            return (self.sensor.x - dist, self.sensor.x + dist)

    def __str__(self):
        return f"Sensor({self.sensor}, {self.beacon})"


class Grid:
    def __init__(self, sensors: 'list[Sensor]'):
        self.sensors = sensors
        self.__calculate_bounds()
        self.grid = None

    def __calculate_bounds(self):
        assert len(self.sensors) > 0
        min_x = max_x = self.sensors[0].sensor.x
        min_y = max_y = self.sensors[0].sensor.y
        for sensor in self.sensors:
            bounding_box = sensor.get_bounding_box()
            min_x = min(min_x, bounding_box[0].x)
            max_x = max(max_x, bounding_box[1].x)
            min_y = min(min_y, bounding_box[0].y)
            max_y = max(max_y, bounding_box[1].y)

        origin = Point(min_x, min_y)
        size = (max_x - min_x + 1, max_y - min_y + 1)

        self.bounds = (Point(min_x, min_y), Point(max_x, max_y))
        self.origin = origin
        self.size = size

    def set_point(self, point: Point, value: str):
        if self.grid is None:
            self.__plot_grid()
        dst = point - self.origin
        if dst.y < 0 or dst.y >= len(self.grid) or dst.x < 0 or dst.x >= len(self.grid[0]):
            raise ValueError(f"Cannot set point {point} outside of grid")
        self.grid[dst.y][dst.x] = value

    def get_point(self, point: Point) -> str:
        if self.grid is None:
            self.__plot_grid()
        dst = point - self.origin
        if dst.y < 0 or dst.y >= len(self.grid) or dst.x < 0 or dst.x >= len(self.grid[0]):
            raise ValueError(f"Cannot get point {point} outside of grid")
        return self.grid[dst.y][dst.x]

    def __plot_grid(self):
        self.grid = [ ['.' for _ in range(self.size[0])] for _ in range(self.size[1]) ]
        for sensor in self.sensors:
            self.set_point(sensor.sensor, 'S')
            self.set_point(sensor.beacon, 'B')

    def __str__(self):
        if self.grid is None:
            self.__plot_grid()
        out = ""
        y_axis_digit_count = max(len(str(self.bounds[0].y)), len(str(self.bounds[1].y)))
        if self.bounds[0].x < 0:
            offset = abs(self.bounds[0].x) % 5
        else:
            offset = 5 - (self.bounds[0].x % 5)
        x_axis_lables = [str(x) for x in range(self.bounds[0].x + offset, self.bounds[1].x+1, 5)]
        x_axis_digit_count = max([len(x) for x in x_axis_lables])
        x_axis_lables = [x.rjust(x_axis_digit_count) for x in x_axis_lables]
        for i in range(0, x_axis_digit_count):
            out += (" " * (y_axis_digit_count + 1)) + (" " * offset)
            for label in x_axis_lables:
                out += label[i]
                if label != x_axis_lables[-1]:
                    out += "    "
            out += "\n"

        for y, row in enumerate(self.grid):
            out += str(y + self.origin.y).rjust(y_axis_digit_count) + " "
            out += "".join(row)
            out += '\n'
        return out

    def __draw_manhattan_ring(self, center: Point, radius: int):
        if self.grid is None:
            self.__plot_grid()
        curr = Point(center.x, center.y - radius)
        dirs = [Point(1, 1), Point(-1, 1), Point(-1, -1), Point(1, -1)]
        for dir in dirs:
            while abs(curr.x - center.x) + abs(curr.y - center.y) == radius:
                try:
                    v = self.get_point(curr)
                    if v == '.':
                        self.set_point(curr, '#')
                except ValueError:
                    pass
                curr += dir
            curr -= dir

    def draw_sensor(self, sensor):
        radius = abs(sensor.beacon.x - sensor.sensor.x) + abs(sensor.beacon.y - sensor.sensor.y)
        for i in range(1, radius+1):
            self.__draw_manhattan_ring(sensor.sensor, i)

    def cross_out_beacon_spots(self):
        for sensor in self.sensors:
            self.draw_sensor(sensor)

    def __get_nobeacon_ranges_for_row(self, row):
        row_ranges = [sensor.get_xrange_for_row(row) for sensor in self.sensors]
        row_ranges = [r for r in row_ranges if r is not None]
        row_ranges.sort(key=lambda r: r[0])
        curr_s, curr_e = row_ranges[0]
        consolidated_ranges = []
        for rang in row_ranges:
            if rang[0] > curr_e+1:
                consolidated_ranges.append((curr_s, curr_e))
                curr_s, curr_e = rang
            else:
                curr_e = max(curr_e, rang[1])
        consolidated_ranges.append((curr_s, curr_e))
        return consolidated_ranges

    def count_nobeacon_spots_in_row(self, row):
        consolidated_ranges = self.__get_nobeacon_ranges_for_row(row)

        count = sum([rang[1] - rang[0] + 1 for rang in consolidated_ranges])

        remove_points = set()

        for sensor in self.sensors:
            remove_points.add(sensor.sensor)
            remove_points.add(sensor.beacon)

        for point in remove_points:
            if point.y == row:
                for rang in consolidated_ranges:
                    if point.x >= rang[0] and point.x <= rang[1]:
                        count -= 1
        return count

    def find_nobeacon_spots_in_area(self, bounding_box):
        x_range = (bounding_box[0].x, bounding_box[1].x)
        y_range = (bounding_box[0].y, bounding_box[1].y)
        points = set()

        print(f"0%")
        for y in range(y_range[0], y_range[1]+1):
            if y % 10000 == 0:
                print(f"\u001b[1F\u001b[2K{(y / 4000000) * 100:.0f}%")
            all_ranges = self.__get_nobeacon_ranges_for_row(y)
            ranges = []
            for rang in all_ranges:
                if rang[1] < x_range[0] or rang[0] > x_range[1]:
                    continue
                range_start = max(rang[0], x_range[0])
                range_end = min(rang[1], x_range[1])
                ranges.append((range_start, range_end))

            uncovered_ranges = []
            curr_x = x_range[0]
            for rang in ranges:
                if rang[0] > curr_x:
                    uncovered_ranges.append((curr_x, rang[0]-1))
                curr_x = rang[1]+1
            if curr_x < x_range[1]:
                uncovered_ranges.append((curr_x+1, x_range[1]))

            if USE_SAMPLE_INPUT:
                print(f"== Row {y} ==")
                print("ranges:", all_ranges)
                print("trimmed ranges:", ranges)
                print("inverted:", uncovered_ranges)
                print()

            for rang in uncovered_ranges:
                for x in range(rang[0], rang[1]+1):
                    points.add(Point(x, y))
        return points




sensors = [Sensor.from_string(line) for line in input.split('\n')]
grid = Grid(sensors)

if USE_SAMPLE_INPUT:
    #grid.draw_sensor(sensors[6])
    grid.cross_out_beacon_spots()

    print(grid)

    count_row = 10
else:
    count_row = 2000000

print("Part 1:", grid.count_nobeacon_spots_in_row(count_row))

# PART 2

if USE_SAMPLE_INPUT:
    points = grid.find_nobeacon_spots_in_area((Point(0, 0), Point(20, 20)))
else:
    points = grid.find_nobeacon_spots_in_area((Point(0, 0), Point(4000000, 4000000)))

for point in points:
    print(point)

assert len(points) == 1

point = next(iter(points))
print("Part 2:", (point.x * 4000000) + point.y)
