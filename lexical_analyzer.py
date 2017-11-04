#!/usr/bin/python3
"""Analyzes a text file and yields token-lexeme pairs"""
import string
import enum
from collections import namedtuple

__author__ = 'Josh'


KEYWORDS = {"while", "if", "fi", "else", "return", "read", "write", "integer", "boolean", "real", "true", "false"}
DIGITS = {'1', '2', '3', '4', '5', '6', '7', '8', '9', '0'}
OPERATORS = {':=', '+', '-', '*', '/', '%%', '@', '<', '>', '/=', '>=', '<='}
LETTERS = set(string.ascii_letters)
SEPARATORS = {'(', ')', '{', '}', ',', ';', '[', ']', ':'}
SEP_OP = SEPARATORS.union(OPERATORS)
DIG_LETT = DIGITS.union(LETTERS).union({".", "#"})

####################################################
###########                              ###########
###########     SOURCE FILE GOES HERE    ###########
###########                              ###########
####################################################
SOURCE_FILE = "code_spaces_tabs_newlines.txt"   # Working code with spaces and tabs and newlines
SOURCE_FILE2 = "difficult_code_no_spaces.txt"   # Working code with missing spaces
SOURCE_FILE3 = "broken_code.txt"                # Code with invalid identifiers, and reals


class State(enum.Enum):
    """Holds possible states for our lexer"""
    START = 0   # Starting state
    ID1 = 1     # Identifier 1  -- Accepting state
    ID2 = 2     # Identifier 2  -- Accepting state
    INT = 3     # Integer       -- Accepting state
    PER = 4     # Period
    FLT = 5     # Real Number   -- Accepting state


class Lexer(object):
    """A lexical analyzer for RAT17F"""
    result = namedtuple('tok_lex', ['token', 'lexeme', 'line_number'])

    def __init__(self):
        self.state = State.START
        self.transition = {"#": self.pound}
        self.transition["."] = self.per
        for dig in DIGITS:
            self.transition[dig] = self.digit
        for let in LETTERS:
            self.transition[let] = self.letter

    def per(self):
        """Transition function for a period"""
        if self.state == State.INT:
            self.state = State.PER
        else:
            return -1

    def pound(self):
        """Transition function for a pound sign"""
        if self.state == State.ID1:
            self.state = State.ID2
        else:
            return -1

    def digit(self):
        """Transition function for a digit"""
        if self.state == State.START or self.state == State.INT:
            self.state = State.INT
        elif self.state == State.PER or self.state == State.FLT:
            self.state = State.FLT
        else:
            return -1

    def letter(self):
        """Transition function for a letter"""
        if self.state == State.START or self.state == State.ID2 or self.state == State.ID1:
            self.state = State.ID1
        else:
            return -1

    def eval(self, input_string, line_number):
        """Iterates through each character in an input string,
            and calls corresponding transition functions for each"""
        line_number = line_number + 1
        if input_string in KEYWORDS:
            return Lexer.result("Keyword", input_string, line_number)
        elif input_string in OPERATORS:
            return Lexer.result("Operator", input_string, line_number)
        elif input_string in SEPARATORS:
            return Lexer.result("Separator", input_string, line_number)

        for char in input_string:
            if char not in self.transition:
                print("Error: char not in transition")
                return 0
            if self.transition[char]() == -1:
                print("Error: Bad transition")
                return 0

        if self.state == State.ID1 or self.state == State.ID2:
            self.state = State.START
            return Lexer.result("Identifier", input_string, line_number)
        elif self.state == State.INT:
            self.state = State.START
            return Lexer.result("Integer", input_string, line_number)
        elif self.state == State.FLT:
            self.state = State.START
            return Lexer.result("Float", input_string, line_number)
        else:
            self.state = State.START
            print("ERROR: '{}' is not a valid Identifier, Integer, or Real".format(input_string))
            return False

    def tokenize(self, in_file):
        """Iterates over a text file, generating tokens and yielding them"""
        buffer = ""
        for line_number, line in enumerate(in_file):
            for word in line.strip().replace('\t', ' ').split(' '):

                if word == '':
                    continue

                if word in SEP_OP or word in KEYWORDS:
                    evaluation = self.eval(word, line_number)
                    yield evaluation

                else:
                    # Make an iter out of the word to allow for the use of "next(iter)"
                    word_iter = iter(word)

                    for character in word_iter:
                        # Checks if curr char is part of a 'multicharacter' Operator
                        if character in SEP_OP:
                            if buffer:
                                # Evaluate anything that might be in the buffer first
                                evaluation = self.eval(buffer, line_number)
                                if evaluation:
                                    yield evaluation
                                # Clear buffer
                                buffer = ''

                            try:
                                # Combine the next character with current one to check if it is a --
                                nxt = next(word_iter)
                                # Multi-character Separator/Operator
                                temp = character + nxt
                                if temp in SEP_OP:
                                    evaluation = self.eval(temp, line_number)
                                    if evaluation:
                                        yield evaluation
                                elif nxt in SEP_OP and character in SEP_OP:
                                    yield self.eval(character, line_number)
                                    yield self.eval(nxt, line_number)

                                else:
                                    yield self.eval(character, line_number)
                                    buffer = nxt
                                continue
                            except StopIteration:
                                evaluation = self.eval(character, line_number)
                                yield evaluation
                                continue

                        buffer += character

                    if buffer:
                        evaluation = self.eval(buffer, line_number)
                        if evaluation:
                            yield evaluation
                    buffer = ''

def main():
    """Main program"""
    lex = Lexer()
    in_file = open(SOURCE_FILE2)
    print('SOURCE CODE:')
    for line in in_file:
        print(line)
    in_file.seek(0)
    print('\n\nOUTPUT:\n')
    for token in lex.tokenize(in_file):
        print("Token:  {}\t\tLexeme:  {}\t\tLine: {}".format(token.token.ljust(10), token.lexeme.ljust(10), token.line_number))
    in_file.close()

if __name__ == "__main__":
    main()

