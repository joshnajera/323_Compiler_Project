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
        print("Token: {}".format(self.next_token.token.ljust(18)),end='')
        print("Lexeme: {}".format(self.next_token.lexeme))

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
            print("ERROR: In IDs(), Expected <Identifier> ")
            self.consume = False
            return False

        self.print_token()
        self.next_tok()
        # Case: <Identifier>
        if self.lexeme_is_not(","):
            print("\t<IDs>")
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
                print("\t<Primary>".ljust(23)+ "=> <Identifier>")
                return True
            self.print_token()
            if not self.IDs():
                print("ERROR: In primary(), Expected <IDs> ")
                self.consume = False
                return False
            self.next_tok()
            if self.lexeme_is_not(']'):
                print("ERROR: In primary(), Expected ']' ")
                return False
            self.print_token()

            # Case: <Identifier>[<IDs>]
            print("\t<Primary>".ljust(23)+"=> <Identifier> [<IDs>]")
            return True

        if self.lexeme_is_not("("):
            # Cases: <Float> OR <Integer> OR "true" OR "false"
            if self.next_token.token in {"Float", "Integer"}:
                self.print_token()
                self.consume = True
                print("\t<Primary>".ljust(23)+"=> {}".format(self.next_token.token))
                return True
            if self.next_token.lexeme in {"true", "false"}:
                self.print_token()
                self.consume = True
                print("\t<Primary>".ljust(23)+"=> {}".format(self.next_token.lexeme))
                return True
            # Case: Not primary
            print("ERROR: In primary(), Expected one of the following...\n<Identifier> OR <Integer> OR <Identifier> [<IDs>] OR ( <Expression> ) OR  <Real>  OR true OR false")
            self.consume = False
            return False

        self.print_token()
        if not self.expression():
            print("ERROR: In primary(), Expected <Expression>")
            self.consume =False
            return False
        self.next_tok()
        if self.lexeme_is_not(")"):
            print("ERROR: In primary(), Expected ')'")
            return False
        self.print_token()

        # Case: ( <Expression> )
        print("\t<Primary>".ljust(23)+"=> ( <Expression> )")
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
            print("ERROR: In read(), Expected '('")
            return False
        self.print_token()
        if not self.IDs():
            print("ERROR: In read(), Expected <IDs>")
            return False
        self.next_tok()
        if self.lexeme_is_not(")"):
            print("ERROR: In read(), Expected ')'")
            return False
        self.print_token()
        self.next_tok()
        if self.lexeme_is_not(";"):
            print("ERROR: In read(), Expected ';'")
            return False
        self.print_token()

        print("\t<Read>".ljust(23)+"=> read ( <IDs> );")
        return True

    def relop(self):
        """   <Relop> ::=   = |  /=  |   >   | <   |  =>   | <=   """

        # Consume next token from generator
        self.next_tok()

        if self.next_token.lexeme not in {'=', '/=', '>', '<', '=>', '<='}:
            print("ERROR: In relop(), Expected relational operator ('=', '/=', '>', '<', '=>', '<=')")
            self.consume = False
            return False

        self.print_token()
        print("\t<Relop>")
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
            print("ERROR: In factor(), Expected <Primary>")
            self.consume = False
            return False

        print("\t<Factor>".ljust(23)+"=> ", end='')
        if neg:
            print("-", end='')
        print("<Primary>")
        return True

    def qualifier(self):
        """   < Qualifier >::= integer | boolean | floating   """

        # Consume next token from generator
        self.next_tok()

        if self.next_token.lexeme not in {"integer", "boolean", "floating"}:
            self.consume = False
            return False

        self.print_token()
        print("\t<Qualifier>".ljust(23)+"=> {}".format(self.next_token.lexeme))
        return True

    def parameter(self):
        """   <Parameter> ::= <IDs > : <Qualifier>   """

        if not self.IDs():
            print("ERROR: In parameter(), Expected <IDs>")
            self.consume = False
            return False
        self.next_tok()
        if self.lexeme_is_not(":"):
            print("ERROR: In parameter(), Expected ':'")
            return False
        self.print_token()
        if not self.qualifier():
            print("ERROR: In paramerer(), Expected <Qualifier>")
            self.consume = False
            return False

        print("\t<Parameter>".ljust(23)+"=> <IDs> : <Qualifier>")
        return True

    def parameter_list(self):
        """   <Parameter List>  ::=  <Parameter>  | <Parameter> , <Parameter List>   """

        if not self.parameter():
            print("ERROR: In parameter_list(), Expected <Parameter>")
            self.consume = False
            return False
        self.next_tok()
        if self.lexeme_is_not(","):
            print("\t<Parameter List>".ljust(23)+"=> <Parameter> | <Parameter>, <Parameter List>")
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
            print("\t<Opt Parameter List>".ljust(23)+"=> <Empty>")
        else:
            print("\t<Opt Parameter List>".ljust(23)+"=> <Parameter List>")
        return True

    def declaration(self):
        """   <Declaration> ::= <Qualifier > <IDs>   """

        if not self.qualifier():
            self.consume = False
            return False
        if not self.IDs():
            print("ERROR: In declaration(), Expected <IDs>")
            self.consume = False
            return False

        print("\t<Declaration>".ljust(23)+"=> <Qualifier> <IDs>")
        return True

    def declaration_list(self):
        """   <Declaration List>  := <Declaration> ;  | <Declaration> ; <Declaration List>   """

        if not self.declaration():
            self.consume = False
            return False
        self.next_tok()
        if self.lexeme_is_not(";"):
            print("ERROR: In declaration_list(), Expected ';'")
            return False
        self.print_token()
        if not self.declaration_list():
            self.consume = False

        print("\t<Declaration List>".ljust(23)+"=> <Declaration>; | <Declaration>; <Declaration List>")
        return True

    def opt_declaration_list(self):
        """<Opt Declaration List> ::= <Declaration List>  | <Empty>"""

        if not self.declaration_list():
            self.consume = False
            print("\t<Opt Declaration List>".ljust(23)+"=> <Empty>")
        else:
            print("\t<Opt Declaration List>".ljust(23)+"=> <Declaration List>")
        return True

    def term_prime(self):

        self.next_tok()

        # Case: Epsilon
        if self.next_token.lexeme not in {"*", "/"}:
            self.consume = False
            return True
        self.print_token()
        if not self.factor():
            print("ERROR: In term_prime(), Expected <Factor>")
            self.consume = False
            return False
        if not self.term_prime():
            self.consume = False
            return False
        return True

    def term(self):
        """   <Term> ::=  <Term> * <Factor>  | <Term> / <Factor> |  <Factor>   """

        if not self.factor():
            print("ERROR: In term(), Expected <Factor>")
            self.consume = False
            return False
        if not self.term_prime():
            self.consume = False
            return False

        print("\t<Term>")
        return True

    def expression_prime(self):

        self.next_tok()

        # Case: Epsilon
        if self.next_token.lexeme not in {"+", "-"}:
            self.consume = False
            return True
        self.print_token()
        if not self.term():
            print("ERROR: In expression_prime(), Expected <Term> ")
            self.consume = False
            return False
        if not self.expression_prime():
            self.consume = False
            return False

        return True

    def expression(self):
        """   <Expression>  ::= <Expression> + <Term>  | <Expression>  - <Term>  | <Term>   """

        if not self.term():
            print("ERROR: In expression(), Expected <Term>")
            self.consume = False
            return False
        if not self.expression_prime():
            self.consume = False
            return False

        print("\t<Expression>")
        return True

    def condition(self):
        """   <Condition> ::= <Expression> <Relop> <Expression>   """

        if not self.expression():
            print("ERROR: In condition(), Expected <Expression>")
            self.consume = False
            return False
        if not self.relop():
            print("ERROR: In condition(), Expected <Relop>")
            self.consume = False
            return False
        if not self.expression():
            print("ERROR: In condition(), Expected <Expression>")
            self.consume = False
            return False

        print("\t<Condition>".ljust(23)+"=> <Expression> <Relop> <Expression>")
        return True

    def write(self):
        """   <Write> ::=   write ( <Expression>);   """

        self.next_tok()

        if self.lexeme_is_not("write"):
            return False
        self.print_token()
        self.next_tok()
        if self.lexeme_is_not("("):
            print("ERROR: In write(), Expected '('")
            return False
        self.print_token()
        if not self.expression():
            print("ERROR: In write(), Expected <Expression>")
            self.consume = False
            return False
        self.next_tok()
        if self.lexeme_is_not(")"):
            print("ERROR: In write(), Expected ')'")
            return False
        self.print_token()
        self.next_tok()
        if self.lexeme_is_not(";"):
            print("ERROR: In write(), Expected ';'")
            return False
        self.print_token()

        print("\t<Write>".ljust(23)+"=> write ( <Expression>);")
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
            print("ERROR: In assign(), Expected ':='")
            return False
        self.print_token()
        if not self.expression():
            print("ERROR: In assign(), Expected <Expression>")
            self.consume = False
            return False
        self.next_tok()
        if self.lexeme_is_not(";"):
            print("ERROR: In assign(), Expected ';'")
            return False
        self.print_token()

        print("\t<Assign>".ljust(23)+"=> <Identifier> := <Expression> ;")
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
            print("ERROR: In _return(), Expected ';'")
            return False
        self.print_token()

        if not with_expression:
            print("\t<Return>".ljust(23)+"=> return ;")
        else:
            print("\t<Return>".ljust(23)+"=> return <Expression> ;")
        return True

    def _while(self):
        """   <While> ::= while ( <Condition> ) <Statement>    """

        self.next_tok()

        if self.lexeme_is_not("while"):
            return False
        self.print_token()
        self.next_tok()
        if self.lexeme_is_not("("):
            print("ERROR: In _while(), Expected '('")
            return False
        self.print_token()
        if not self.condition():
            self.consume = False
            return False
        self.next_tok()
        if self.lexeme_is_not(")"):
            print("ERROR: In _while(), Expected ')'")
            return False
        self.print_token()
        if not self.statement():
            print("ERROR: In _while(), Expected <Statement>")
            self.consume = False
            return False

        print("\t<While>".ljust(23)+"=> while ( <Condition> ) <Statement>")
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
            print("ERROR: In _if(), Expected 'if'")
            return False
        self.print_token()
        if not self.condition():
            print("ERROR: In _if(), Expected <Condition>")
            self.consume = False
            return False
        self.next_tok()
        if self.lexeme_is_not(")"):
            print("ERROR: In _if(), Expected ')'")
            return False
        self.print_token()
        if not self.statement():
            print("ERROR: In _if(), Expected <Statement>")
            self.consume = False
            return False
        self.next_tok()
        if self.lexeme_is_not("else"):
            if self.lexeme_is_not("fi"):
                print("ERROR: In _if(), Expected 'else' or 'fi'")
                print("Error")
                return False
            print("\t<If>".ljust(23)+"=> if ( <Condition>  ) <Statement> fi")
        # Case: if ( <Condition>  ) <Statement> fi
        self.print_token()
        if self.lexeme_is_not("else"):
            print("\t<If>")
            return True
        if not self.statement():
            print("ERROR: In _if(), Expected <Statement>")
            self.consume = False
            return False
        self.next_tok()
        if self.lexeme_is_not("fi"):
            print("ERROR: In _if(), Expected 'fi'")
            return False
        self.print_token()

        print("\t<If>".ljust(23)+"=> if ( <Condition>  ) <Statement> else <Statement> fi")
        return True

    def statement(self):
        """   <Statement> ::=  <Compound> | <Assign> | <If> |  <Return> | <Write> | <Read> | <While>   """

        if self.assign():
            print("\t<Statement>".ljust(23)+"=> <Assign>")
            return True
        if self._if():
            print("\t<Statement>".ljust(23)+"=> <If>")
            return True
        if self._return():
            print("\t<Statement>".ljust(23)+"=> <Return>")
            return True
        if self.write():
            print("\t<Statement>".ljust(23)+"=> <Write>")
            return True
        if self.read():
            print("\t<Statement>".ljust(23)+"=> <Read>")
            return True
        if self._while():
            print("\t<Statement>".ljust(23)+"=> <While>")
            return True
        if self.compound():
            print("\t<Statement>".ljust(23)+"=> <Compound>")
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
            print("\t<Statement List>".ljust(23)+"=> <Statement>  |  <Statement> <Statement List>")
        return True

    def compound(self):
        """   <Compound> ::= { <Statement List> }   """

        self.next_tok()

        if self.lexeme_is_not("{"):
            return False
        self.print_token()
        if not self.statement_list():
            print("ERROR: In compound(), Expected <Statement_List>")
            self.consume = False
            return False
        self.next_tok()
        if self.lexeme_is_not("}"):
            print("ERROR: In compound(), Expected '}'")
            return False
        self.print_token()

        print("\t<Compound>".ljust(23)+"=> { <Statement List> }")
        return True

    def body(self):
        """   <Body> ::= { < Statement List> }   """

        self.next_tok()

        if self.lexeme_is_not("{"):
            return False
        self.print_token()
        if not self.statement_list():
            print("ERROR: In body(), Expected <Statement_List>")
            self.consume = False
            return False
        self.next_tok()
        if self.lexeme_is_not("}"):
            print("ERROR: In body(), Expected '}' ")
            return False
        self.print_token()

        print("\t<Body>".ljust(23)+"=> { <Statements List> }")
        return True

    def function(self):
        """<Function> ::=  @  <Identifier> ( <Opt Parameter List> ) <Opt Declaration List> <Body>"""

        self.next_tok()

        if self.lexeme_is_not("@"):
            return False
        self.print_token()
        self.next_tok()
        if self.next_token.token is not "Identifier":
            print("ERROR: In function(), Expected <Identifier>")
            self.consume = False
            return False
        self.print_token()
        self.next_tok()
        if self.lexeme_is_not("("):
            print("ERROR: In function(), Expected '('")
            return False
        self.print_token()
        if self.opt_parameter_list():
            self.consume = False
        self.next_tok()
        if self.lexeme_is_not(")"):
            print("ERROR: In function(), Expected ')'")
            return False
        self.print_token()
        if self.opt_declaration_list():
            self.consume = False
        if not self.body():
            print("ERROR: In function(), Expected <Body>")
            self.consume = False
            return False

        print("\t<Function>".ljust(23)+"=> @ <Identifier> ( <Opt Parameter List> ) <Opt Declaration List> <Body>")
        return True

    def function_definitions(self):
        """   <Function Definitions>  ::= <Function> | <Function> <Function Definitions>    """

        if not self.function():
            self.consume = False
            return False
        if not self.function_definitions():
            self.consume = False
        print("\t<Function Definitions>".ljust(23)+"=> <Function> | <Function> <Function Definitions>")
        return True

    def opt_function_definitions(self):
        """   <Opt Function Definitions> ::= <Function Definitions> | <Empty>   """

        if not self.function_definitions():
            self.consume = False
            print("\t<Opt Function Definitions>".ljust(23)+"=> <Empty>")
        else:
            print("\t<Opt Function Definitions>".ljust(23)+"=> <Function Definitions>")
        return True

    def rat17f(self):
        """   <Rat17F>  ::=  <Opt Function Definitions>
                         %%  <Opt Declaration List> <Statement List>    """
        if not self.opt_function_definitions():
            self.consume = False
        self.next_tok()
        if self.lexeme_is_not("%%"):
            print("ERROR: In rat17f(), Expected '%%'")
            return False
        self.print_token()
        if not self.opt_declaration_list():
            self.consume = False
        if not self.statement_list():
            self.consume = False
            return False

        print("\t<Rat17f>".ljust(23)+"=> <Opt Function Definitions> %% <Opt Declaration List> <Statement List>")
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
