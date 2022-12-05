from pathlib import Path

USE_SAMPLE_INPUT = False
in_path = Path.cwd() / 'input.txt'

assignments = []
if USE_SAMPLE_INPUT:
    assignments = [
        ((2, 4), (6, 8)),
        ((2, 3), (4, 5)),
        ((5, 7), (7, 9)),
        ((2, 8), (3, 7)),
        ((6, 6), (4, 6)),
        ((2, 6), (4, 8))
    ]
else:
    with in_path.open("r") as inf:
        for line in inf.readlines():
            ass1, ass2 = line.strip().split(',')
            ass1 = [int(i) for i in ass1.split('-')]
            ass2 = [int(i) for i in ass2.split('-')]
            assert ass1[0] <= ass1[1] and ass2[0] <= ass2[1]
            assignments.append((ass1, ass2))

def ass1_in_ass2(ass1, ass2):
    if ass1[0] >= ass2[0] and ass1[1] <= ass2[1]:
        return True
    return False

def ass1_overlap_ass2(ass1, ass2):
    if ass1[0] < ass2[0]:
        return ass1[1] >= ass2[0]
    else:
        return ass1[0] <= ass2[1]

count = 0
for ass1, ass2 in assignments:
    if ass1_in_ass2(ass1, ass2) or ass1_in_ass2(ass2, ass1):
        count += 1

print("Part 1:", count)

count = 0
for ass1, ass2 in assignments:
    if ass1_overlap_ass2(ass1, ass2):
        count += 1

print("Part 2:", count)
