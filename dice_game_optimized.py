import random

def get_positive_int(prompt, min_value=1):
    """Get a positive integer from user with validation."""
    while True:
        try:
            value = int(input(prompt))
            if value >= min_value:
                return value
            print(f"Please enter a number >= {min_value}")
        except ValueError:
            print("Please enter a valid number")

def get_player_names(num_players):
    """Get unique, non-empty player names."""
    names = set()
    for i in range(1, num_players + 1):
        while True:
            name = input(f"Player {i} name: ").strip()
            if name and name not in names:
                names.add(name)
                break
            elif not name:
                print("Name cannot be empty")
            else:
                print("Name already taken")
    return list(names)

def roll_dice():
    """Roll two dice and return individual values and total."""
    dice1, dice2 = random.randint(1, 6), random.randint(1, 6)
    return dice1, dice2, dice1 + dice2

def main():
    print("Dice Rolling Game!")
    print("Roll two dice and try to get the highest total!")
    
    players = get_positive_int("How many players? ")
    rounds = get_positive_int("How many rounds? ", 1)
    
    names = get_player_names(players)
    scores = {name: 0 for name in names}
    
    for round_num in range(1, rounds + 1):
        print(f"\nRound {round_num}:")
        for name in names:
            input(f"{name}, press Enter to roll dice...")
            dice1, dice2, total = roll_dice()
            scores[name] += total
            print(f"{name} rolled {dice1} and {dice2} = {total}")
    
    print("\nFinal Scores:")
    for name, score in scores.items():
        print(f"{name}: {score}")
    
    winner = max(scores, key=scores.get)
    print(f"\n{winner} wins!")

if __name__ == "__main__":
    main()