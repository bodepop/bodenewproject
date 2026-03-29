import random

questions = [
    ("What color do you get when you mix red and yellow?", "orange"),
    ("How many legs does a spider have?", "8"),
    ("What is the largest planet in our solar system?", "jupiter"),
    ("What animal says 'moo'?", "cow"),
    ("How many days are in a week?", "7"),
    ("What do bees make?", "honey"),
    ("What is 5 + 3?", "8"),
    ("What season comes after winter?", "spring")
]

score = 0
print("Family Trivia Game!")

for question, answer in random.sample(questions, 5):
    user_answer = input(f"{question} ").lower()
    if user_answer == answer:
        print("Correct!")
        score += 1
    else:
        print(f"Wrong! The answer is {answer}")

print(f"Final score: {score}/5")