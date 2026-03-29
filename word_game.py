import random

words = ["python", "computer", "game", "coding", "challenge", "mystery", "adventure"]
word = random.choice(words)
guessed = ["_"] * len(word)
wrong_guesses = 0
max_wrong = 6

print("Word Guessing Game!")
print(" ".join(guessed))

while "_" in guessed and wrong_guesses < max_wrong:
    guess = input("Guess a letter: ").lower()
    
    if guess in word:
        for i, letter in enumerate(word):
            if letter == guess:
                guessed[i] = guess
        print("Good guess!")
    else:
        wrong_guesses += 1
        print(f"Wrong! {max_wrong - wrong_guesses} guesses left.")
    
    print(" ".join(guessed))

if "_" not in guessed:
    print("You won!")
else:
    print(f"Game over! The word was: {word}")