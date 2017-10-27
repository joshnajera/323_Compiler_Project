"""Handles Syntax Analysis"""
#!/usr/bin/python3
import inspect
import lexical_analyzer


# with open('symbols.txt') as file:
#     with open('out.txt', mode='w') as out_f:
#         myList = sorted((x for x in file), key=len)
#         for item,i in zip(myList,range(len(myList))):
#             out_f.write('{} = {}\n'.format(str(item).strip(), i))
#         out_f.close()


class SyntaxAnalyzer(object):
    """   Checks syntax according to ra17f rules   """
    def __init__(self, file_name, CONSOLE_DEBUG):
        self.CONSOLE_DEBUG = CONSOLE_DEBUG
        in_file = open(file_name)
        self.next_token = lexical_analyzer.Lexer.result("token", "lexeme")
        self.consume = True
        self.lexer = lexical_analyzer.Lexer()
        self.lex = self.lexer.tokenize(in_file)
        self.rat17f()
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
    
    def print_token(self):
        print("Token: {}".format(self.next_token.token.ljust(24)), end='')
        print("Lexeme: {}".format(self.next_token.lexeme))

    @staticmethod
    def print_production(lhs='', rhs=''):
        """   Prints and saves the production rule given   """

        print("R:\t<{}>".format(lhs).ljust(30), end='')
        if len(rhs) > 0:
            print("=>\t  {}".format(rhs))
            return
        print('')

    def error(self, expected=''):
        """   Prints an error report   """

        caller = inspect.stack()[1][3]
        report = "ERROR: In {}()-- \n\tReceived: {}  \n\tExpected: {}"\
            .format(caller, self.next_token.lexeme, expected)
        print(report)

    def lexeme_is_not(self, char):
        """   Determines if the lexeme is NOT input, if not, dont consume token on next next_tok() call"""

        if self.next_token.lexeme != char:
            self.consume = False
            return True
        return False

    def IDs(self):
        """  <IDs> ::= <Identifier> | <Identifier>, <IDs>   """

        # Consume next token from generator ?
        self.next_tok()

        # Case: Not <IDs>
        if self.next_token.token is not "Identifier":
            self.error('<Identifier>')
            self.consume = False
            return False

        self.print_token()
        self.next_tok()
        # Case: <Identifier>
        if self.lexeme_is_not(","):
            SyntaxAnalyzer.print_production('IDs')
            return True

        self.print_token()
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
            self.print_token()
            self.next_tok()

            # Case: <Identifier>
            if self.lexeme_is_not('['):
                SyntaxAnalyzer.print_production('Primary', '<Identifier>')
                return True
            self.print_token()
            if not self.IDs():
                self.error('<IDs>')
                self.consume = False
                return False
            self.next_tok()
            if self.lexeme_is_not(']'):
                self.error(']')
                return False
            self.print_token()

            # Case: <Identifier>[<IDs>]
            SyntaxAnalyzer.print_production('Primary', '<Identifier> [<IDs>]')
            return True

        if self.lexeme_is_not("("):
            # Cases: <Float> OR <Integer> OR "true" OR "false"
            if self.next_token.token in {"Float", "Integer"}:
                self.print_token()
                self.consume = True
                SyntaxAnalyzer.print_production('Primary', "<{}>".format(self.next_token.token))
                return True
            if self.next_token.lexeme in {"true", "false"}:
                self.print_token()
                self.consume = True
                SyntaxAnalyzer.print_production('Primary', "<{}>".format(self.next_token.lexeme))
                return True
            # Case: Not primary
            self.error('<Identifier> OR <Integer> OR <Identifier> [<IDs>] OR ( <Expression> ) OR  <Real>  OR true OR false')
            self.consume = False
            return False

        self.print_token()
        if not self.expression():
            self.error('<Expression>')
            self.consume =False
            return False
        self.next_tok()
        if self.lexeme_is_not(")"):
            self.error(')')
            return False
        self.print_token()

        # Case: ( <Expression> )
        SyntaxAnalyzer.print_production('Primary', '( <Expression> )')
        return True

    def read(self):
        """   <Read> ::= read ( <IDs> );   """

        # Consume next token from generator
        self.next_tok()

        if self.lexeme_is_not("read"):
            return False
        self.print_token()
        self.next_tok()
        if self.lexeme_is_not("("):
            self.error('(')
            return False
        self.print_token()
        if not self.IDs():
            self.error('<IDs>')
            return False
        self.next_tok()
        if self.lexeme_is_not(")"):
            self.error(')')
            return False
        self.print_token()
        self.next_tok()
        if self.lexeme_is_not(";"):
            self.error(';')
            return False
        self.print_token()

        SyntaxAnalyzer.print_production('Read', 'read ( <IDs> );')
        return True

    def relop(self):
        """   <Relop> ::=   = |  /=  |   >   | <   |  =>   | <=   """

        # Consume next token from generator
        self.next_tok()

        if self.next_token.lexeme not in {'=', '/=', '>', '<', '=>', '<='}:
            self.error('relational operator (\'=\', \'/=\', \'>\', \'<\', \'=>\', \'<=\')')
            self.consume = False
            return False

        self.print_token()
        SyntaxAnalyzer.print_production('Relop', '')
        return True

    def factor(self):
        """"   <Factor> ::= - <Primary> | <Primary>   """

        # Consume next token from generator
        self.next_tok()

        neg = False
        # Case: <Primary>
        if self.lexeme_is_not('-'):
            self.consume = False
        else:
            neg = True
            self.print_token()

        # Case: - <Primary>
        if not self.primary():
            self.error('<Primary>')
            self.consume = False
            return False

        if neg:
            SyntaxAnalyzer.print_production('Factor', '-<Primary>')
        else:
            SyntaxAnalyzer.print_production('Factor', '<Primary>')
        return True

    def qualifier(self):
        """   < Qualifier >::= integer | boolean | floating   """

        # Consume next token from generator
        self.next_tok()

        if self.next_token.lexeme not in {"integer", "boolean", "floating"}:
            self.consume = False
            return False

        self.print_token()
        SyntaxAnalyzer.print_production('Qualifier', '<{}>'.format(self.next_token.lexeme))
        return True

    def parameter(self):
        """   <Parameter> ::= <IDs > : <Qualifier>   """

        if not self.IDs():
            self.error('<IDs>')
            self.consume = False
            return False
        self.next_tok()
        if self.lexeme_is_not(":"):
            self.error(':')
            return False
        self.print_token()
        if not self.qualifier():
            self.error('<Qualifier>')
            self.consume = False
            return False

        SyntaxAnalyzer.print_production('Parameter', '<IDs> : <Qualifier>')
        return True

    def parameter_list(self):
        """   <Parameter List>  ::=  <Parameter>  | <Parameter> , <Parameter List>   """

        if not self.parameter():
            self.error('<Parameter>')
            self.consume = False
            return False
        self.next_tok()
        if self.lexeme_is_not(","):
            SyntaxAnalyzer.print_production('Parameter List', '<Parameter> | <Parameter>, <Parameter List>')
            return True
        self.print_token()
        if not self.parameter_list():
            self.consume = False
            return False

        return True

    def opt_parameter_list(self):
        """   <Opt Parameter List> ::= <Parameter List>  |  <Empty>   """

        if not self.parameter_list():
            self.consume = False
            SyntaxAnalyzer.print_production('Opt Parameter List', '<Empty>')
        else:
            SyntaxAnalyzer.print_production('Opt Parameter List', '<Parameter List>')
        return True

    def declaration(self):
        """   <Declaration> ::= <Qualifier > <IDs>   """

        if not self.qualifier():
            self.consume = False
            return False
        if not self.IDs():
            self.error('<IDs>')
            self.consume = False
            return False

        SyntaxAnalyzer.print_production('Declaration', '<Qualifier> <IDs>')
        return True

    def declaration_list(self):
        """   <Declaration List>  := <Declaration> ;  | <Declaration> ; <Declaration List>   """

        if not self.declaration():
            self.consume = False
            return False
        self.next_tok()
        if self.lexeme_is_not(";"):
            self.error(';')
            return False
        self.print_token()
        if not self.declaration_list():
            self.consume = False

        SyntaxAnalyzer.print_production('Declaration List', '<Declaration>; | <Declaration>; <Declaration List>')
        return True

    def opt_declaration_list(self):
        """<Opt Declaration List> ::= <Declaration List>  | <Empty>"""

        if not self.declaration_list():
            self.consume = False
            SyntaxAnalyzer.print_production('Opt Declaration List', '<Empty>')
        else:
            SyntaxAnalyzer.print_production('Opt Declaration List', '<Declaration List>')
        return True

    def term_prime(self):

        self.next_tok()

        # Case: Epsilon
        if self.next_token.lexeme not in {"*", "/"}:
            self.consume = False
            return True
        self.print_token()
        if not self.factor():
            self.error('<Factor>')
            self.consume = False
            return False
        if not self.term_prime():
            self.consume = False
            return False
        return True

    def term(self):
        """   <Term> ::=  <Term> * <Factor>  | <Term> / <Factor> |  <Factor>   """

        if not self.factor():
            self.error('<Factor>')
            self.consume = False
            return False
        if not self.term_prime():
            self.consume = False
            return False

        SyntaxAnalyzer.print_production('Term', '')
        return True

    def expression_prime(self):

        self.next_tok()

        # Case: Epsilon
        if self.next_token.lexeme not in {"+", "-"}:
            self.consume = False
            return True
        self.print_token()
        if not self.term():
            self.error('<Term>')
            self.consume = False
            return False
        if not self.expression_prime():
            self.consume = False
            return False

        return True

    def expression(self):
        """   <Expression>  ::= <Expression> + <Term>  | <Expression>  - <Term>  | <Term>   """

        if not self.term():
            self.error('<Term>')
            self.consume = False
            return False
        if not self.expression_prime():
            self.consume = False
            return False

        SyntaxAnalyzer.print_production('Expression', '')
        return True

    def condition(self):
        """   <Condition> ::= <Expression> <Relop> <Expression>   """

        if not self.expression():
            self.error('<Expression>')
            self.consume = False
            return False
        if not self.relop():
            self.error('<Relop>')
            self.consume = False
            return False
        if not self.expression():
            self.error('<Expression>')
            self.consume = False
            return False

        SyntaxAnalyzer.print_production('Condition', '<Expression> <Relop> <Expression>')
        return True

    def write(self):
        """   <Write> ::=   write ( <Expression>);   """

        self.next_tok()

        if self.lexeme_is_not("write"):
            return False
        self.print_token()
        self.next_tok()
        if self.lexeme_is_not("("):
            self.error('(')
            return False
        self.print_token()
        if not self.expression():
            self.error('<Expression>')
            self.consume = False
            return False
        self.next_tok()
        if self.lexeme_is_not(")"):
            self.error(')')
            return False
        self.print_token()
        self.next_tok()
        if self.lexeme_is_not(";"):
            self.error(';')
            return False
        self.print_token()

        SyntaxAnalyzer.print_production('Write', 'write ( <Expression>);')
        return True

    def assign(self):
        """   <Assign> ::= <Identifier> := <Expression> ;   """

        self.next_tok()

        if self.next_token.token is not "Identifier":
            self.consume = False
            return False
        self.print_token()
        self.next_tok()
        if self.lexeme_is_not(":="):
            self.error(':=')
            return False
        self.print_token()
        if not self.expression():
            self.error('<Expression>')
            self.consume = False
            return False
        self.next_tok()
        if self.lexeme_is_not(";"):
            self.error(';')
            return False
        self.print_token()

        SyntaxAnalyzer.print_production('Assign', '<Identifier> := <Expression> ;')
        return True

    def _return(self):
        """   <Return> ::=  return ; | return <Expression> ;   """

        with_expression = True
        self.next_tok()

        if self.lexeme_is_not("return"):
            return False
        self.print_token()
        if not self.expression():
            self.consume = False
            with_expression = False

        self.next_tok()
        if self.lexeme_is_not(";"):
            self.error(';')
            return False
        self.print_token()

        if not with_expression:
            SyntaxAnalyzer.print_production('Return', 'return ;')
        else:
            SyntaxAnalyzer.print_production('Return', 'return <Expression> ;')
        return True

    def _while(self):
        """   <While> ::= while ( <Condition> ) <Statement>    """

        self.next_tok()

        if self.lexeme_is_not("while"):
            return False
        self.print_token()
        self.next_tok()
        if self.lexeme_is_not("("):
            self.error('(')
            return False
        self.print_token()
        if not self.condition():
            self.consume = False
            return False
        self.next_tok()
        if self.lexeme_is_not(")"):
            self.error(')')
            return False
        self.print_token()
        if not self.statement():
            self.error('<Statement>')
            self.consume = False
            return False

        SyntaxAnalyzer.print_production('While', 'while ( <Condition> ) <Statement>')
        return True

    def _if(self):
        """   <If> ::=  if ( <Condition>  ) <Statement> fi    |
                        if ( <Condition>  ) <Statement> else <Statement> fi   """

        self.next_tok()

        if self.lexeme_is_not("if"):
            return False
        self.print_token()
        self.next_tok()
        if self.lexeme_is_not("("):
            self.error('if')
            return False
        self.print_token()
        if not self.condition():
            self.error('<Condition>')
            self.consume = False
            return False
        self.next_tok()
        if self.lexeme_is_not(")"):
            self.error(')')
            return False
        self.print_token()
        if not self.statement():
            self.error('<Statement>')
            self.consume = False
            return False
        self.next_tok()
        if self.lexeme_is_not("else"):
            if self.lexeme_is_not("fi"):
                self.error('\'else\' or \'fi\'')
                return False
            SyntaxAnalyzer.print_production('If', 'if ( <Condition>  ) <Statement> fi')
        # Case: if ( <Condition>  ) <Statement> fi
        self.print_token()
        if self.lexeme_is_not("else"):
            print("\t<fi>")
            return True
        if not self.statement():
            self.error('<Statement>')
            self.consume = False
            return False
        self.next_tok()
        if self.lexeme_is_not("fi"):
            self.error('fi')
            return False
        self.print_token()

        SyntaxAnalyzer.print_production('If', 'if ( <Condition>  ) <Statement> else <Statement> fi')
        return True

    def statement(self):
        """   <Statement> ::=  <Compound> | <Assign> | <If> |  <Return> | <Write> | <Read> | <While>   """

        if self.assign():
            SyntaxAnalyzer.print_production('Statement', '<Assign>')
            return True
        if self._if():
            SyntaxAnalyzer.print_production('Statement', '<If>')
            return True
        if self._return():
            SyntaxAnalyzer.print_production('Statement', '<Return>')
            return True
        if self.write():
            SyntaxAnalyzer.print_production('Statement', '<Write>')
            return True
        if self.read():
            SyntaxAnalyzer.print_production('Statement', '<Read>')
            return True
        if self._while():
            SyntaxAnalyzer.print_production('Statement', '<While>')
            return True
        if self.compound():
            SyntaxAnalyzer.print_production('Statement', '<Compound>')
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
            SyntaxAnalyzer.print_production('Statement List', '<Statement>  |  <Statement> <Statement List>')
        return True

    def compound(self):
        """   <Compound> ::= { <Statement List> }   """

        self.next_tok()

        if self.lexeme_is_not("{"):
            return False
        self.print_token()
        if not self.statement_list():
            self.error('<Statement_List>')
            self.consume = False
            return False
        self.next_tok()
        if self.lexeme_is_not("}"):
            self.error('}')
            return False
        self.print_token()

        SyntaxAnalyzer.print_production('Compound', '{ <Statement List> }')
        return True

    def body(self):
        """   <Body> ::= { < Statement List> }   """

        self.next_tok()

        if self.lexeme_is_not("{"):
            return False
        self.print_token()
        if not self.statement_list():
            self.error('<Statement_List>')
            self.consume = False
            return False
        self.next_tok()
        if self.lexeme_is_not("}"):
            self.error('}')
            return False
        self.print_token()

        SyntaxAnalyzer.print_production('Body', '{ <Statement List> }')
        return True

    def function(self):
        """<Function> ::=  @  <Identifier> ( <Opt Parameter List> ) <Opt Declaration List> <Body>"""

        self.next_tok()

        if self.lexeme_is_not("@"):
            return False
        self.print_token()
        self.next_tok()
        if self.next_token.token is not "Identifier":
            self.error('<Identifier>')
            self.consume = False
            return False
        self.print_token()
        self.next_tok()
        if self.lexeme_is_not("("):
            self.error('(')
            return False
        self.print_token()
        if not self.opt_parameter_list():
            self.consume = False
        self.next_tok()
        if self.lexeme_is_not(")"):
            self.error(')')
            return False
        self.print_token()
        if self.opt_declaration_list():
            self.consume = False
        if not self.body():
            self.error('<Body>')
            self.consume = False
            return False

        SyntaxAnalyzer.print_production('Function', '@ <Identifier> ( <Opt Parameter List> ) <Opt Declaration List> <Body>')
        return True

    def function_definitions(self):
        """   <Function Definitions>  ::= <Function> | <Function> <Function Definitions>    """

        if not self.function():
            self.consume = False
            return False
        if not self.function_definitions():
            self.consume = False
        SyntaxAnalyzer.print_production('Function Definitions', '<Function> | <Function> <Function Definitions>')
        return True

    def opt_function_definitions(self):
        """   <Opt Function Definitions> ::= <Function Definitions> | <Empty>   """

        if not self.function_definitions():
            self.consume = False
            SyntaxAnalyzer.print_production('Opt Function Definitions', '<Empty>')
        else:
            SyntaxAnalyzer.print_production('Opt Function Definitions', '<Function Definitions>')
        return True

    def rat17f(self):
        """   <Rat17F>  ::=  <Opt Function Definitions>
                         %%  <Opt Declaration List> <Statement List>    """
        if not self.opt_function_definitions():
            self.consume = False
        self.next_tok()
        if self.lexeme_is_not("%%"):
            self.error('%%')
            return False
        self.print_token()
        if not self.opt_declaration_list():
            self.consume = False
        if not self.statement_list():
            self.consume = False
            return False

        SyntaxAnalyzer.print_production('Rat17f', '<Opt Function Definitions> %% <Opt Declaration List> <Statement List>')
        return True


def main():
    # with open('test_syntax.txt') as in_file:
    #     la = lexical_analyzer.Lexer()
    #     tokens = la.tokenize(in_file)
    #     for token in tokens:
    #         print(token)
    CONSOLE_DEBUG = False
    mySA = SyntaxAnalyzer("test_syntax.txt", CONSOLE_DEBUG)


if __name__ == "__main__":
    main()
