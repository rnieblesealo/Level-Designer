"""
Algorithm for copying elements from a 1D iterable into a 2D matrix.

For every element in the 1D iterable, we scan the matrix for an empty slot.
If we find one, we copy the 1D iterable's element to that slot.
We repeat the procedure for all elements in the 1D iterable.

"""

import numpy

symbols = ('#', '$', '^', '*', 'A', 'B', 'C')
matrix = numpy.full((5, 5), ' ', str)

# Utilize a method like this one; its the most comprehensive (and brain-efficient) way of doing things!
def place_at_empty(symbol):
    for y in range(matrix.shape[0]):
        for x in range(matrix.shape[1]):
            if matrix[y][x] == ' ':
                matrix[y][x] = symbol
                return

for symbol in symbols:
    place_at_empty(symbol)

print(matrix)