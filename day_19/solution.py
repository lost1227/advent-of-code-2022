from pathlib import Path
import re
from queue import SimpleQueue

USE_SAMPLE_INPUT = True
in_path = Path.cwd() / 'input.txt'

sample_input = """
Blueprint 1:
  Each ore robot costs 4 ore.
  Each clay robot costs 2 ore.
  Each obsidian robot costs 3 ore and 14 clay.
  Each geode robot costs 2 ore and 7 obsidian.

Blueprint 2:
  Each ore robot costs 2 ore.
  Each clay robot costs 3 ore.
  Each obsidian robot costs 3 ore and 8 clay.
  Each geode robot costs 3 ore and 12 obsidian.
""".strip()

if USE_SAMPLE_INPUT:
    blueprints = [' '.join([l.strip() for l in bp.split('\n')]) for bp in sample_input.split("\n\n")]
else:
    with in_path.open("r") as inf:
        blueprints = inf.read().strip().split('\n')

class Resources:
    def __init__(self, ore: int = 0, clay: int = 0, obsidian: int = 0, geodes: int = 0):
        self.ore = ore
        self.clay = clay
        self.obsidian = obsidian
        self.geodes = geodes

    def can_afford(self, cost: 'Resources') -> bool:
        return self.ore >= cost.ore \
            and self.clay >= cost.clay \
            and self.obsidian >= cost.obsidian \
            and self.geodes >= cost.geodes

    def __str__(self):
        strs = []
        if self.ore > 0:
            strs.append(f'{self.ore} ore')
        if self.clay > 0:
            strs.append(f'{self.clay} clay')
        if self.obsidian > 0:
            strs.append(f'{self.obsidian} obsidian')
        if self.geodes > 0:
            strs.append(f'{self.geodes} geodes')

        if len(strs) == 0:
            return 'No cost'
        elif len(strs) == 1:
            return strs[0]
        elif len(strs) == 2:
            return strs[0] + " and " + strs[1]
        else:
            return ", ".join(strs[:-1]) + ", and " + strs[-1]

    def __repr__(self):
        strs = []
        if self.ore > 0:
            strs.append(f'ore={self.ore}')
        if self.clay > 0:
            strs.append(f'clay={self.clay}')
        if self.obsidian > 0:
            strs.append(f'obsidian={self.obsidian}')
        if self.geodes > 0:
            strs.append(f'geodes={self.geodes}')
        return "Cost(" + ", ".join(strs) + ")"

    def __eq__(self, other):
        if not isinstance(other, Resources):
            return False
        return self.ore == other.ore \
            and self.clay == other.clay \
            and self.obsidian == other.obsidian \
            and self.geodes == other.geodes

    def __hash__(self):
        return (self.ore, self.clay, self.obsidian, self.geodes).__hash__()

    def __add__(self, other):
        if not isinstance(other, Resources):
            raise TypeError(f"Can only add Resources (not \"{ other.__class__.__name__ }\") to Resources")
        return Resources(self.ore + other.ore, self.clay + other.clay, self.obsidian + other.obsidian, self.geodes + other.geodes)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if not isinstance(other, Resources):
            raise TypeError(f"Can only subtract Resources (not \"{ other.__class__.__name__ }\") from Resources")
        return Resources(self.ore - other.ore, self.clay - other.clay, self.obsidian - other.obsidian, self.geodes - other.geodes)

    def __rsub__(self, other):
        return self.__sub__(other)


