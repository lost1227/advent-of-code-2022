from pathlib import Path
import re
from itertools import chain, combinations

from tqdm import tqdm

USE_SAMPLE_INPUT = True
SKIP_PART_1 = True
in_path = Path.cwd() / 'input.txt'

sample_input = """
Valve AA has flow rate=0; tunnels lead to valves DD, II, BB
Valve BB has flow rate=13; tunnels lead to valves CC, AA
Valve CC has flow rate=2; tunnels lead to valves DD, BB
Valve DD has flow rate=20; tunnels lead to valves CC, AA, EE
Valve EE has flow rate=3; tunnels lead to valves FF, DD
Valve FF has flow rate=0; tunnels lead to valves EE, GG
Valve GG has flow rate=0; tunnels lead to valves FF, HH
Valve HH has flow rate=22; tunnel leads to valve GG
Valve II has flow rate=0; tunnels lead to valves AA, JJ
Valve JJ has flow rate=21; tunnel leads to valve II
""".strip()

if USE_SAMPLE_INPUT:
    input = sample_input
else:
    with in_path.open("r") as inf:
        input = inf.read().strip()


def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))

class Valve:
    STR_RE = re.compile(r'Valve (\S+) has flow rate=(\d+); tunnels? leads? to valves? (.*)$')

    def __init__(self, label: str, flow_rate: int, tunnels: 'list[str]'):
        self.label = label
        self.flow_rate = flow_rate
        self.tunnels = tunnels

    @staticmethod
    def from_str(inputstr: str):
        match = Valve.STR_RE.match(inputstr)
        if match is None:
            raise ValueError(f'Invalid valve string:"{inputstr}"')
        label = match.group(1)
        flow_rate = int(match.group(2))
        tunnels = match.group(3).split(", ")
        return Valve(label, flow_rate, tunnels)

    def __str__(self):
        return f'Valve {self.label} has flow rate={self.flow_rate}; tunnels lead to valves ' + ', '.join(self.tunnels)

    def __eq__(self, other):
        if not isinstance(other, Valve):
            return False
        return self.label == other.label and self.flow_rate == other.flow_rate and self.tunnels == other.tunnels

    def __hash__(self):
        return self.label.__hash__()

    def __repr__(self):
        return f"Valve({self.label})"

valves: 'dict[str, Valve]' = {}

for line in input.split('\n'):
    valve = Valve.from_str(line)
    valves[valve.label] = valve

for valve in valves.values():
    print(valve)

significant_valves = [valve for valve in valves.values() if valve.flow_rate > 0]
possible_open_valves = [frozenset(s) for s in powerset(significant_valves)]

if not SKIP_PART_1:

    solutions: 'list[dict[str, dict[set[Valve], int]]]' = []

    for i in trange(30):
        solutions.append({})
        #if i > 2:
        #    solutions[i-2] = []

        for valve in valves.values():
            solutions[i][valve.label] = {}
            for open_valves in possible_open_valves:
                sol = 0

                if i > 0:
                    for tunnel in valve.tunnels:
                        sol = max(sol, solutions[i-1][tunnel][open_valves])

                    if valve.flow_rate > 0 and valve not in open_valves:
                        new_open_valves = frozenset(open_valves.union([valve]))
                        sol = max(sol, solutions[i-1][valve.label][frozenset(new_open_valves)] + (valve.flow_rate * i))
                solutions[i][valve.label][open_valves] = sol

    solution = solutions[29]['AA'][frozenset()]
    print("Part 1:", solution)

    del solution
    del solutions
