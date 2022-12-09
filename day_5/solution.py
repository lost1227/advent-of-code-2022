from pathlib import Path

import math
import copy

USE_SAMPLE_INPUT = False
in_path = Path.cwd() / 'input.txt'

class CrateStack:
    def __init__(self, crates = []):
        self.crates = crates

    def count(self):
        return len(self.crates)

    def pop_crate(self):
        assert self.count() > 0
        retval = self.crates[-1]
        self.crates = self.crates[:-1]
        return retval

    def push_crate(self, crate):
        self.crates.append(crate)

class PuzzleState:
    def __init__(self, stacks):
        self.stacks = stacks

    @staticmethod
    def from_lines(lines):
        num_stacks = math.ceil(len(lines[-1]) / 4)
        print(lines[-1])
        print(num_stacks)
        stacks = [[] for i in range(num_stacks)]

        for line in lines[:-1][::-1]:
            for i in range(num_stacks):
                #print(f"\"{line}\" -- {(i*4)+1} -- \"{line[i*4:(i+1)*4]}\" -- {line[(i*4)+1]}")
                crate = line[(i*4)+1]
                if crate != " ":
                    stacks[i].append(crate)

        return PuzzleState([CrateStack(crates) for crates in stacks])

    def move(self, count, from_stack_no, to_stack_no):
        from_stack = self.stacks[from_stack_no-1]
        to_stack = self.stacks[to_stack_no-1]
        for i in range(count):
            crate = from_stack.pop_crate()
            to_stack.push_crate(crate)

    def move_2(self, count, from_stack_no, to_stack_no):
        from_stack = self.stacks[from_stack_no-1]
        to_stack = self.stacks[to_stack_no-1]
        crates = [from_stack.pop_crate() for i in range(count)]
        for crate in crates[::-1]:
            to_stack.push_crate(crate)


    def __str__(self):
        out = ""
        max_stack_height = max([it.count() for it in self.stacks])
        for row in range(max_stack_height-1, -1, -1):
            for stack in self.stacks:
                if stack.count() > row:
                    out += f"[{stack.crates[row]}]"
                else:
                    out += "   "
            out += "\n"
        for i in range(len(self.stacks)):
            out += f" {i+1} "

        out += "\n"
        return out

if USE_SAMPLE_INPUT:
    state = PuzzleState([CrateStack(stack) for stack in [['Z', 'N'], ['M', 'C', 'D'], ['P']]])
    moves = [
        (1, 2, 1),
        (3, 1, 3),
        (2, 2, 1),
        (1, 1, 2)
    ]
else:
    with in_path.open("r") as inf:
        read_moves = False
        state_lines = []
        moves = []
        for line in inf.readlines():
            line = line[:-1]
            if not read_moves:
                if line == "":
                    read_moves = True
                    state = PuzzleState.from_lines(state_lines)
                else:
                    state_lines.append(line)
            else:
                parts = line.split()
                assert parts[0] == "move" and parts[2] == "from" and parts[4] == "to"
                move = (int(parts[1]), int(parts[3]), int(parts[5]))
                moves.append(move)

part1_state = copy.deepcopy(state)

print(part1_state)
for move in moves:
    part1_state.move(move[0], move[1], move[2])
print(part1_state)

print("Part 1:", "".join([stack.crates[-1] for stack in part1_state.stacks]))

print("\n\n")

part2_state = copy.deepcopy(state)
print(part2_state)
for move in moves:
    part2_state.move_2(move[0], move[1], move[2])
print(part2_state)

print("Part 2:", "".join([stack.crates[-1] for stack in part2_state.stacks]))
