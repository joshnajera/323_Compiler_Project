'''Handles Syntax Analysis'''
#!/usr/bin/python3
import enum
import lexical_analyzer

# with open('symbols.txt') as file:
#     with open('out.txt', mode='w') as out_f:
#         myList = sorted((x for x in file), key=len)
#         for item,i in zip(myList,range(len(myList))):
#             out_f.write('{} = {}\n'.format(str(item).strip(), i))
#         out_f.close()


class Symbol(enum.Enum):
    '''Holds the symbols for syntax analysis'''
    If = 0
    IDs = 1
    Body = 2
    Read = 3
    Term = 4
    Real = 5
    Empty = 6
    Write = 7
    While = 8
    Relop = 9
    Rat17F = 10
    Return = 11
    Assign = 12
    Factor = 13
    Primary = 14
    Integer = 15
    Function = 16
    Compound = 17
    Parameter = 18
    Qualifier = 19
    Statement = 20
    Condition = 21
    Identifier = 22
    Expression = 23
    Declaration = 24
    StatementList = 25
    ParameterList = 26
    DeclarationList = 27
    OptParameterList = 28
    OptDeclarationList = 29
    FunctionDefinitions = 30
    OptFunctionDefinitions = 31




class SyntaxAnalyzer(object):
    def __init__(self, file_name):
        in_file = open(file_name)
        self.next_token = ''
        self.lexer = lexical_analyzer.Lexer()
        self.lex = self.lexer.tokenize(in_file)
        self.primary()
        in_file.close()
    
    def next_tok(self):
        try:    
            self.next_token = next(self.lex)
            return self.next_token
        except StopIteration:
            return False


    def IDs(self):
        self.next_tok()
        if self.next_token[0] == 'Identifier':
            print(self.next_token[0], end='')
            self.next_tok()
            if self.next_token[1] == ',':
                print(', ', end='')
                self.IDs()
            else:
                print('\nIDs')
        else:
            print("Error! ID")

    def primary(self):
        self.next_token = next(self.lex)
        if self.next_token[0] == 'Identifier':
            self.next_token = next(self.lex)
            if self.next_token[1] == '[':
                self.IDs()
                self.next_token = next(self.lex)
                if self.next_token[1] == ']':
                    print("Primary-- Identifier[]")
                    return
                else:
                    print("Error! Primary: Identifier[]")
                    return
            else:
                pass
            print("Primary-- Identifier")
        elif self.next_token[0] in {'Integer', 'Real'}:
            print("Primary-- {}"%self.next_token[0])
        elif self.next_token[1] in {'true', 'false'}:
            print("Primary-- {}"%self.next_token[1])

    # def addition(self):
    #     self.integer()
    #     self.addition_prime()

    # def addition_prime(self):
    #     self.next_token = next(self.lex)
    #     if self.next_token[1] in {'+', '-'}:
    #         print("Operator Accepted")
    #         self.integer()
    #         self.addition_prime()
    #     else:
    #         pass

    # def integer(self):
    #     self.next_token = next(self.lex)
    #     if self.next_token[0] == 'Integer':
    #         print("Integer Accepted")
    #         return True
    #     else:
    #         print("Error!")
    #         return False
    

def main():
    # with open('test_syntax.txt') as in_file:
    #     la = lexical_analyzer.Lexer()
    #     tokens = la.tokenize(in_file)
    #     for token in tokens:
    #         print(token)
    mySA = SyntaxAnalyzer("test_syntax.txt")



if __name__ == "__main__":
    main()
