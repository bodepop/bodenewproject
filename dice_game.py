import random

print("Dice Rolling Game!")
print("Roll two dice and try to get the highest total!")

players = int(input("How many players? "))
scores = {}

for player in range(1, players + 1):
    name = input(f"Player {player} name: ")
    scores[name] = 0

rounds = 3
for round_num in range(1, rounds + 1):
    print(f"\nRound {round_num}:")
    
    for name in scores:
        input(f"{name}, press Enter to roll dice...")
        dice1 = random.randint(1, 6)
        dice2 = random.randint(1, 6)
        total = dice1 + dice2
        scores[name] += total
        print(f"{name} rolled {dice1} and {dice2} = {total}")

print("\nFinal Scores:")
for name, score in scores.items():
    print(f"{name}: {score}")

winner = max(scores, key=scores.get)
print(f"\n{winner} wins!")