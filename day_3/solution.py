from pathlib import Path

USE_SAMPLE_INPUT = False
in_path = Path.cwd() / 'input.txt'

if USE_SAMPLE_INPUT:
    rucksacks = [
        'vJrwpWtwJgWrhcsFMMfFFhFp',
        'jqHRNqRjqzjGDLGLrsFMfFZSrLrFZsSL',
        'PmmdzqPrVvPwwTWBwg',
        'wMqvLMZHhHMvwLHjbvcjnnSBnvTQFn',
        'ttgJtRGJQctTZtZT',
        'CrZsJsPPZsGzwwsLwLmpwMDw',
    ]
else:
    with in_path.open('r') as inf:
        rucksacks = [line.strip() for line in inf.readlines()]

def item_to_priority(item):
    assert len(item) == 1
    itemcode = ord(item)

    if itemcode >= ord('a') and itemcode <= ord('z'):
        itemcode = itemcode - ord('a') + 1
    elif itemcode >= ord('A') and itemcode <= ord('Z'):
        itemcode = itemcode - ord('A') + 27
    else:
        raise ValueError(f'Invalid item {item}')

    return itemcode

common_items = []

for sack in rucksacks:
    split_point = len(sack) // 2
    c1 = sack[:split_point]
    c2 = sack[split_point:]

    for item in c1:
        if item in c2:
            common_items.append(item)
            break

print("Part 1:", sum([item_to_priority(item) for item in common_items]))

badges = []
for i in range(0, len(rucksacks), 3):
    sack_1 = set(rucksacks[i])
    sack_2 = set(rucksacks[i+1])
    sack_3 = set(rucksacks[i+2])

    badge = sack_1.intersection(sack_2).intersection(sack_3)
    assert len(badge) == 1
    badge = badge.pop()

    badges.append(badge)

print("Part 2:", sum([item_to_priority(item) for item in badges]))
