"""Contains multiple different algorithms and helpful functions
table of content:
    rsolv // recursive solving algorithm
    print sudoku in terminal"""

## rsolv // recursive solving algorithm
def rsolv_recursive_solving(input_matrix):
    """rsolv_recursive_solving(input_matrix)
    -> True (when completly solved)

    alters input_matrix so it gets solved

    input_matrix needs to be arrays within an array
    gets position of next space, if False we are finished
    loops number from 1 to end, checks each on that position
    if number is valid, number gets placed into position
    recursive call until either finished or we find a deadend
    if deadend we jump back and overwrite position with 0
    then number gets incremented and we repeat validation etc..
    deadends are validation violations in recursive calls"""
    position = rsolv_find_next_space(input_matrix)
    if position == False:
        return True
    x_pos = position[0]
    y_pos = position[1]
    for number in range(1,len(input_matrix[0])+1):
        if rsolv_validation_check(input_matrix, number, position):
            input_matrix[x_pos][y_pos] = number
            if rsolv_recursive_solving(input_matrix):
                return True
            input_matrix[x_pos][y_pos] = 0
    return False

## looks for next empty field
def rsolv_find_next_space(input_matrix):
    """rsolv_find_next_space(input_matrix)
    -> coordinate / False

    part of rsolv_recursive_solving
    input_matrix needs to be arrays within an array
    returns position of next space as tuple
    returns False if theres no next space"""
    for i in range(len(input_matrix[0])):
        for j in range(len(input_matrix)):
            if input_matrix[i][j] == 0:
                return (i,j)
    return False

## checks if a guessed number violates the rules
def rsolv_validation_check(input_matrix, number, position):
    """rsolv_validation_check(input_matrix, number, position)
    -> True / False

    part of rsolv_recursive_solving
    input_matrix needs to be arrays within an array
    position needs to be a tuple
    number should be an integer
    checks if number is valid at position"""

    ## checking row
    for i in range(len(input_matrix[0])):
        if input_matrix[position[0]][i] == number and position[1] != i:
            return False

    ## checking column
    for (i, row) in enumerate(input_matrix, start=0):
        if row[position[1]] == number and position[0] != i:
            return False

    ## checking field
    field = (position[0]//3,position[1]//3)
    for i in range(field[0]*3, field[0]*3+3):
        for j in range(field[1]*3, field[1]*3+3):
            if input_matrix[i][j] == number and position != (i,j):
                return False

    ## all checks valid
    return True

## print sudoku in terminal
def print_sudoku(input_matrix):
    """print_sudoku(input_matrix)
    -> None

    input_matrix needs to be arrays within an array
    prints formatted matrix in command line"""

    for i in range(len(input_matrix)):
        if i%3 == 0 and i != 0:
            print("-"*21)
        for j in range(len(input_matrix[0])):
            if j % 3 == 0 and j != 0:
                print("| ", end="")
            if j == 8:
                print(input_matrix[i][j])
            else:
                print(str(input_matrix[i][j]) + " ", end="")
    return