class Blueprint:
    FROM_STR_RE = re.compile(r'Blueprint (\d+): Each ore robot costs (\d+) ore. Each clay robot costs (\d+) ore. Each obsidian robot costs (\d+) ore and (\d+) clay. Each geode robot costs (\d+) ore and (\d+) obsidian.')
    def __init__(self, id: int, ore_cost: Resources, clay_cost: Resources, obsidian_cost: Resources, geode_cost: Resources):
        self.id = id
        self.ore_cost = ore_cost
        self.clay_cost = clay_cost
        self.obsidian_cost = obsidian_cost
        self.geode_cost = geode_cost

        self.__calculate_max_costs()

    @staticmethod
    def from_str(instr: str) -> 'Blueprint':
        match = Blueprint.FROM_STR_RE.match(instr)
        if not match:
            raise ValueError(f"Invalid blueprint string: \"{instr}\"")
        id = int(match.group(1))
        ore_cost = Resources(ore=int(match.group(2)))
        clay_cost = Resources(ore=int(match.group(3)))
        obsidian_cost = Resources(ore=int(match.group(4)), clay=int(match.group(5)))
        geode_cost = Resources(ore=int(match.group(6)), obsidian=int(match.group(7)))
        return Blueprint(id, ore_cost, clay_cost, obsidian_cost, geode_cost)

    def __calculate_max_costs(self) -> Resources:
        self.max_costs = Resources(
            ore = max(self.ore_cost.ore, self.clay_cost.ore, self.obsidian_cost.ore, self.geode_cost.ore),
            clay = max(self.ore_cost.clay, self.clay_cost.clay, self.obsidian_cost.clay, self.geode_cost.clay),
            obsidian = max(self.ore_cost.obsidian, self.clay_cost.obsidian, self.obsidian_cost.obsidian, self.geode_cost.obsidian),
            geodes = max(self.ore_cost.geodes, self.clay_cost.geodes, self.obsidian_cost.geodes, self.geode_cost.geodes)
        )

    def __repr__(self):
        return f'Blueprint(ore_cost={self.ore_cost.__repr__()}, clay_cost={self.clay_cost.__repr__()}, obsidian_cost={self.obsidian_cost.__repr__()}, geode_cost={self.geode_cost.__repr__()})'

class GameState:
    def __init__(self, minutes_left: int, resources: Resources, robots: Resources):
        self.minutes_left = minutes_left
        self.resources = resources
        self.robots = robots

    def tick(self) -> 'GameState':
        return GameState(
            minutes_left=self.minutes_left-1,
            resources=self.resources + self.robots,
            robots=self.robots
        )

    def can_build_ore_robot(self, blueprint: Blueprint) -> bool:
        return self.resources.can_afford(blueprint.ore_cost)

    def should_build_ore_robot(self, blueprint: Blueprint) -> bool:
        return self.robots.ore < blueprint.max_costs.ore \
            and self.robots.ore > 0

    def build_ore_robot(self, blueprint: Blueprint) -> 'GameState':
        assert self.can_build_ore_robot(blueprint)
        return GameState(
            minutes_left=self.minutes_left-1,
            resources=self.resources + self.robots - blueprint.ore_cost,
            robots = self.robots + Resources(ore=1)
        )

    def can_build_clay_robot(self, blueprint: Blueprint) -> bool:
        return self.resources.can_afford(blueprint.clay_cost)

    def should_build_clay_robot(self, blueprint: Blueprint) -> bool:
        return self.robots.clay < blueprint.max_costs.clay \
            and self.robots.ore > 0

    def build_clay_robot(self, blueprint: Blueprint) -> 'GameState':
        assert self.can_build_clay_robot(blueprint)
        return GameState(
            minutes_left=self.minutes_left-1,
            resources=self.resources + self.robots - blueprint.clay_cost,
            robots = self.robots + Resources(clay=1)
        )

    def can_build_obsidian_robot(self, blueprint: Blueprint) -> bool:
        return self.resources.can_afford(blueprint.obsidian_cost)

    def should_build_obsidian_robot(self, blueprint: Blueprint) -> bool:
        return self.robots.obsidian < blueprint.max_costs.obsidian \
            and self.robots.ore > 0 and self.robots.clay > 0

    def build_obsidian_robot(self, blueprint: Blueprint) -> 'GameState':
        assert self.can_build_obsidian_robot(blueprint)
        return GameState(
            minutes_left=self.minutes_left-1,
            resources=self.resources + self.robots - blueprint.obsidian_cost,
            robots = self.robots + Resources(obsidian=1)
        )

    def can_build_geode_robot(self, blueprint: Blueprint) -> bool:
        return self.resources.can_afford(blueprint.geode_cost)

    def should_build_geode_robot(self, blueprint: Blueprint) -> bool:
        return self.robots.ore > 0 and self.robots.obsidian > 0

    def build_geode_robot(self, blueprint: Blueprint) -> 'GameState':
        assert self.can_build_geode_robot(blueprint)
        return GameState(
            minutes_left=self.minutes_left-1,
            resources=self.resources + self.robots - blueprint.geode_cost,
            robots = self.robots + Resources(geodes=1)
        )

    def estimate_upper_bound(self, blueprint: Blueprint):
        n = self.robots.geodes + self.minutes_left
        return self.resources.geodes + ( (n * (n+1) ) - (self.robots.geodes * (self.robots.geodes + 1)) ) / 2

    def __eq__(self, other):
        if not isinstance(other, GameState):
            return False
        return other.minutes_left == self.minutes_left \
            and other.resources == self.resources \
            and other.robots == self.robots

    def __hash__(self):
        return (self.minutes_left, self.resources, self.robots).__hash__()

