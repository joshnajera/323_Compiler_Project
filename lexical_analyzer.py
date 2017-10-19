#!/usr/bin/python3
__author__ = 'Josh'

import string
import enum

KEYWORDS = {"while", "if", "fi", "else", "return", "read", "write", "integer", "boolean", "real"}
DIGITS = {'1', '2', '3', '4', '5', '6', '7', '8', '9', '0'}
OPERATORS = {':=', '+', '-', '*', '/', '%%', '@', '<', '>', '/=', '>=', '<='}
LETTERS = set(string.ascii_letters)
SEPARATORS = {'(', ')', '{', '}', ',', ';'}
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
    RL = 5      # Real Number   -- Accepting state


class Lexer:
    """A lexical analyzer for RAT17F"""
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
        elif self.state == State.PER or self.state == State.RL:
            self.state = State.RL
        else:
            return -1

    def letter(self):
        """Transition function for a letter"""
        if self.state == State.START or self.state == State.ID2 or self.state == State.ID1:
            self.state = State.ID1
        else:
            return -1

    def eval(self, input_string):
        """Iterates through each character in an input string,
            and calls corresponding transition functions for each"""
        if input_string in KEYWORDS:
            return ("Keyword", input_string)
        elif input_string in OPERATORS:
            return ("Operator", input_string)
        elif input_string in SEPARATORS:
            return ("Separator", input_string)
        
        for char in input_string:
            if char not in self.transition:
                print("Error: String is not a valid int, real, or identifier")
                return 0
            if self.transition[char]() == -1:
                print("Error: String is not a valid int, real, or identifier")
                return 0
            
        if self.state == State.ID1 or self.state == State.ID2:
            self.state = State.START
            return ("Identifier", input_string)
        elif self.state == State.INT:
            self.state = State.START
            return ("Integer", input_string)
        elif self.state == State.RL:
            self.state = State.START
            return ("Real", input_string)
        else:
            self.state = State.START
            print("ERROR: '{}' is not a valid Identifier, Integer, or Real".format(input_string))
            return (False)
        
    def tokenize(self, in_file):
        """Iterates over a text file, generating tokens and yielding them"""
        buffer = ""
        for line in in_file:
            for word in line.strip().replace('\t',' ').split(' '):
            
                if word == '':
                    continue
            
                if word in SEP_OP or word in KEYWORDS:
                    evaluation = self.eval(word)
                    yield evaluation
            
                else:
                    word_iter = iter(word)          # Make an iter out of the word to allow for the use of "next(iter)"
                
                    for character in word_iter:
                        if character in SEP_OP.union(':'): # Checks if curr char is part of a 'multicharacter' Operator
                            if buffer:              # Evaluate anything that might be in the buffer first
                                evaluation = self.eval(buffer)
                                if evaluation:
                                    yield evaluation
                                buffer = ''         # Clear buffer
                        
                            try:
                                nxt = next(word_iter)   # Combine the next character with current one to check if it is a --
                                temp = character + nxt  # multicharacter Separator/Operator
                                if temp in SEP_OP:
                                    evaluation = self.eval(temp)
                                    if evaluation:
                                        yield evaluation
                                else:
                                    yield self.eval(character)
                                    buffer = nxt
                                continue
                            except StopIteration:
                                evaluation = self.eval(character)
                                yield evaluation
                                continue
                    
                        buffer += character
                
                    if buffer:
                        evaluation = self.eval(buffer)
                        if evaluation:
                            yield evaluation
                    buffer = ''

def main():
    """Main program"""
    lex = Lexer()
    in_file = open(SOURCE_FILE3)
    print('SOURCE CODE:')
    for line in in_file:
        print(line)
    in_file.seek(0)
    print('\n\nOUTPUT:\n')
    for token in lex.tokenize(in_file):
        print("Token:  {}\t\tLexeme:  {}".format(token[0].ljust(10), token[1]))
    in_file.close()

if __name__ == "__main__":
    main()

