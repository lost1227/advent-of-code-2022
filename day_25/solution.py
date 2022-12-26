from pathlib import Path

USE_SAMPLE_INPUT = False
in_path = Path.cwd() / 'input.txt'

sample_input = """
1=-0-2
12111
2=0=
21
2=01
111
20012
112
1=-1=
1-12
12
1=
122
"""

if USE_SAMPLE_INPUT:
    input = sample_input.strip()
else:
    with in_path.open("r") as inf:
        input = inf.read().strip()

snafu_to_int = {
    '2': 2,
    '1': 1,
    '0': 0,
    '-': -1,
    '=': -2
}

int_to_snafu = {
    2: '2',
    1: '1',
    0: '0',
    -1: '-',
    -2: '='
}

def adder(a, b, carry='0'):
    value = snafu_to_int[a] + snafu_to_int[b] + snafu_to_int[carry]
    carry_out = '0'
    if value > 2:
        value -= 5
        carry_out = '1'
    elif value < -2:
        value += 5
        carry_out = '-'

    return (int_to_snafu[value], carry_out)

def add(snafu1: str, snafu2: str) -> str:
    count = len(snafu1)
    if len(snafu1) > len(snafu2):
        snafu2 = ('0' * (len(snafu1) - len(snafu2))) + snafu2
    elif len(snafu2) > len(snafu1):
        count = len(snafu2)
        snafu1 = ('0' * (len(snafu2) - len(snafu1))) + snafu1

    carry = '0'
    out = ''
    for i in range(count-1, -1, -1):
        result, carry = adder(snafu1[i], snafu2[i], carry)
        out += result

    if carry != '0':
        out += carry

    out = out[::-1]

    return out

def snafu_to_decimal(snafu: str) -> int:
    result = 0
    for i, c in enumerate(snafu[::-1]):
        result += (snafu_to_int[c] * (5**i))
    return result

def test_add(snafu1, snafu2):
    print("=== TEST ===")
    dec1 = snafu_to_decimal(snafu1)
    dec2 = snafu_to_decimal(snafu2)
    result = add(snafu1, snafu2)
    resdec = snafu_to_decimal(result)
    print(f"'{snafu1}' + '{snafu2}' = '{result}' ({resdec})")
    print(f"{dec1} + {dec2} = {dec1 + dec2}")
    assert dec1 + dec2 == resdec

value = "0"
for snafu in input.split("\n"):
    value = add(snafu, value)

print(f"Part 1: '{value}' ({snafu_to_decimal(value)})")
