from pathlib import Path

USE_SAMPLE_INPUT = False
in_path = Path.cwd() / 'input.txt'

sample_input = """
[1,1,3,1,1]
[1,1,5,1,1]

[[1],[2,3,4]]
[[1],4]

[9]
[[8,7,6]]

[[4,4],4,4]
[[4,4],4,4,4]

[7,7,7,7]
[7,7,7]

[]
[3]

[[[]]]
[[]]

[1,[2,[3,[4,[5,6,7]]]],8,9]
[1,[2,[3,[4,[5,6,0]]]],8,9]
""".strip()

if USE_SAMPLE_INPUT:
    input = sample_input.split("\n\n")
else:
    with in_path.open("r") as inf:
        input = inf.read().strip().split("\n\n")

enable_printd = True

class NoComparisonResult(Exception):
    pass

def printd(msg, depth):
    if enable_printd:
        print(("  " * depth) + msg)

def packet_lt(a, b, depth=0):
    printd(f"- Compare {a} vs {b}", depth)
    if isinstance(a, int) and isinstance(b, int):
        if a < b:
            printd("- Left side is smaller, so inputs are in the right order", depth+1)
            return True
        else:
            printd("- Right side is smaller, so inputs are not in the right order", depth+1)
            return False
    elif isinstance(a, list) and isinstance(b, list):
        for i in range(min(len(a), len(b))):
            if a[i] == b[i]:
                printd(f"- Compare {a[i]} vs {b[i]} (=)", depth+1)
            else:
                try:
                    if packet_lt(a[i], b[i], depth+1):
                        printd("- Left side is smaller, so inputs are in the right order", depth+1)
                        return True
                    else:
                        printd("- Right side is smaller, so inputs are not in the right order", depth+1)
                        return False
                except NoComparisonResult:
                    pass
        if len(a) < len(b):
            printd("- Left side ran out of items, so inputs are in the right order", depth+1)
            return True
        elif len(b) < len(a):
            printd("- Right side ran out of items, so inputs are not in the right order", depth+1)
            return False
    elif isinstance(a, list) and isinstance(b, int):
        printd(f"- Mixed types; convert right to [{b}] and retry comparison", depth+1)
        return packet_lt(a, [b], depth+1)
    elif isinstance(a, int) and isinstance(b, list):
        printd(f"- Mixed types; convert left to [{a}] and retry comparison", depth+1)
        return packet_lt([a], b, depth+1)

    raise NoComparisonResult()

pairs = []

for pair in input:
    first, second = pair.split("\n")
    first = eval(first)
    second = eval(second)

    pairs.append((first, second))

in_order_indices = []
for i, (first, second) in enumerate(pairs):
    print(f"== Pair {i+1} ==")
    if packet_lt(first, second):
        in_order_indices.append(i+1)
    print()

print("In order indices:", ", ".join(str(i) for i in in_order_indices))
print("Part 1:", sum(in_order_indices))

# PART 2

def mergesort(a):
    if len(a) == 1:
        return a
    mid = len(a) // 2
    sorted_left = mergesort(a[:mid])
    sorted_right = mergesort(a[mid:])

    merged = []
    i = j = 0
    while i < len(sorted_left) and j < len(sorted_right):
        if packet_lt(sorted_left[i], sorted_right[j]):
            merged.append(sorted_left[i])
            i += 1
        else:
            merged.append(sorted_right[j])
            j += 1
    while i < len(sorted_left):
        merged.append(sorted_left[i])
        i += 1
    while j < len(sorted_right):
        merged.append(sorted_right[j])
        j += 1

    for i in range(len(merged)):
        for j in range(i+1, len(merged)):
            assert packet_lt(merged[i], merged[j])
    return merged


packets = []
for first, second in pairs:
    packets.append(first)
    packets.append(second)

enable_printd = False

divider_packets = [[[2]], [[6]]]

sorted_packets = mergesort(packets + divider_packets)

decoder_key = 1
for i, packet in enumerate(sorted_packets):
    if packet == [[2]] or packet == [[6]]:
        decoder_key *= (i+1)
        print("-> ", end='')
    else:
        print('   ', end='')
    print(f"{ i:2d})", packet)

print("Part 2:", decoder_key)
