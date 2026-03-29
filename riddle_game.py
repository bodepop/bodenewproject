import random

riddles = [
    ("I have keys but no locks. I have space but no room. What am I?", ["keyboard"]),
    ("What gets wet while drying?", ["towel"]),
    ("What has hands but cannot clap?", ["clock", "watch"]),
    ("What goes up but never comes down?", ["age"]),
    ("What can you catch but not throw?", ["cold", "flu"]),
    ("What has one eye but cannot see?", ["needle"]),
    ("What gets bigger the more you take away from it?", ["hole"]),
    ("What runs but never walks?", ["water", "river"])
]

score = 0
print("Family Riddle Game! (type 'skip' to skip, 'quit' to exit)")

for riddle, answers in random.sample(riddles, min(4, len(riddles))):
    print(f"\n{riddle}")
    guess = input("Your answer: ").strip().lower()
    
    if guess == 'quit':
        break
    elif guess == 'skip':
        print(f"Skipped! Answer: {answers[0]}")
        continue
    
    if any(ans in guess for ans in answers):
        print("Correct!")
        score += 1
    else:
        print(f"The answer is: {answers[0]}")

print(f"\nFinal score: {score} correct!")