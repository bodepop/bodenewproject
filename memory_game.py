import random
import time

colors = ["red", "blue", "green", "yellow", "purple", "orange"]
sequence = []
level = 1

print("Memory Game! Watch the sequence and repeat it.")

while True:
    sequence.append(random.choice(colors))
    
    print(f"\nLevel {level}")
    print("Watch carefully...")
    time.sleep(1)
    
    for color in sequence:
        print(color.upper())
        time.sleep(1)
    
    print("\nNow repeat the sequence:")
    for i in range(len(sequence)):
        guess = input(f"Color {i+1}: ").lower()
        if guess != sequence[i]:
            print(f"Wrong! You reached level {level}")
            exit()
    
    print("Correct! Next level...")
    level += 1
    time.sleep(1)