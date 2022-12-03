from pathlib import Path

USE_SAMPLE_INPUT = False

in_path = Path.cwd() / 'input.txt'

other_moves = {
    'A': 1, # Rock
    'B': 2, # Paper
    'C': 3  # Scissors
}

your_moves = {
    'X': 1, # Rock / lose
    'Y': 2, # Paper / draw
    'Z': 3  # Scissors / win
}

def calculate_score(move):
    score = move[1]
    if move[0] == move[1]:
        # draw
        score += 3
    elif (move[1] % 3) == (move[0] - 1):
        # loss
        score += 0
    else:
        # win
        score += 6
    return score

moves = []

if USE_SAMPLE_INPUT:
    moves = [
        (other_moves['A'], your_moves['Y']),
        (other_moves['B'], your_moves['X']),
        (other_moves['C'], your_moves['Z'])
    ]
else:
    with in_path.open("r") as inf:
        for line in inf.readlines():
            line = line.strip()
            other_move, your_move = line.split()
            moves.append((other_moves[other_move], your_moves[your_move]))

total_score = sum([calculate_score(move) for move in moves])
print("Part 1:", total_score)

def calculate_move(move):
    opponent_move = move[0]
    required_outcome = move[1]

    if required_outcome == 1:
        # lose
        your_move = ((opponent_move + 1) % 3) + 1
    elif required_outcome == 2:
        # draw
        your_move = opponent_move
    else:
        # win
        your_move = (opponent_move % 3) + 1

    return (opponent_move, your_move)

moves_2 = [calculate_move(move) for move in moves]
total_score_2 = sum([calculate_score(move) for move in moves_2])
print("Part 2:", total_score_2)
