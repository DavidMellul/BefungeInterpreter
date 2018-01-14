import os.path
import operator
import random
from enum import Enum

"""
    Basic stack implementation
"""


class Stack:
    data = list()

    def __init__(self):
        pass

    def push(self, value):
        self.data.append(value)

    def pop(self):
        if len(self.data) == 0:
            return 0
        else:
            return int(self.data.pop())

    def peek(self):
        if len(self.data) == 0:
            return 0
        else:
            return self.data[-1]

    # Duplicate top value
    def dup(self):
        self.push(self.peek())

    # Swap top values
    def swap(self):
        a, b = self.pop(), self.pop()
        self.push(a)
        self.push(b)

    def __len__(self):
        return len(self.data)

    def __str__(self):
        return str(self.data)


"""
    Direction of the program reader
"""


class Direction(Enum):
    LEFT = '<'
    RIGHT = '>'
    UP = '^'
    DOWN = 'v'


"""
    Instructions supported
"""


class Instruction(Enum):
    ADD = '+'
    SUB = '-'
    DIV = '/'
    MUL = '*'
    MOD = '%'
    NOT = '!'
    JMP = '#'
    DUP = ':'
    HIF = '_'
    VIF = '|'
    RND = '?'
    POP = '$'
    GET = 'g'
    PUT = 'p'
    READ_INTEGER = '&'
    READ_CHAR = '~'
    GREATER = '`'
    SWAP = '\\'
    INTEGER_OUTPUT = '.'
    ASCII_OUTPUT = ','
    TOGGLE_ASCII_MODE = '"'
    END_PROGRAM = '@'


"""
    Lookup table : string -> arithmetic operator
"""


def get_operator(symbol):
    return {
        Instruction.ADD.value: operator.add,
        Instruction.SUB.value: operator.sub,
        Instruction.DIV.value: operator.truediv,
        Instruction.MUL.value: operator.mul,
        Instruction.MOD.value: operator.mod
    }[symbol]


"""
   Ask the user for the filepath of his Befunge-93 source 
"""


def retrieve_program_source_path():
    filename = input("Source file to process : ")

    if not (os.path.isfile(filename)):
        return retrieve_program_source_path()
    else:
        return filename


"""
    Befunge-93 source file -> Matrix
"""


def source_to_matrix(source):
    with open(source) as program:
        lines = [line.rstrip('\n') for line in program]
        source_as_matrix = [[line[i] for i in range(len(line))] for line in lines]
        fix_lines_length(source_as_matrix)
        return source_as_matrix


"""
    Make all the lines the same length
"""


def fix_lines_length(program_matrix):
    max_len = max([len(line) for line in program_matrix])

    for line in program_matrix:
        line_length = len(line)
        if line_length < max_len:
            for i in range(0, max_len - line_length):
                line.append(' ')


"""
    Main method, execute each instruction in the matrix
    Python has no switch :( 
    Dict trick is not flexlible enough
"""


