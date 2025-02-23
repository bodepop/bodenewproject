import random

def number_guessing_game():
    # Generate a random number between 1 and 100
    secret_number = random.randint(1, 100)
    attempts = 0
    max_attempts = 10

    print("Welcome to the Number Guessing Game!")
    print(f"I'm thinking of a number between 1 and 100. You have {max_attempts} attempts to guess it.")

    while attempts < max_attempts:
        try:
            # Get the player's guess
            guess = int(input("Enter your guess: "))
            attempts += 1

            # Check if the guess is correct
            if guess == secret_number:
                print(f"Congratulations! You've guessed the number in {attempts} attempts!")
                return
            elif guess < secret_number:
                print("Too low! Try a higher number.")
            else:
                print("Too high! Try a lower number.")
            
            # Inform the player of remaining attempts
            print(f"You have {max_attempts - attempts} attempts left.")

        except ValueError:
            print("Please enter a valid number.")

    print(f"Sorry, you've run out of attempts. The number was {secret_number}.")

# Run the game
if __name__ == "__main__":
    number_guessing_game()
    
    while True:
        play_again = input("Do you want to play again? (yes/no): ").lower()
        if play_again != 'yes':
            print("Thanks for playing! Goodbye!")
            break
        number_guessing_game()