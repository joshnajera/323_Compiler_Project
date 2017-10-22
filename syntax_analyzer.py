"""Handles Syntax Analysis"""
#!/usr/bin/python3
import enum
import lexical_analyzer

# with open('symbols.txt') as file:
#     with open('out.txt', mode='w') as out_f:
#         myList = sorted((x for x in file), key=len)
#         for item,i in zip(myList,range(len(myList))):
#             out_f.write('{} = {}\n'.format(str(item).strip(), i))
#         out_f.close()

CONSOLE_DEBUG = True


class Symbol(enum.Enum):
    """Holds the symbols for syntax analysis"""
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
        self.next_token = lexical_analyzer.Lexer.result("token", "lexeme")
        self.lexer = lexical_analyzer.Lexer()
        self.lex = self.lexer.tokenize(in_file)
        self.factor()
        in_file.close()

    # Idea: Add check in next_tok to make sure we don't have 'extra_token_consumed' flag raised before consuming
    def next_tok(self):
        try:    
            self.next_token = next(self.lex)
            return self.next_token
        except StopIteration:
            return False

    def lexeme_is(self, char):
        return self.next_token.lexeme is char

    def lexeme_is_not(self, char):
        return self.next_token.lexeme is not char

    def IDs(self, consume_next=True):
        """  <IDs> ::= <Identifier> | <Identifier>, <IDs>   """

        # Consume next token from generator ?
        if consume_next:
            self.next_tok()

        # Case: Not <IDs>
        if self.next_token.token is not "Identifier":
            return False

        # Case: <Identifier>, ...
        # print("Identifier", end='')
        self.next_tok()
        if self.next_token.lexeme is ',':
            # print(", ", end='')
            return self.IDs()

        # Case: <Identifier>
        print("<IDs>", end='')
        return True

    def primary(self, consume_next=True):
        """   <Primary> ::= <Identifier> | <Integer> | <Identifier> [<IDs>]
                           | ( <Expression> ) |  <Real>  | true | false   """

        # Consume next token from generator ?
        if consume_next:
            self.next_tok()

        if self.next_token.token is "Identifier":
            print("<Primary>", end='')
            self.next_tok()

            print(self.next_token.lexeme, end='')
            if self.next_token.lexeme is not '[':
                return True
            if not self.IDs():
                return False
            self.next_tok()
            print(self.next_token.lexeme, end='')
            return self.lexeme_is(']')

        # TODO Case: ( <Expression> )

        if self.next_token.token not in {"Float", "Integer"}:
            if self.next_token.lexeme not in {"true", "false"}:
                return False

        print("<Primary>", end='')
        return True

    def expression(self, consume_next=True):
        pass

    def read(self, consume_next):
        """   <Read> ::= read ( <IDs> );   """

        # Consume next token from generator
        if consume_next:
            self.next_tok()

        if self.lexeme_is_not("read"):
            return False
        self.next_tok()
        if self.lexeme_is_not("("):
            return False
        if not self.IDs():
            return False
        self.next_tok()
        if self.lexeme_is_not(")"):
            return False
        self.next_tok()
        if self.lexeme_is_not(";"):
            return False

        print("<Read>")
        return True

    def relop(self, consume_next=True):
        """   <Relop> ::=   = |  /=  |   >   | <   |  =>   | <=   """
        # Consume next token from generator
        if consume_next:
            self.next_tok()

        if self.next_token.lexeme not in {'=', '/=', '>', '<', '=>', '<='}:
            return False

        print("<Relop>")
        return True

    def factor(self, consume_next=True):
        """"   <Factor> ::= - <Primary> | <Primary>   """

        # Consume next token from generator
        if consume_next:
            self.next_tok()

        # Case: <Primary>
        if self.lexeme_is_not('-'):
            if self.primary(consume_next=False):
                print("<Factor>")
                return True
            else: return False

        # Case: - <Primary>
        if self.primary():
            print("<Factor>")
            return True
        else: return False

    def qualifier(self, consume_next=True):
        """   < Qualifier >::= integer | boolean | floating   """

        # Consume next token from generator
        if consume_next:
            self.next_tok()

        if self.next_token.lexeme not in {"integer", "boolean", "floating"}:
            return False

        print("<Qualifier>")
        return True

    def parameter(self, consume_next=True):
        """   <Parameter> ::= <IDs > : <Qualifier>   """

        # Consume next token from generator
        if consume_next:
            self.next_tok()

        if not self.IDs():
            return False
        self.next_tok()
        if self.lexeme_is_not(":"):
            return False
        if not self.qualifier():
            return False

        print("<Parameter>")
        return True

    def parameter_list(self, consume_next=True):
        """   <Parameter List>  ::=  <Parameter>  | <Parameter> , <Parameter List>   """

        # Consume next token from generator
        if consume_next:
            self.next_tok()

        if not self.parameter():
            return False
        self.next_tok()
        if self.lexeme_is_not(","):
            # TODO: Extra token consumed...
            print("<Parameter List> TODO: Extra token consumed...")
            return True
        if not self.parameter_list():
            return False

        print("Parameter List>")
        return True

    def declaration(self, consume_next=True):
        """   <Declaration> ::= <Qualifier > <IDs>   """

        # Consume next token from generator
        if consume_next:
            self.next_tok()

        if not self.qualifier():
            return False
        if not self.IDs():
            return False

        print("<Declaration>")
        return True

    def declaration_list(self, consume_next=True):
        """   <Declaration List>  := <Declaration> ;  | <Declaration> ; <Declaration List>   """

        # Consume next token from generator
        if consume_next:
            self.next_tok()

        if not self.declaration():
            return False
        self.next_tok()
        if self.lexeme_is_not(";"):
            return False
        if not self.declaration_list():
            pass
        return True

    def opt_declaration_list(self, consume_next=True):
        """<Opt Declaration List> ::= <Declaration List>  | <Empty>"""

        # Consume next token from generator
        if consume_next:
            self.next_tok()

        if not self.declaration_list():
            pass
        return True




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
























































