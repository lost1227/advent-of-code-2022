from pathlib import Path

USE_SAMPLE_INPUT = False
in_path = Path.cwd() / 'input.txt'

sample_input = """
root: pppw + sjmn
dbpl: 5
cczh: sllz + lgvd
zczc: 2
ptdq: humn - dvpt
dvpt: 3
lfqf: 4
humn: 5
ljgn: 2
sjmn: drzm * dbpl
sllz: 4
pppw: cczh / lfqf
lgvd: ljgn * ptdq
drzm: hmdt - zczc
hmdt: 32
"""

if USE_SAMPLE_INPUT:
    input = sample_input.strip()
else:
    with in_path.open("r") as inf:
        input = inf.read().strip()

values = {}
for line in input.split("\n"):
    colonidx = line.index(':')
    name = line[:colonidx]
    values[name] = line[colonidx+2:]

resolved_values = {}
def resolve(key) -> float:
    if key in resolved_values:
        return resolved_values[key]
    if key not in values:
        raise ValueError('Invalid key')
    value = values[key]
    try:
        out = float(value)
    except ValueError:
        lhs, op, rhs = value.split()
        lhs = resolve(lhs)
        rhs = resolve(rhs)
        if op == '+':
            out = lhs + rhs
        elif op == '-':
            out = lhs - rhs
        elif op == '*':
            out = lhs * rhs
        elif op == '/':
            out = lhs / rhs
        else:
            raise ValueError(f'Invalid operation: \'{op}\'')
    resolved_values[key] = out
    return out

print('Part 1:', resolve('root'))

# PART 2
print('\n\n')

values = {}
resolved_values = {}
for line in input.split("\n"):
    colonidx = line.index(':')
    name = line[:colonidx]
    if name == 'humn':
        continue
    values[name] = line[colonidx+2:]

lhs, _, rhs = values['root'].split()
del values['root']

try:
    target_root_val = resolve(rhs)
    backsolve_target = lhs
except ValueError:
    target_root_val = resolve(lhs)
    backsolve_target = rhs

print(f"Need to solve for {backsolve_target} = {target_root_val}")

def resolve_with_humn(key, humn):
    global resolved_values
    resolved_values = {}
    values['humn'] = humn
    out = resolve(key)
    del values['humn']
    return out

DER_EST_DELTA = 0.01

# NEWTON'S METHOD FTW
# https://en.wikipedia.org/wiki/Newton%27s_method
x = 0
for i in range(100):
    print(f"{i}) {x} -> ", end="")
    f_x = resolve_with_humn(backsolve_target, x) - target_root_val
    df_x = (resolve_with_humn(backsolve_target, x+DER_EST_DELTA) - resolve_with_humn(backsolve_target, x-DER_EST_DELTA)) / DER_EST_DELTA

    x = x - (f_x / df_x)

    print(x)