blueprints = [Blueprint.from_str(bp) for bp in blueprints]

for blueprint in blueprints:
    print(blueprint)

def evaluate_blueprint(bp: Blueprint):
    global_max = 0
    states: 'dict[GameState, int]' = {}
    def _max_geodes(state: GameState):
        nonlocal global_max
        if state.minutes_left == 0:
            return state.resources.geodes
        if state in states:
            return states[state]

        next_states = []
        if state.should_build_geode_robot(bp):
            next_state = state
            while not next_state.can_build_geode_robot(bp):
                next_state = state.tick()
            next_state = state.build_geode_robot()
            next_states.append(next_state)

        if state.should_build_obsidian_robot(bp):
            next_state = state
            while not next_state.can_build_obsidian_robot(bp):
                next_state = state.tick()
            next_state = state.build_obsidian_robot()
            next_states.append(next_state)

        next_states = []
        if state.should_build_clay_robot(bp):
            next_state = state
            while not next_state.can_build_clay_robot(bp):
                next_state = state.tick()
            next_state = state.build_clay_robot()
            next_states.append(next_state)

        next_states = []
        if state.should_build_ore_robot(bp):
            next_state = state
            while not next_state.can_build_ore_robot(bp):
                next_state = state.tick()
            next_state = state.build_ore_robot()
            next_states.append(next_state)

        next_states = [(s.estimate_upper_bound(bp), s) for s in next_states]
        next_states.sort(key=lambda s: s[0], reverse=True)

        curr_max = 0
        for bound, state in next_states:
            if bound < curr_max or bound < global_max:
                continue
            curr_max = max(curr_max, _max_geodes(state))

        states[state] = curr_max
        global_max = max(global_max, curr_max)
        return curr_max

    #for i in range(10, 24):
    #    print(i, _max_geodes(GameState(i, Resources(), Resources(ore=1))), global_max)

    return _max_geodes(GameState(24, Resources(), Resources(ore=1)))


    """
    max_so_far = 0
    states: 'SimpleQueue[GameState]' = SimpleQueue()
    states.put(GameState(24, Resources(), Resources(ore=1)))
    while not states.empty():
        curr = states.get()
        if curr.minutes_left == 0:
            if curr.resources.geodes > max_so_far:
                max_so_far = curr.resources.geodes
        else:
            next_states: 'list[GameState]' = [curr.tick()]
            if curr.can_build_geode_robot(bp):
                next_states.append(curr.build_geode_robot(bp))
            if curr.can_build_obsidian_robot(bp):
                next_states.append(curr.build_obsidian_robot(bp))
            if curr.can_build_clay_robot(bp):
                next_states.append(curr.build_clay_robot(bp))
            if curr.can_build_ore_robot(bp):
                next_states.append(curr.build_ore_robot(bp))
            for state in next_states:
                if state.estimate_upper_bound(bp) > max_so_far:
                    states.put(state)
    return max_so_far
    """

print(evaluate_blueprint(blueprints[0]))
