from pathlib import Path

USE_SAMPLE_INPUT = False
in_path = Path.cwd() / 'input.txt'

if USE_SAMPLE_INPUT:
    input = "mjqjpqmgbljsphdztnvjfqwrcgsmlb"
else:
    with in_path.open("r") as inf:
        input = inf.readlines()[0]

def check_uniq(str):
    for i in range(len(str)-1):
        if str[i] in str[i+1:]:
            return False
    return True

def first_uniq_substr(instr, strlen):
    for i in range(strlen, len(instr)):
        substr = instr[i-strlen: i]
        if check_uniq(substr):
            return (i, substr)

print("Part 1:", first_uniq_substr(input, 4))
print("Part 2:", first_uniq_substr(input, 14))
