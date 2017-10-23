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

    def lexeme_is_not(self, char):
        """   Determines if the lexeme is NOT input, if not, dont consume token on next next_tok() call"""

        if self.next_token.lexeme is not char:
            self.consume = False
            return True

        return False

    def IDs(self):
        """  <IDs> ::= <Identifier> | <Identifier>, <IDs>   """

        # Consume next token from generator ?
        self.next_tok()

        # Case: Not <IDs>
        if self.next_token.token is not "Identifier":
            self.consume = False
            return False

        self.next_tok()
        # Case: <Identifier>
        if self.lexeme_is_not(","):
            print("<IDs>")
            return True

        # Case: <Identifier>, not <IDs>
        if not self.IDs():
            self.consume = False
            return False

        # Case: <IDs>
        return True

    def primary(self):
        """   <Primary> ::= <Identifier> | <Integer> | <Identifier> [<IDs>]
                           | ( <Expression> ) |  <Real>  | true | false   """

        # Consume next token from generator ?
        self.next_tok()

        if self.next_token.token is "Identifier":
            self.next_tok()

            # Case: <Identifier>
            if self.lexeme_is_not('['):
                print("<Primary>")
                return True
            if not self.IDs():
                self.consume = False
                return False
            self.next_tok()
            if self.lexeme_is_not(']'):
                return False

            # Case: <Identifier>[<IDs>]
            print("<Primary>")
            return True

        if self.lexeme_is_not("("):
            # Cases: <Float> OR <Integer> OR "true" OR "false"
            if self.next_token.token in {"Float", "Integer"}:
                print("<Primary>")
                return True
            if self.next_token.lexeme in {"true", "false"}:
                print("<Primary>")
                return True
            # Case: Not primary
            self.consume = False
            return False

        if not self.expression():
            self.consume =False
            return False
        self.next_tok()
        if self.lexeme_is_not(")"):
            return False

        # Case: ( <Expression> )
        print("<Primary>")
        return True

    def read(self):
        """   <Read> ::= read ( <IDs> );   """

        # Consume next token from generator
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

    def relop(self):
        """   <Relop> ::=   = |  /=  |   >   | <   |  =>   | <=   """

        # Consume next token from generator
        self.next_tok()

        if self.next_token.lexeme not in {'=', '/=', '>', '<', '=>', '<='}:
            self.consume = False
            return False

        print("<Relop>")
        return True

    def factor(self):
        """"   <Factor> ::= - <Primary> | <Primary>   """

        # Consume next token from generator
        self.next_tok()

        # Case: <Primary>
        if self.lexeme_is_not('-'):
            pass
        # Case: - <Primary>
        if not self.primary():
            self.consume = False
            return False

        print("<Factor>")
        return True

    def qualifier(self):
        """   < Qualifier >::= integer | boolean | floating   """

        # Consume next token from generator
        self.next_tok()

        if self.next_token.lexeme not in {"integer", "boolean", "floating"}:
            self.consume = False
            return False

        print("<Qualifier>")
        return True

    def parameter(self):
        """   <Parameter> ::= <IDs > : <Qualifier>   """

        if not self.IDs():
            self.consume = False
            return False
        self.next_tok()
        if self.lexeme_is_not(":"):
            return False
        if not self.qualifier():
            self.consume = False
            return False

        print("<Parameter>")
        return True

    def parameter_list(self):
        """   <Parameter List>  ::=  <Parameter>  | <Parameter> , <Parameter List>   """

        if not self.parameter():
            self.consume = False
            return False
        self.next_tok()
        if self.lexeme_is_not(","):
            print("<Parameter List> TODO: Extra token consumed...")
            return True
        if not self.parameter_list():
            self.consume = False
            return False

        print("Parameter List>")
        return True

    def opt_parameter_list(self):
        """   <Opt Parameter List> ::= <Parameter List>  |  <Empty>   """

        if not self.parameter_list():
            self.consume = False
        return True

    def declaration(self):
        """   <Declaration> ::= <Qualifier > <IDs>   """

        if not self.qualifier():
            self.consume = False
            return False
        if not self.IDs():
            self.consume = False
            return False

        print("<Declaration>")
        return True

    def declaration_list(self):
        """   <Declaration List>  := <Declaration> ;  | <Declaration> ; <Declaration List>   """

        if not self.declaration():
            self.consume = False
            return False
        self.next_tok()
        if self.lexeme_is_not(";"):
            return False
        if not self.declaration_list():
            self.consume = False

        print("<Declaration List>")
        return True

    def opt_declaration_list(self):
        """<Opt Declaration List> ::= <Declaration List>  | <Empty>"""

        if not self.declaration_list():
            self.consume = False
        return True

    def term_prime(self):

        self.next_tok()

        # Case: Epsilon
        if self.next_token.lexeme not in {"*", "/"}:
            return True
        if not self.factor():
            self.consume = False
            return False
        if not self.term_prime():
            self.consume = False
            return False
        return True

    def term(self):
        """   <Term> ::=  <Term> * <Factor>  | <Term> / <Factor> |  <Factor>   """

        if not self.factor():
            self.consume = False
            return False
        if not self.term_prime():
            self.consume = False
            return False

        print("<Term>")
        return True

    def expression_prime(self):

        self.next_tok()

        # Case: Epsilon
        if self.next_token.lexeme not in {"+", "-"}:
            self.consume = False
            return True
        if not self.term():
            self.consume = False
            return False
        if not self.expression_prime():
            self.consume = False
            return False

        return True

    def expression(self):
        """   <Expression>  ::= <Expression> + <Term>  | <Expression>  - <Term>  | <Term>   """

        if not self.term():
            self.consume = False
            return False
        if not self.expression_prime():
            self.consume = False
            return False

        print("<Expression>")
        return True

    def condition(self):
        """   <Condition> ::= <Expression> <Relop> <Expression>   """

        if not self.expression():
            self.consume = False
            return False
        if not self.relop():
            self.consume = False
            return False
        if not self.expression():
            self.consume = False
            return False

        print("<Condition>")
        return True

    def write(self):
        """   <Write> ::=   write ( <Expression>);   """

        self.next_tok()

        if self.lexeme_is_not("write"):
            return False
        self.next_tok()
        if self.lexeme_is_not("("):
            return False
        if not self.expression():
            self.consume = False
            return False
        self.next_tok()
        if self.lexeme_is_not(")"):
            return False
        self.next_tok()
        if self.lexeme_is_not(";"):
            return False

        print("<Write>")
        return True

    def assign(self):
        """   <Assign> ::= <Identifier> := <Expression> ;   """

        self.next_tok()

        if self.next_token.token is not "Identifier":
            self.consume = False
            return False
        self.next_tok()
        if self.lexeme_is_not(":="):
            return False
        if not self.expression():
            self.consume = False
            return False
        self.next_tok()
        if self.lexeme_is_not(";"):
            return False

        print("<Assign>")
        return True

    def _return(self):
        """   <Return> ::=  return ; | return <Expression> ;   """

        self.next_tok()

        if self.lexeme_is_not("return"):
            return False
        if self.expression():
            self.consume = False
            self.next_tok()
        if self.lexeme_is_not(";"):
            return False

        print("<Return>")
        return True

    def _while(self):
        """   <While> ::= while ( <Condition> ) <Statement>    """

        self.next_tok()

        if self.lexeme_is_not("while"):
            return False
        self.next_tok()
        if self.lexeme_is_not("("):
            return False
        if not self.condition():
            self.consume = False
            return False
        self.next_tok()
        if self.lexeme_is_not(")"):
            return False
        if not self.statement():
            self.consume = False
            return False

    def _if(self):
        """   <If> ::=  if ( <Condition>  ) <Statement> fi    |
                        if ( <Condition>  ) <Statement> else <Statement> fi   """

        self.next_tok()

        if self.lexeme_is_not("if"):
            return False
        self.next_tok()
        if self.lexeme_is_not("("):
            return False
        if not self.condition():
            self.consume = False
            return False
        self.next_tok()
        if self.lexeme_is_not(")"):
            return False
        if not self.statement():
            self.consume = False
            return False
        self.next_tok()
        if self.lexeme_is_not("else"):
            if self.lexeme_is_not("fi"):
                return False
        # Case: if ( <Condition>  ) <Statement> fi
        if self.lexeme_is_not("else"):
            return True
        if not self.statement():
            self.consume = False
            return False
        self.next_tok()
        if self.lexeme_is_not("fi"):
            return False

        print("<If>")
        return True

    def statement(self):
        """   <Statement> ::=  <Compound> | <Assign> | <If> |  <Return> | <Write> | <Read> | <While>   """

        if self.assign():
            return True
        if self._if():
            return True
        if self._return():
            return True
        if self.write():
            return True
        if self.read():
            return True
        if self._while():
            return True
        if self.compound():
            return True

        self.consume = False
        return False

    def statement_list(self):
        """   <Statement List> ::= <Statement>  |  <Statement> <Statement List>   """

        if not self.statement():
            self.consume = False
            return False
        if not self.statement_list():
            self.consume = False
        return True

    def compound(self):
        """   <Compound> ::= { <Statement List> }   """

        self.next_tok()

        if self.lexeme_is_not("{"):
            return False
        if not self.statement_list():
            self.consume = False
            return False
        self.next_tok()
        if self.lexeme_is_not("}"):
            return False

        print("<Compound>")
        return True

    def body(self):
        """   <Body> ::= { < Statement List> }   """

        self.next_tok()

        if self.lexeme_is_not("{"):
            return False
        if not self.statement_list():
            self.consume = False
            return False
        self.next_tok()
        if self.lexeme_is_not("}"):
            return False

        print("<Body>")
        return True

    def function(self):
        """<Function> ::=  @  <Identifier> ( <Opt Parameter List> ) <Opt Declaration List> <Body>"""

        self.next_tok()

        if self.lexeme_is_not("@"):
            return False
        self.next_tok()
        if self.next_token.token is not "Identifier":
            self.consume = False
            return False
        self.next_tok()
        if self.lexeme_is_not("("):
            return False
        if self.opt_parameter_list():
            self.consume = False
        self.next_tok()
        if self.lexeme_is_not(")"):
            return False
        if self.opt_declaration_list():
            self.consume = False
        if not self.body():
            self.consume = False
            return False

        print("<Function>")
        return True

    def function_definitions(self):
        """   <Function Definitions>  ::= <Function> | <Function> <Function Definitions>    """

        if not self.function():
            self.consume = False
            return False
        if not self.function_definitions():
            self.consume = False
        return True

    def opt_function_definitions(self):
        """   <Opt Function Definitions> ::= <Function Definitions> | <Empty>   """

        if not self.function_definitions():
            self.consume = False
        return True

    def rat17f(self):
        """   <Rat17F>  ::=  <Opt Function Definitions>
                         %%  <Opt Declaration List> <Statement List>    """
        if not self.opt_function_definitions():
            self.consume = False
        self.next_tok()
        if self.lexeme_is_not("%%"):
            return False
        if not self.opt_declaration_list():
            self.consume = False
        if not self.statement_list():
            self.consume = False
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
