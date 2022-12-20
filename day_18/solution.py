from pathlib import Path
from queue import SimpleQueue

USE_SAMPLE_INPUT = False
in_path = Path.cwd() / 'input.txt'

sample_input = """
2,2,2
1,2,2
3,2,2
2,1,2
2,3,2
2,2,1
2,2,3
2,2,4
2,2,6
1,2,5
3,2,5
2,1,5
2,3,5
""".strip()

if USE_SAMPLE_INPUT:
    input = sample_input
else:
    with in_path.open("r") as inf:
        input = inf.read().strip()

class Vector3:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        return f'({self.x}, {self.y}, {self.z})'

    def __repr__(self):
        return f'Vector2({self.x}, {self.y}, {self.z})'

    def __eq__(self, other):
        if not isinstance(other, Vector3):
            return False

        return other.x == self.x and other.y == self.y and other.z == self.z

    def __hash__(self):
        return (self.x, self.y, self.z).__hash__()

    def __add__(self, other):
        if not isinstance(other, Vector3):
            raise TypeError(f"Can only add Vector3 (not \"{ other.__class__.__name__ }\") to Vector3")
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if not isinstance(other, Vector3):
            raise TypeError(f"Can only subtract Vector3 (not \"{ other.__class__.__name__ }\") from Vector3")
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __rsub__(self, other):
        return self.__sub__(other)

DIRS = (Vector3(1, 0, 0), Vector3(-1, 0, 0), Vector3(0, 1, 0), Vector3(0, -1, 0), Vector3(0, 0, 1), Vector3(0, 0, -1))

cubes: 'set[Vector3]' = set()
for line in input.split("\n"):
    x, y, z = line.split(",")
    cubes.add(Vector3(int(x), int(y), int(z)))

seen: 'set[Vector3]' = set()
to_visit: 'SimpleQueue[Vector3]' = SimpleQueue()
connected_side_count = 0
while len(seen) < len(cubes):
    unseen = cubes.difference(seen)
    curr = next(iter(unseen))
    to_visit.put(curr)
    seen.add(curr)

    while not to_visit.empty():
        curr = to_visit.get()
        for dir in DIRS:
            test = curr + dir
            if test in cubes:
                connected_side_count += 1
            if test in cubes and test not in seen:
                seen.add(test)
                to_visit.put(test)

print("Part 1:", (len(cubes) * 6) - connected_side_count)

# PART 2

curr = next(iter(cubes))
minx = maxx = curr.x
miny = maxy = curr.y
minz = maxz = curr.z
for cube in cubes:
    minx = min(minx, cube.x)
    miny = min(miny, cube.y)
    minz = min(minz, cube.z)

    maxx = max(maxx, cube.x)
    maxy = max(maxy, cube.y)
    maxz = max(maxz, cube.z)



to_visit: 'SimpleQueue[Vector3]' = SimpleQueue()
seen: 'set[Vector3]' = set()

for x in range(minx-1, maxx + 2):
    for y in range(miny - 1, maxy + 2):
        for z in range(minz - 1, maxz + 2):
            if x > minx-1 and x < maxx+1 and y > miny-1 and y < maxy+1 and z > minz-1 and z < maxz+1:
                continue
            curr = Vector3(x, y, z)
            if curr in seen:
                continue
            to_visit.put(curr)
            seen.add(curr)

surface_area_count = 0
while not to_visit.empty():
    curr = to_visit.get()
    for dir in DIRS:
        test = curr + dir
        if test in cubes:
            surface_area_count += 1
        else:
            if test.x < minx or test.x > maxx or test.y < miny or test.y > maxy or test.z < minz or test.z > maxz:
                continue
            if test not in seen:
                seen.add(test)
                to_visit.put(test)

print("Part 2:", surface_area_count)

