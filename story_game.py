print("Story Building Game!")
print("Let's create a story together. Fill in the blanks:")

name = input("Enter a name: ")
animal = input("Enter an animal: ")
place = input("Enter a place: ")
adjective = input("Enter an adjective: ")
food = input("Enter a food: ")
color = input("Enter a color: ")
number = input("Enter a number: ")

story = f"""
Once upon a time, there was a {adjective} person named {name}.
{name} had a pet {animal} that was {color} and loved to eat {food}.
One day, they went to {place} and found {number} magical treasures.
The {animal} was so excited that it danced for {number} hours!
They all lived happily ever after.
"""

print("\nHere's your story:")
print(story)