def process_code(program_matrix):
    # Program stack
    program_stack = Stack()

    # Cursor starting position
    cursor_x, cursor_y = 0, 0

    # Cursor starting direction
    cursor_direction = Direction.RIGHT.value

    # Self explanatory
    in_ascii_mode = False
    program_end_reached = False
    should_skip = False

    while not program_end_reached:
        if should_skip:
            should_skip = False
        else:
            # Check that cursor position is within matrix bounds

            if cursor_y == len(program_matrix) and cursor_direction == Direction.DOWN.value:
                cursor_y = 0
            elif cursor_y < 0 and cursor_direction == Direction.UP.value:
                cursor_y = len(program_matrix) - 1
            elif cursor_x == len(program_matrix[cursor_y]) and cursor_direction == Direction.RIGHT.value:
                cursor_x = 0
            elif cursor_x < 0 and cursor_direction == Direction.LEFT.value:
                cursor_x = len(program_matrix[cursor_y]) - 1

            # Retrieve the instruction
            instruction = program_matrix[cursor_y][cursor_x]
            # print('{} ... ({},{}) => {}'.format(program_stack, cursor_y, cursor_x, instruction))

            if instruction == Instruction.TOGGLE_ASCII_MODE.value:
                in_ascii_mode = not in_ascii_mode

            # ASCII mode activated
            elif in_ascii_mode:
                program_stack.push(ord(instruction))

            # Direction changer
            elif instruction in [d.value for d in [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]]:
                cursor_direction = instruction

            # Toggle ASCII mode


            # Numbers
            elif instruction.isdigit() and int(instruction) in range(0, 10):
                program_stack.push(int(instruction))

            # Mathematics operators
            elif instruction in [i.value for i in [Instruction.ADD, Instruction.SUB, Instruction.MUL, Instruction.DIV,
                                                   Instruction.MOD]]:
                a, b = program_stack.pop(), program_stack.pop()
                program_stack.push(get_operator(instruction)(b, a))

            # Bridge -> Jump to the next instruction
            elif instruction == Instruction.JMP.value:
                should_skip = True

            # Duplication of the stack's peek
            elif instruction == Instruction.DUP.value:
                program_stack.dup()

            # Not
            elif instruction == Instruction.NOT.value:
                program_stack.push(not (program_stack.pop()))

            # Greather Than
            elif instruction == Instruction.GREATER.value:
                a, b = program_stack.pop(), program_stack.pop()
                program_stack.push(1 if b > a else 0)

            # Random Direction
            elif instruction == Instruction.RND.value:
                cursor_direction = random.choice(
                    [d.value for d in {Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT}])

            # Horizontal IF
            elif instruction == Instruction.HIF.value:
                value = program_stack.pop()
                cursor_direction = Direction.RIGHT.value if value == 0 else Direction.LEFT.value

            # Vertical IF
            elif instruction == Instruction.VIF.value:
                value = program_stack.pop()
                cursor_direction = Direction.DOWN.value if value == 0 else Direction.UP.value

            # Pop and output as integer
            elif instruction == Instruction.INTEGER_OUTPUT.value:
                print(int(program_stack.pop()), end='')

            # Pop and output as ASCII
            elif instruction == Instruction.ASCII_OUTPUT.value:
                print(chr(program_stack.pop()), end='')

            # Swap
            elif instruction == Instruction.SWAP.value:
                program_stack.swap()

            # Pop
            elif instruction == Instruction.POP.value:
                program_stack.pop()

            # Read integer
            elif instruction == Instruction.READ_INTEGER.value:
                program_stack.push(int(input("Enter a number: ")))

            # Read character
            elif instruction == Instruction.READ_CHAR.value:
                program_stack.push(ord(input("Enter a single character: ")))

            # Get
            elif instruction == Instruction.GET.value:
                y, x = program_stack.pop(), program_stack.pop()
                if 0 <= y < len(program_matrix) and 0 <= x < len(program_matrix[y]):
                    program_stack.push(ord(program_matrix[y][x]))
                else:
                    program_stack.push(0)

            # Put
            elif instruction == Instruction.PUT.value:
                y, x, v = program_stack.pop(), program_stack.pop(), program_stack.pop()
                if 0 <= y < len(program_matrix) and 0 <= x < len(program_matrix[y]):
                    program_matrix[y][x] = chr(int(v))

            # End program
            elif instruction == Instruction.END_PROGRAM.value:
                program_end_reached = True

        # Update the cursor position once the instruction has been processed
        if cursor_direction == Direction.RIGHT.value:
            cursor_x += 1
        elif cursor_direction == Direction.LEFT.value:
            cursor_x -= 1
        elif cursor_direction == Direction.UP.value:
            cursor_y -= 1
        else:  # Direction.DOWN
            cursor_y += 1


if __name__ == '__main__':
    process_code(source_to_matrix(retrieve_program_source_path()))
