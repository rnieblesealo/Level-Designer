"""
Generator of a random value that does not exist in a list.
"""

from random import randint

exclusions = [2, 4, 6, 8, 10, 12]

def rand_exclusive():
    prospect = randint(0, 12)
    for i in range(len(exclusions)):
        if prospect == exclusions[i]:
            return rand_exclusive()
    return prospect

print(rand_exclusive())