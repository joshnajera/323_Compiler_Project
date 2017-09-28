__author__ = 'Josh'

import string
import enum

KEYWORDS = {"while", "if", "fi", "else", "return", "read", "write", "integer", "boolean", "real"}
PUNCTUATIONS = {':=', '+', '-', '*', '/', '@', '(', ')', '{', '}'}
DIGITS = {'1', '2', '3', '4', '5', '6', '7', '8', '9', '0'}
OPERATORS = {':=', '+', '-', '*', '/'}
LETTERS = set(string.ascii_letters)
SEPARATORS = {'(', ')', '{', '}', ',', ';', '@', '%%'}
SOP = SEPARATORS.union(OPERATORS).union(PUNCTUATIONS)
DigLet = DIGITS.union(LETTERS).union({".", "#"})

class State(enum.Enum):
    '''Holds possible states for our lexer'''
    START = 0   # Starting state
    ID1 = 1     # Identifier 1 -- Accepting state
    ID2 = 2     # Identifier 2 -- Accepting state
    INT = 3     # Integer -- Accepting state
    PER = 4     # Period
    RL = 5      # Real Number -- Accepting state

class Lexer:
    '''A lexical analyzer for RAT17F'''
    def __init__(self):
        self.state = State.START
        self.transition = {"#":self.pound}
        self.transition["."] = self.per
        for dig in DIGITS:
            self.transition[dig] = self.digit
        for let in LETTERS:
            self.transition[let] = self.letter

    def per(self):
        '''Transition function for a period'''
        if self.state == State.INT:
            self.state = State.PER
        else:
            return -1

    def pound(self):
        '''Transition function for a pound sign'''
        if self.state == State.ID1:
            self.state = State.ID2
        else:
            return -1

    def digit(self):
        '''Transition function for a digit'''
        if self.state == State.START or self.state == State.INT:
            self.state = State.INT
        elif self.state == State.PER or self.state == State.RL:
            self.state = State.RL
        else:
            return -1

    def letter(self):
        '''Transition function for a letter'''
        if self.state == State.START or self.state == State.ID2 or self.state == State.ID1:
            self.state = State.ID1
        else:
            return -1


    def eval(self, input_string):
        '''Iterates through each character in an input string,
            and calls corresponding transition functions for each'''
        for char in input_string:
            if char not in self.transition:
                print("Error: String is not a valid int, real, or identifier")
                return -1
            if self.transition[char]() == -1:
                print("Error: String is not a valid int, real, or identifier")
                return -1
        if self.state == State.ID1 or self.state == State.ID2:
            print("Entered string is an identifier")
            self.state = State.START
        elif self.state == State.INT:
            print("Entered string is an integer")
            self.state = State.START
        elif self.state == State.RL:
            print("Entered string is a real")
            self.state = State.START
        else:
            print("Error: String is not a valid int, real, or identifier")
            self.state = State.START

def main():
    '''Main program'''
    lex = Lexer()
    in_file = open("test_code.txt")
    buffer = ""
    special = False
    for line in in_file:
        for word in line.split(' '):
            if word == '':
                continue
            if word in SOP or word in KEYWORDS:
                print(word)
                # TODO: Deal with getting token type
            else:
                a = iter(word)
                for character in a:
                    if character in {":", "%"}:
                        if buffer:
                            print(buffer)
                            buffer = ''
                        nxt = next(a)
                        temp = character + nxt
                        if temp in SOP:
                            print(temp)
                        else:
                            buffer = nxt
                            print("ERROR")
                        continue
                    if character in SOP:
                        if buffer:
                            print(buffer)
                        print(character)
                        buffer = ''
                        continue
                    buffer += character
                print(buffer)
                buffer = ''
            #     if character in DigLet:     # While the character is not a space, add it to the buffer
            # if buffer in SOP:
            #         print(buffer)
            #         buffer = ''
            #     buffer = buffer + character
            # else:
            #     if buffer and buffer not in {":"}:
            #         print(buffer)
            #         lex.eval(buffer)
            #         buffer = ''
            #     if character != ' ':
            #         buffer += character
            #         if buffer != ":":
            #             print(buffer)
            #             buffer = ''

    # st = "123.0"
    # lex.eval(st)

if __name__ == "__main__":
    main()
