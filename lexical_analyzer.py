__author__ = 'Josh'

import string
import enum

KEYWORDS = {"while", "if", "fi", "else", "return", "read", "write", "integer", "boolean", "real"}
DIGITS = {'1', '2', '3', '4', '5', '6', '7', '8', '9', '0'}
OPERATORS = {':=', '+', '-', '*', '/'}
LETTERS = set(string.ascii_letters)
SEPARATORS = {'(', ')', '{', '}', ',', ';', '@', '%%'}
SEP_OP = SEPARATORS.union(OPERATORS)
DIG_LETT = DIGITS.union(LETTERS).union({".", "#"})

class State(enum.Enum):
    '''Holds possible states for our lexer'''
    START = 0   # Starting state
    ID1 = 1     # Identifier 1  -- Accepting state
    ID2 = 2     # Identifier 2  -- Accepting state
    INT = 3     # Integer       -- Accepting state
    PER = 4     # Period
    RL = 5      # Real Number   -- Accepting state

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
        if input_string in KEYWORDS:
            return (input_string, "Keyword")
        elif input_string in OPERATORS:
            return (input_string, "Operator")
        elif input_string in SEPARATORS:
            return (input_string, "Separator")
        
        for char in input_string:
            if char not in self.transition:
                print("Error: String is not a valid int, real, or identifier")
                return -1
            if self.transition[char]() == -1:
                print("Error: String is not a valid int, real, or identifier")
                return -1
            
        if self.state == State.ID1 or self.state == State.ID2:
            self.state = State.START
            return (input_string, "Identifier")
        elif self.state == State.INT:
            self.state = State.START
            return (input_string, "Integer")
        elif self.state == State.RL:
            self.state = State.START
            return (input_string, "Float")
        else:
            self.state = State.START
            print("ERROR: '{}' is not a valid Identifier, Integer, or Float".format(input_string))
            return (False)
        
    def tokenize(self, in_file):
        '''Iterates over a text file, generating tokens and yielding them'''
        buffer = ""
        for line in in_file:
            for word in line.split(' '):
            
                if word == '':
                    continue
            
                if word in SEP_OP or word in KEYWORDS: # TODO Clean this line up
                    evaluation = self.eval(word)
                    yield evaluation
            
                else:
                    word_iter = iter(word)          # Make an iterator out of the word to allow for the use of "next(iter)"
                
                    for character in word_iter:
                        if character in {":", "%"}: # Checks if curr char is a part of a 'multicharacter' Separator/Operator
                            if buffer:              # Evaluate anything that might be in the buffer first
                                evaluation = self.eval(word)
                                if evaluation:
                                    yield evaluation
                                buffer = ''         # Clear buffer
                        
                            nxt = next(word_iter)   # Combine the next character with current one to check if it is a --
                            temp = character + nxt  #    multicharacter Separator/Operator
                            if temp in SEP_OP:
                                evaluation = self.eval(temp)
                                if evaluation:
                                    yield evaluation
                            else:
                                buffer = nxt
                                print("ERROR")
                            continue
                    
                        if character in SEP_OP:        # Checks if curr char is a separator or Operator
                            if buffer:
                                evaluation = self.eval(buffer)
                                if evaluation:
                                    yield evaluation
                            evaluation = self.eval(character)
                            yield evaluation
                            buffer = ''
                            continue
                    
                        buffer += character
                
                    evaluation = self.eval(buffer)
                    if evaluation:
                        yield evaluation
                    buffer = ''
        

def main():
    '''Main program'''
    lex = Lexer()
    in_file = open("test_code.txt")
    for token in lex.tokenize(in_file):
        print(token)
    in_file.close()

if __name__ == "__main__":
    main()