solutions: 'list[dict[str, dict[str, dict[set[Valve], int]]]]' = []
with tqdm(total=26 * len(valves) * len(valves) * len(possible_open_valves)) as pbar:
    for i in range(26):
        solutions.append({})
        if i > 2:
            solutions[i-2] = []

        for uvalve in valves.values():
            solutions[i][uvalve.label] = {}
            for evalve in valves.values():
                solutions[i][uvalve.label][evalve.label] = {}
                for open_valves in possible_open_valves:
                    pbar.update()
                    sol = 0

                    if i > 0:
                        # 1. you move, elephant moves
                        for ut in uvalve.tunnels:
                            for et in evalve.tunnels:
                                sol = max(sol, solutions[i-1][ut][et][open_valves])

                        # 2. you move, elephant opens
                        if evalve.flow_rate > 0 and evalve not in open_valves:
                            for ut in uvalve.tunnels:
                                new_open_valves = frozenset(open_valves.union([evalve]))
                                sol = max(sol, solutions[i-1][ut][evalve.label][new_open_valves] + (evalve.flow_rate * i))

                        # 3. you open, elephant moves
                        if uvalve.flow_rate > 0 and uvalve not in open_valves:
                            for et in evalve.tunnels:
                                new_open_valves = frozenset(open_valves.union([uvalve]))
                                sol = max(sol, solutions[i-1][uvalve.label][et][new_open_valves] + (uvalve.flow_rate * i))

                        # 4. you open, elephant opens
                        if uvalve.flow_rate > 0 and evalve.flow_rate > 0 and uvalve not in open_valves and evalve not in open_valves and uvalve != evalve:
                            new_open_valves = frozenset(open_valves.union([uvalve, evalve]))
                            sol = max(sol, solutions[i-1][uvalve.label][evalve.label][new_open_valves] + (uvalve.flow_rate * i) + (evalve.flow_rate * i))
                    solutions[i][uvalve.label][evalve.label][open_valves] = sol

def backtrace(moves_left: int, your_pos: str, elephant_pos: str, open_valves: 'set[Valve]'):
    print(f"== Minute {25-moves_left} ==")
    if len(open_valves) == 0:
        print("No valves are open.")
    else:
        print("Valves " + ", ".join(sorted([v.label for v in open_valves])) + " are open, releasing " + str(sum([v.flow_rate for v in open_valves])) + " pressure.")

    solution = solutions[moves_left][your_pos][elephant_pos][open_valves]

    if moves_left == 0:
        print()
        return

    print("Solution:", solution)

    uvalve = valves[your_pos]
    evalve = valves[elephant_pos]

    # 1. you move, elephant moves
    for ut in uvalve.tunnels:
        for et in evalve.tunnels:
            if solution == solutions[moves_left-1][ut][et][open_valves]:
                print(f"You move to valve {ut}.")
                print(f"The elephant moves to valve {et}.")
                print()
                backtrace(moves_left-1, ut, et, open_valves)
                return

    # 3. you open, elephant moves
    if uvalve.flow_rate > 0 and uvalve not in open_valves:
        for et in evalve.tunnels:
            new_open_valves = frozenset(open_valves.union([uvalve]))
            if solution == solutions[moves_left-1][uvalve.label][et][new_open_valves] + (uvalve.flow_rate * moves_left):
                print(f"You open valve {uvalve.label}.")
                print(f"The elephant moves to valve {et}.")
                print()
                backtrace(moves_left-1, uvalve.label, et, new_open_valves)
                return

    # 2. you move, elephant opens
    if evalve.flow_rate > 0 and evalve not in open_valves:
        for ut in uvalve.tunnels:
            new_open_valves = frozenset(open_valves.union([evalve]))
            if solution == solutions[moves_left-1][ut][evalve.label][new_open_valves] + (evalve.flow_rate * moves_left):
                print(f"You move to valve {ut}.")
                print(f"The elephant opens valve {evalve.label}.")
                print()
                backtrace(moves_left-1, ut, evalve.label, new_open_valves)
                return

    # 4. you open, elephant opens
    if uvalve.flow_rate > 0 and evalve.flow_rate > 0 and uvalve not in open_valves and evalve not in open_valves and uvalve != evalve:
        new_open_valves = frozenset(open_valves.union([uvalve, evalve]))
        if solution == solutions[moves_left-1][uvalve.label][evalve.label][new_open_valves] + (uvalve.flow_rate * moves_left) + (evalve.flow_rate * moves_left):
            print(f"You open valve {uvalve.label}.")
            print(f"The elephant opens valve {evalve.label}.")
            print()
            backtrace(moves_left-1, uvalve.label, evalve.label, new_open_valves)
            return

    raise ValueError("Should not be reached!!")

solution = solutions[-1]['AA']['AA'][frozenset()]

# backtrace(25, 'AA', 'AA', frozenset())

print("Part 2:", solution)
