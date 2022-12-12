from pathlib import Path
import copy

USE_SAMPLE_INPUT = False
in_path = Path.cwd() / 'input.txt'

sample_input = """
Monkey 0:
  Starting items: 79, 98
  Operation: new = old * 19
  Test: divisible by 23
    If true: throw to monkey 2
    If false: throw to monkey 3

Monkey 1:
  Starting items: 54, 65, 75, 74
  Operation: new = old + 6
  Test: divisible by 19
    If true: throw to monkey 2
    If false: throw to monkey 0

Monkey 2:
  Starting items: 79, 60, 97
  Operation: new = old * old
  Test: divisible by 13
    If true: throw to monkey 1
    If false: throw to monkey 3

Monkey 3:
  Starting items: 74
  Operation: new = old + 3
  Test: divisible by 17
    If true: throw to monkey 0
    If false: throw to monkey 1
""".strip()

def maybe_print(should_print, message):
    if should_print:
        print(message)

disable_global_worry_operation = False
def global_worry_operation(item):
    if disable_global_worry_operation:
        return item
    else:
        return item // 3

class Monkey:
    def __init__(self, monkey_id, items, operation, test, true_monkey_idx, false_monkey_idx):
        self.monkey_id = monkey_id
        self.items = items
        self.operation = operation
        self.test = test
        self.true_monkey_idx = true_monkey_idx
        self.false_monkey_idx = false_monkey_idx
        self.inspect_count = 0

        self.mod_base = -1

    def set_mod_base(self, mod_base):
        self.mod_base = mod_base

    @staticmethod
    def from_str(monkey_str):
        lines = [line.strip() for line in monkey_str.split("\n")]
        monkey_id = int(lines[0][7:-1])
        starting_items = [int(item) for item in (lines[1][16:]).split(',')]
        operation = lines[2][17:]
        test = int(lines[3][19:])
        true_monkey_idx = int(lines[4][25:])
        false_monkey_idx = int(lines[5][26:])
        return Monkey(monkey_id, starting_items, operation, test, true_monkey_idx, false_monkey_idx)

    def reference_monkeys(self, monkeys):
        self.true_monkey = monkeys[self.true_monkey_idx]
        self.false_monkey = monkeys[self.false_monkey_idx]

    def catch(self, item):
        self.items.append(item)

    def apply_operation(self, item):
        self.inspect_count += 1
        old = item
        result = eval(self.operation)
        if self.mod_base > 0:
            result = result % mod_base
        return result

    def take_turn(self, quiet=True):
        items = self.items
        self.items = []
        maybe_print(not quiet, f"Monkey {self.monkey_id}:")
        for item in items:
            maybe_print(not quiet, f"  Monkey inspects an item with a worry level of {item}.")
            item = self.apply_operation(item)
            maybe_print(not quiet, f"    Worry level becomes {item}.")
            item = global_worry_operation(item)
            maybe_print(not quiet, f"    Monkey gets bored with item. Worry level is divided by 3 to {item}.")
            if item % self.test == 0:
                maybe_print(not quiet, f"    Current worry level is divisible by {self.test}.")
                maybe_print(not quiet, f"    Item with worry level {item} is thrown to monkey {self.true_monkey_idx}.")
                self.true_monkey.catch(item)
            else:
                maybe_print(not quiet, f"    Current worry level is not divisible by {self.test}.")
                maybe_print(not quiet, f"    Item with worry level {item} is thrown to monkey {self.false_monkey_idx}.")
                self.false_monkey.catch(item)

    def __str__(self):
        return f"Monkey {self.monkey_id}:\n" \
            + "  Items: " + ', '.join([str(itm) for itm in self.starting_items]) + '\n' \
            + "  Operation: new = " + self.operation + '\n' \
            + f"  Test: divisible by {self.test}\n" \
            + f"    If true: throw to monkey {self.true_monkey_idx}\n" \
            + f"    If false: throw to monkey {self.false_monkey_idx}"


if USE_SAMPLE_INPUT:
    orig_monkeys = [Monkey.from_str(m) for m in sample_input.split("\n\n")]
else:
    with in_path.open("r") as inf:
        orig_monkeys = [Monkey.from_str(m) for m in inf.read().split("\n\n")]

monkeys = copy.deepcopy(orig_monkeys)
for monkey in monkeys:
    monkey.reference_monkeys(monkeys)


for round in range(20):
    for monkey in monkeys:
        monkey.take_turn()
    if USE_SAMPLE_INPUT:
        print(f"After round {round+1}, the monkeys are holding items with these worry levels:")
        for monkey in monkeys:
            print(f"Monkey {monkey.monkey_id}: {', '.join([str(item) for item in monkey.items])}")
        print()

for monkey in monkeys:
    print(f'Monkey {monkey.monkey_id} inspected items {monkey.inspect_count} times.')

sorted_monkeys = sorted(monkeys, key=lambda m: m.inspect_count, reverse=True)
print("Part 1:", sorted_monkeys[0].inspect_count * sorted_monkeys[1].inspect_count)

# Part 2

monkeys = copy.deepcopy(orig_monkeys)
for monkey in monkeys:
    monkey.reference_monkeys(monkeys)

# We need to find a way to prevent worry levels from becoming too large. If we just leave the
# worry levels as-is, they rapidly become so large that it takes a significant amount of processor
# time to perform even basic multiplication or addition.
#
# The goal is to find a sort of "representative" number that is smaller, but will satisfy the
# divisibility tests in the same way as the original number. Also, this property needs to be
# maintained across addition and multiplication.
#
# Let f(x) be the function that returns the representative number.
# Let S be the set of integers used by the monkeys in their various divisibility tests.
# We need the following to be true:
#   1. For any x and any s in S, then if x = 0 mod s, then f(x) = 0 mod s
#   2. For any x and any s in S, then if x != 0 mod s, then f(x) != 0 mod s
#   3. For any x,k and any s in S, then if (x+k) = 0 mod s, then f(f(x) + k) = 0 mod s
#   4. For any x,k and any s in S, then if (x+k) != 0 mod s, then f(f(x) + k) != 0 mod s
#   5. For any x,k and any s in S, then if kx = 0 mod s, then f(k*f(x)) = 0 mod s
#   6. For any x,k and any s in S, then if kx != 0 mod s, then f(k*f(x)) != 0 mod s
#
# Let m be the product of all values in S.
# It can be shown (aka, I don't want to prove it rn) that f(x) = x % m satisfies the above
# properties.

mod_base = 1
for monkey in monkeys:
    mod_base *= monkey.test
for monkey in monkeys:
    monkey.set_mod_base(mod_base)

disable_global_worry_operation = True

for round in range(10000):
    for monkey in monkeys:
        monkey.take_turn()

for monkey in monkeys:
    print(f'Monkey {monkey.monkey_id} inspected items {monkey.inspect_count} times.')

sorted_monkeys = sorted(monkeys, key=lambda m: m.inspect_count, reverse=True)
print("Part 2:", sorted_monkeys[0].inspect_count * sorted_monkeys[1].inspect_count)
