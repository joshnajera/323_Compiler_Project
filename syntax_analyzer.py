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


class SyntaxAnalyzer(object):
    def __init__(self, file_name):
        in_file = open(file_name)
        self.next_token = lexical_analyzer.Lexer.result("token", "lexeme")
        self.consume = True
        self.lexer = lexical_analyzer.Lexer()
        self.lex = self.lexer.tokenize(in_file)
        self.factor()
        in_file.close()

    # Idea: Add check in next_tok to make sure we don't have 'extra_token_consumed' flag raised before consuming
    def next_tok(self):
        """Fetches next token/lexeme pair, if allowed"""

        if not self.consume:
            self.consume = True
            return

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

    # TODO Finish primary
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

    def opt_parameter_list(self, consume_next=True):
        """   <Opt Parameter List> ::= <Parameter List>  |  <Empty>   """

        if not self.parameter_list(consume_next):
            pass
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

    def term_prime(self, consume_next=True):

        if consume_next:
            self.next_tok()

        # Case: Epsilon
        if self.next_token.lexeme not in {"*", "/"}:
            return True
        if not self.factor():
            return False
        return self.term_prime()

    def term(self, consume_next=True):

        if not self.factor(consume_next):
            return False
        return self.term_prime()

    def expression_prime(self, consume_next=True):

        if consume_next:
            self.next_tok()

        # Case: Epsilon
        if self.next_token.lexeme not in {"+", "-"}:
            return True
        if not self.term():
            return False
        return self.expression_prime()

    def expression(self, consume_next=True):

        if not self.term(consume_next):
            return False
        return self.expression_prime()

    def condition(self, consume_next=True):
        """   <Condition> ::= <Expression> <Relop> <Expression>   """

        if not self.expression(consume_next):
            return False
        if not self.relop():
            return False
        if not self.expression():
            return False

        print("<Condition>")
        return True

    def write(self, consume_next=True):
        """   <Write> ::=   write ( <Expression>);   """

        if consume_next:
            self.next_tok()

        if self.lexeme_is_not("write"):
            return False
        self.next_tok()
        if self.lexeme_is_not("("):
            return False
        if not self.expression():
            return False
        self.next_tok()
        if self.lexeme_is_not(")"):
            return False
        self.next_tok()
        if self.lexeme_is_not(";"):
            return False

        print("<Write>")
        return True

    def assign(self, consume_next=True):
        """   <Assign> ::= <Identifier> := <Expression> ;   """

        if consume_next:
            self.next_tok()

        if self.next_token.token is not "Identifier":
            return False
        self.next_tok()
        if self.lexeme_is_not(":="):
            return False
        if not self.expression():
            return False
        self.next_tok()
        if self.lexeme_is_not(";"):
            return False

        print("<Assign>")
        return True

    def _return(self, consume_next=True):
        """   <Return> ::=  return ; | return <Expression> ;   """

        if consume_next:
            self.next_tok()

        if self.lexeme_is_not("return"):
            return False
        if self.expression():
            self.next_tok()
        if self.lexeme_is_not(";"):
                return False

        print("<Return>")
        return True

    def _while(self, consume_next=True):
        """   <While> ::= while ( <Condition> ) <Statement>    """

        if consume_next:
            self.next_tok()

        if self.lexeme_is_not("while"):
            return False
        self.next_tok()
        if self.lexeme_is_not("("):
            return False
        if not self.condition():
            return False
        self.next_tok()
        if self.lexeme_is_not(")"):
            return False
        if not self.statement():
            return False

    def _if(self, consume_next=True):
        """   <If> ::=  if ( <Condition>  ) <Statement> fi    |
                        if ( <Condition>  ) <Statement> else <Statement> fi   """

        if consume_next:
            self.next_tok()

        if self.lexeme_is_not("if"):
            return False
        self.next_tok()
        if self.lexeme_is_not("("):
            return False
        if not self.condition():
            return False
        self.next_tok()
        if self.lexeme_is_not(")"):
            return False
        if not self.statement():
            return False
        self.next_tok()
        if self.lexeme_is("else"):
            if not self.statement():
                return False
        self.next_tok()
        if self.lexeme_is_not("fi"):
            return False

        print("<If>")
        return True

    def statement(self, consume_next=True):
        """   <Statement> ::=  <Compound> | <Assign> | <If> |  <Return> | <Write> | <Read> | <While>   """

        if self.assign(consume_next):
            return True
        if self._if(False):
            return True
        if self._return(False):
            return True
        if self.write(False):
            return True
        if self.read(False):
            return True
        if self._while(False):
            return True
        if self.compound(False):
            return True

        return False

    def statement_list(self, consume_next=True):
        """   <Statement List> ::= <Statement>  |  <Statement> <Statement List>   """

        if not self.statement(consume_next):
            return False
        if not self.statement_list():
            pass
        return True

    def compound(self, consume_next=True):
        """   <Compound> ::= { <Statement List> }   """

        if consume_next:
            self.next_tok()

        if self.lexeme_is_not("{"):
            return False
        if not self.statement_list():
            return False
        self.next_tok()
        if self.lexeme_is_not("}"):
            return False

        print("<Compound>")
        return True

    def body(self, consume_next=True):
        """   <Body> ::= { < Statement List> }   """

        if consume_next:
            self.next_tok()

        if self.lexeme_is_not("{"):
            return False
        if not self.statement_list():
            return False
        self.next_tok()
        if self.lexeme_is_not("}"):
            return False

        print("<Body>")
        return True

    def function(self, consume_next=True):
        """<Function> ::=  @  <Identifier> ( <Opt Parameter List> ) <Opt Declaration List> <Body>"""

        if consume_next:
            self.next_tok()

        if self.lexeme_is_not("@"):
            return False
        self.next_tok()
        if self.next_token.token is not "Identifier":
            return False
        self.next_tok()
        if self.lexeme_is_not("("):
            return False
        if self.opt_parameter_list():
            pass
        self.next_tok() # Del?
        if self.lexeme_is_not(")"):
            return False
        if self.opt_declaration_list():
            pass
        if not self.body():
            return False

        print("<Function>")
        return True

    def function_definitions(self, consume_next=True):
        """   <Function Definitions>  ::= <Function> | <Function> <Function Definitions>    """

        if not self.function(consume_next):
            return False
        if not self.function_definitions():
            pass
        return True

    def opt_function_definitions(self, consume_next=True):
        """   <Opt Function Definitions> ::= <Function Definitions> | <Empty>   """

        if not self.function_definitions(consume_next):
            pass
        return True

    def rat17f(self):
        """   <Rat17F>  ::=  <Opt Function Definitions>
                         %%  <Opt Declaration List> <Statement List>    """
        if not self.opt_function_definitions():
            pass
        self.next_tok()
        if self.lexeme_is_not("%%"):
            return False
        if not self.opt_declaration_list():
            pass
        if not self.statement_list():
            return False


def main():
    # with open('test_syntax.txt') as in_file:
    #     la = lexical_analyzer.Lexer()
    #     tokens = la.tokenize(in_file)
    #     for token in tokens:
    #         print(token)
    mySA = SyntaxAnalyzer("test_syntax.txt")


if __name__ == "__main__":
    main()
