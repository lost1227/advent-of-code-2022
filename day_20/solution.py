from pathlib import Path

USE_SAMPLE_INPUT = False
in_path = Path.cwd() / 'input.txt'

sample_input = """
1
2
-3
3
-2
0
4
""".strip()

if USE_SAMPLE_INPUT:
    input = sample_input.strip()
else:
    with in_path.open("r") as inf:
        input = inf.read().strip()

input = [int(n) for n in input.split('\n')]

class DLLNode:
    def __init__(self, value: int, next: 'DLLNode|None' = None, prev: 'DLLNode|None' = None):
        self.value = value
        self.next = next
        self.prev = prev

    @property
    def subsequent_values(self) -> 'list[int]':
        out = [self.value]
        curr = self.next
        while curr is not None and curr != self:
            out.append(curr.value)
            curr = curr.next
        return out

    def __str__(self):
        return "DLLNode: " + ", ".join([str(n) for n in self.subsequent_values])


head = None
curr = None
for n in input:
    if head is None:
        head = curr = DLLNode(int(n))
    else:
        curr.next = DLLNode(int(n), prev=curr)
        curr = curr.next

tail = curr
tail.next = head
head.prev = tail

to_mix: 'list[DLLNode]' = [head]
curr = head.next
while curr != head:
    to_mix.append(curr)
    curr = curr.next

if USE_SAMPLE_INPUT:
    print('Initial arrangement:')
    print(', '.join([str(n) for n in head.subsequent_values]))
    print()

for node in to_mix:
    value = node.value
    if value == 0:
        if USE_SAMPLE_INPUT:
            print("0 does not move:")
            print(', '.join([str(n) for n in head.subsequent_values]))
            print()
        continue

    if node == head:
        head = node.next

    node.prev.next = node.next
    node.next.prev = node.prev

    curr = node
    if value > 0:
        for _ in range(value):
            curr = curr.next
    else:
        assert value < 0
        for _ in range(-value + 1):
            curr = curr.prev

    node.next = curr.next
    node.prev = curr

    node.next.prev = node
    node.prev.next = node

    if USE_SAMPLE_INPUT:
        print(f"{node.value} moves between {node.prev.value} and {node.next.value}:")
        print(', '.join([str(n) for n in head.subsequent_values]))
        print()

zero = head
while zero.value != 0:
    zero = zero.next

first = zero
for _ in range(1000):
    first = first.next
print("first:", first.value)

second = first
for _ in range(1000):
    second = second.next
print("second:", second.value)

third = second
for _ in range(1000):
    third = third.next
print("third:", third.value)

print()
print("Part 1:", first.value + second.value + third.value)

# PART 2
print("\n\n")

DECRYPTION_KEY = 811589153

head = None
curr = None
for n in input:
    if head is None:
        head = curr = DLLNode(int(n) * DECRYPTION_KEY)
    else:
        curr.next = DLLNode(int(n) * DECRYPTION_KEY, prev=curr)
        curr = curr.next

tail = curr
tail.next = head
head.prev = tail

to_mix: 'list[DLLNode]' = [head]
curr = head.next
while curr != head:
    to_mix.append(curr)
    curr = curr.next

if USE_SAMPLE_INPUT:
    print('Initial arrangement:')
    print(', '.join([str(n) for n in head.subsequent_values]))
    print()

num_values = len(to_mix)

for i in range(10):
    for node in to_mix:
        value = node.value
        moves = value % (num_values-1)
        if moves == 0:
            continue

        if node == head:
            head = node.next

        node.prev.next = node.next
        node.next.prev = node.prev

        curr = node
        if moves > 0:
            for _ in range(moves):
                curr = curr.next
        else:
            assert moves < 0
            for _ in range(-moves + 1):
                curr = curr.prev

        node.next = curr.next
        node.prev = curr

        node.next.prev = node
        node.prev.next = node

    if USE_SAMPLE_INPUT:
        print(f'After {i+1} rounds of mixing:')
        print(', '.join([str(n) for n in head.subsequent_values]))
        print()

zero = head
while zero.value != 0:
    zero = zero.next

first = zero
for _ in range(1000):
    first = first.next
print("first:", first.value)

second = first
for _ in range(1000):
    second = second.next
print("second:", second.value)

third = second
for _ in range(1000):
    third = third.next
print("third:", third.value)

print()
print("Part 2:", first.value + second.value + third.value)
