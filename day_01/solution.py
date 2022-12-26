from pathlib import Path

in_path = Path.cwd() / "input.txt"

with in_path.open("r") as inf:
    lines = inf.readlines()
    elves = []
    curr_elf = []
    for line in lines:
        if line.strip() == "":
            if curr_elf != []:
                elves.append(curr_elf)
                curr_elf = []
        else:
            curr_elf.append(int(line.strip()))

sums = [sum(elf) for elf in elves]

print("Part 1:", max(sums))

sums.sort(reverse=True)

print("Part 2:", sums[0] + sums[1] + sums[2])
