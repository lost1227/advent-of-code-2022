from pathlib import Path

USE_SAMPLE_INPUT = False
in_path = Path.cwd() / 'input.txt'

class Tree:
    def __init__(self, height):
        self.height = height
        self.visible = False

sample_input = """
30373
25512
65332
33549
35390
""".strip()

def print_forrest(forrest):
    for row in forrest:
        for tree in row:
            if tree.visible:
                print("\u001b[31m", end="")
            else:
                print("\u001b[32m", end="")
            print(tree.height, end="")
        print()
    print("\u001b[0m", end="")

if USE_SAMPLE_INPUT:
    forrest = [[Tree(int(c)) for c in row] for row in sample_input.split("\n")]
else:
    forrest = []
    with in_path.open("r") as inf:
        for line in inf.readlines():
            forrest.append([Tree(int(c)) for c in line.strip()])

def process_row(row):
    max_height_so_far = -1
    for tree in row:
        if tree.height > max_height_so_far:
            max_height_so_far = tree.height
            tree.visible = True

for row in forrest:
    process_row(row)
for row in forrest:
    process_row(row[::-1])
for i in range(len(forrest[0])):
    process_row([row[i] for row in forrest])
for i in range(len(forrest[0])):
    process_row([row[i] for row in forrest[::-1]])


#print_forrest(forrest)

visible_count = 0
for row in forrest:
    for tree in row:
        if tree.visible:
            visible_count += 1

print("Part 1:", visible_count)

def calculate_scenic_score(forrest, pos):
    calc_tree = forrest[pos[1]][pos[0]]
    #print(calc_tree.height)
    total_score = 1
    curr_score = 0
    # RIGHT
    for i in range(pos[0]+1, len(forrest[0])):
        curr_tree = forrest[pos[1]][i]
        curr_score += 1
        if curr_tree.height >= calc_tree.height:
            break
    total_score *= curr_score
    #print(f"{curr_score} * ", end = "")
    curr_score = 0
    # LEFT
    for i in range(pos[0]-1, -1, -1):
        curr_tree = forrest[pos[1]][i]
        curr_score += 1
        if curr_tree.height >= calc_tree.height:
            break
    total_score *= curr_score
    #print(f"{curr_score} * ", end = "")
    curr_score = 0
    # DOWN
    for i in range(pos[1]+1, len(forrest)):
        curr_tree = forrest[i][pos[0]]
        curr_score += 1
        if curr_tree.height >= calc_tree.height:
            break
    total_score *= curr_score
    #print(f"{curr_score} * ", end = "")
    curr_score = 0
    # UP
    for i in range(pos[1]-1, -1, -1):
        curr_tree = forrest[i][pos[0]]
        curr_score += 1
        if curr_tree.height >= calc_tree.height:
            break
    total_score *= curr_score
    #print(f"{curr_score} = {total_score} ")
    return total_score

max_score = 0

for i in range(0, len(forrest)):
    for j in range(0, len(forrest[0])):
        score = calculate_scenic_score(forrest, (j, i))
        if score > max_score:
            max_score = score

print("Part 2:", max_score)
