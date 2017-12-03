#!/usr/bin/python3
"""Handles Syntax Analysis"""
# By Josh Najera
import sys
import inspect
import lexical_analyzer
from inspect import currentframe as c_frame
from inspect import getouterframes as o_frame
from pathlib import Path
from collections import namedtuple as nt

class Semantics(object):
    '''  Handles semantic actions, actions such as instruction and symbol table management   '''

    sym = nt('ID_Entry', 'address type')
    instr = nt('Instr', 'Op Oprnd')

    def __init__(self):
        '''Inits'''
        # Might have to change it from a table to something else
        self.instruction_table = ['[Index]=Instr_address: (Op, Operand)']
        self.sym_table = dict()
        self.j_stack = []


    def addr(self):
        '''   Gets address   '''
        return len(self.instruction_table)

    
    def print_table(self):
        '''   Prints out entire Instruction Table   '''
        print()
        print("Symbol Table".center(30))
        print("-------------------------------------------")
        print("{}\t|\t{}\t|\t{}".format('Var', 'Value', 'Type'))
        for item, value in self.sym_table.items():
            print("{}\t|\t{}\t|\t{}".format(item, value[0], value[1]))

        print()
        print("Instruction Table".center(30))
        print("{}\t|\t{}\t|\t{}".format('Addr', 'Op', 'Oprnd'))
        print("-------------------------------------------")
        for i, item in enumerate(self.instruction_table[1:]):
            print("{}\t|\t{}\t|\t{}".format((i+1), item.Op, item.Oprnd))


    def gen_sym(self, id_symbol, id_type):
        '''   Generates a new symbol table entry for id_symbol   '''
        if id_symbol in self.sym_table:
            print("ERROR: {} is already defined".format(id_symbol))
            return False
        self.sym_table[id_symbol] = self.sym(1000 + len(self.sym_table), id_type)
        return True
        

    def gen_instr(self, instruction_name, address=None): # get_addr(id) ):
        '''   Generates a new table instruction table entry auto increment address   '''
        self.instruction_table.append(self.instr(instruction_name, address))


    def get_addr(self, id_symbol):
        '''   Gets the address of an identifier   '''
        if id_symbol in self.sym_table:
            return self.sym_table[id_symbol].address
        else:
            print('ERROR: Identifier {} undefined'.format(id_symbol))
            return False


    def push_jump_stack(self, instr_addr=None):
        '''   Pushes an instruction address onto j_stack so it can be used to back patch   '''
        '''   If no argument, the address of the last instruction is used   '''
        if not instr_addr:
            instr_addr = len(self.instruction_table)
        self.j_stack.append(instr_addr)


    def back_patch(self, jump_addr=None):
        '''   Patchs the top of j_stack with jump_addr   '''
        if not jump_addr:
            jump_addr = len(self.instruction_table)
        addr = self.j_stack.pop()
        self.instruction_table[addr] = self.instr(self.instruction_table[addr].Op, jump_addr)



class SyntaxAnalyzer(object):
    """   Checks syntax according to ra17f rules   """

    def __init__(self, file_name, CONSOLE_DEBUG):
        self.CONSOLE_DEBUG = CONSOLE_DEBUG
        self.has_errors = False
        self.mode = None
        self.semantic = Semantics()
        in_file = open(file_name)
        self.out_file = open("output.txt", 'w')
        self.next_token = lexical_analyzer.Lexer.result("token", "lexeme", 0)
        self.consume = True
        self.lexer = lexical_analyzer.Lexer()
        self.lex = self.lexer.tokenize(in_file)
        self.rat17f()
        self.out_file.close()
        in_file.close()

    # Idea: Add check in next_tok to make sure we don't have 'extra_token_consumed' flag raised before consuming
    def next_tok(self):
        """   Fetches next token/lexeme pair, if allowed   """

        if not self.consume:
            self.consume = True
            return

        try:
            self.next_token = next(self.lex)
            return self.next_token
        except StopIteration:
            return False

    def print_token(self):
        """   Prints the token-lexeme pair   """

        if self.has_errors:
            return
        output = "Token: {} Lexeme: {}".format(self.next_token.token.ljust(23), self.next_token.lexeme)
        if self.CONSOLE_DEBUG:
            print(output)
        self.out_file.write(output+'\n')

    def print_production(self, lhs='', rhs=''):
        """   Prints and saves the production rule given   """

        if self.has_errors:
            return
        output = "R:\t<{}>".format(lhs).ljust(30)
        if len(rhs) > 0:
            output = output + "=>\t   {}".format(rhs)
        if self.CONSOLE_DEBUG:
            print(output)
        self.out_file.write(output+'\n')

    def error(self, expected=''):
        """   Prints an error report   """

        # Only print the display the first error.  I can't handle error-recovery yet.
        caller = inspect.stack()[1][3]
        if not self.has_errors:
            report = "\nERROR:  Line {}\n\tIn function:\t'{}()' \n\tReceived:\t{}  \n\tExpected:\t{}\nProduction call Stack:"\
                .format(self.next_token.line_number, caller, self.next_token.lexeme, expected)
            if self.CONSOLE_DEBUG:
                print(report)
            self.out_file.write(report+'\n')
        else:
            report = "\t'{}()'".format(caller)
            if self.CONSOLE_DEBUG:
                print(report)
            self.out_file.write(report+'\n')
        self.has_errors = True

    def lexeme_is_not(self, char):
        """   Determines if the lexeme is NOT input, if not, dont consume token on next next_tok() call"""

        if self.next_token.lexeme != char:
            self.consume = False
            return True
        return False

    def IDs(self, qualif=None):
        """   <IDs> ::= <Identifier> | <Identifier>, <IDs>    """

        # Consume next token from generator ?
        self.next_tok()

        # Case: Not <IDs>
        if self.next_token.token is not "Identifier":
            self.consume = False
            return False

        self.print_token()
        # If there is a qualifier passed, we are making a new entry

        if qualif:
            self.semantic.gen_sym(self.next_token.lexeme, qualif)
        else:
            if self.mode == 'write':
                addr = self.semantic.get_addr(self.next_token.lexeme)
                self.semantic.gen_instr('PUSHM', addr)
            if self.mode == 'read':
                addr = self.semantic.get_addr(self.next_token.lexeme)
                # self.semantic.
                self.semantic.gen_instr('POPM', addr)

        self.next_tok()
        # Case: <Identifier>
        if self.lexeme_is_not(","):
            self.mode = None
            self.print_production('IDs')
            return True

        self.print_token()
        # Case: <Identifier>, not <IDs>
        if not self.IDs(qualif):
            self.consume = False
            return False

        # Case: <IDs>
        return True

    def primary(self):
        """   <Primary> ::= <Identifier> | <Integer> | <Identifier> [<IDs>]
                           | ( <Expression> ) |  <Real>  | true | false   """

        # Consume next token from generator ?
        self.next_tok()
        lex = self.next_token.lexeme

        if self.next_token.token is "Identifier":
            self.semantic.gen_instr('PUSHM',self.semantic.get_addr(lex))
            self.print_token()
            self.next_tok()
            # Case: <Identifier>
            if self.lexeme_is_not('['):
                self.print_production('Primary', '<Identifier>')
                return True
            self.print_token()
            if not self.IDs():
                self.consume = False
                return False
            self.next_tok()
            if self.lexeme_is_not(']'):
                self.error(']')
                return False
            self.print_token()

            # Case: <Identifier>[<IDs>]
            self.print_production('Primary', '<Identifier> [<IDs>]')
            return True

        if self.lexeme_is_not("("):
            # Cases: <Float> OR <Integer> OR "true" OR "false"
            if self.next_token.token in {"Float", "Integer"}:
                self.print_token()
                self.consume = True
                self.print_production('Primary', "<{}>".format(self.next_token.token))
                self.semantic.gen_instr('PUSHI', self.next_token.lexeme)
                return True
            if self.next_token.lexeme in {"true", "false"}:
                self.print_token()
                self.consume = True
                self.print_production('Primary', "<{}>".format(self.next_token.lexeme))
                return True
            # Case: Not primary
            self.consume = False
            return False

        # Case: ( . . .
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
        self.print_production('Primary', '( <Expression> )')
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

        # Semantic actions?  Ids > possibility of more than one > stdin needs to read and save to each?
        self.semantic.gen_instr('STDIN')
        self.mode = 'read'

        if not self.IDs(None):
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

        # Case: <Read> ::= read ( <IDs> );
        self.print_production('Read', 'read ( <IDs> );')
        return True

    def relop(self):
        """   <Relop> ::=   = |  /=  |   >   | <   |  =>   | <=   """

        # Consume next token from generator
        self.next_tok()

        # Case: Not a relational operator
        if self.next_token.lexeme not in {'=', '/=', '>', '<', '=>', '<='}:
            self.error('relational operator (\'=\', \'/=\', \'>\', \'<\', \'=>\', \'<=\')')
            self.consume = False
            return False

        self.print_token()
        # Case: Relational Operator
        self.print_production('Relop', '')
        return True

    def factor(self):
        """   <Factor> ::= - <Primary> | <Primary>   """

        # Consume next token from generator
        self.next_tok()

        neg = False
        # Case: <Primary>
        if self.lexeme_is_not('-'):
            self.consume = False
        else:
            neg = True
            self.semantic.gen_instr('PUSHI', '-1')
            self.print_token()

        # Case: - <Primary>
        if not self.primary():
            self.consume = False
            return False

        if neg:
            self.semantic.gen_instr('MUL ')
            self.print_production('Factor', '-<Primary>')
        else:
            self.print_production('Factor', '<Primary>')
        return True

    def qualifier(self):
        """   < Qualifier >::= integer | boolean | floating   """

        # Consume next token from generator
        self.next_tok()

        if self.next_token.lexeme not in {"integer", "boolean", "floating"}:
            self.consume = False
            return False

        self.print_token()
        self.print_production('Qualifier', '<{}>'.format(self.next_token.lexeme))
        return True

    def parameter(self):
        """   <Parameter> ::= <IDs > : <Qualifier>   """

        if not self.IDs():
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

        self.print_production('Parameter', '<IDs> : <Qualifier>')
        return True

    def parameter_list(self):
        """   <Parameter List>  ::=  <Parameter>  | <Parameter> , <Parameter List>   """

        if not self.parameter():
            self.consume = False
            return False
        self.next_tok()
        if self.lexeme_is_not(","):
            self.print_production('Parameter List', '<Parameter> | <Parameter>, <Parameter List>')
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
            self.print_production('Opt Parameter List', '<Empty>')
        else:
            self.print_production('Opt Parameter List', '<Parameter List>')
        return True

    def declaration(self):
        """   <Declaration> ::= <Qualifier > <IDs>   """

        if not self.qualifier():
            self.consume = False
            return False
        qualif = self.next_token.lexeme
        if not self.IDs(qualif):
            self.error('<IDs>')
            self.consume = False
            return False

        self.print_production('Declaration', '<Qualifier> <IDs>')
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

        self.print_production('Declaration List', '<Declaration>; | <Declaration>; <Declaration List>')
        return True

    def opt_declaration_list(self):
        """   <Opt Declaration List> ::= <Declaration List>  | <Empty>   """

        if not self.declaration_list():
            self.consume = False
            self.print_production('Opt Declaration List', '<Empty>')
        else:
            self.print_production('Opt Declaration List', '<Declaration List>')
        return True

    def term_prime(self):

        self.next_tok()

        # Case: Epsilon
        lex = self.next_token.lexeme
        if lex not in {"*", "/"}:
            self.consume = False
            return True
        self.print_token()
        if not self.factor():
            self.error('<Factor>')
            self.consume = False
            return False
        if lex is '*':
            self.semantic.gen_instr('MUL ')
        elif lex is '/':
            self.semantic.gen_instr('DIV ')
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

        self.print_production('Term', '')
        return True

    def expression_prime(self):

        self.next_tok()

        # Case: Epsilon
        lex = self.next_token.lexeme
        if lex not in {"+", "-"}:
            self.consume = False
            return True
        self.print_token()
        if not self.term():
            self.error('<Term>')
            self.consume = False
            return False
        if lex is '+':
            self.semantic.gen_instr('ADD ')
        elif lex is '-':
            self.semantic.gen_instr('SUB ')
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

        self.print_production('Expression', '')
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

        # Conditional semantics
        rel = self.next_token.lexeme

        if not self.expression():
            self.error('<Expression>')
            self.consume = False
            return False

        # Conditional semantics
        if rel == '>':
            self.semantic.gen_instr('GRE')
        elif rel == '<':
            self.semantic.gen_instr('LES')
        elif rel == '=':
            self.semantic.gen_instr('EQU')
        elif rel == '/=':
            self.semantic.gen_instr('NEQ')
        elif rel == '=>':
            self.semantic.gen_instr('GEQ')
        elif rel == '<=':
            self.semantic.gen_instr('LEQ')

        self.print_production('Condition', '<Expression> <Relop> <Expression>')
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

        self.mode = 'write'

        self.print_token()
        if not self.expression():
            self.error('<Expression>')
            self.consume = False
            return False

        self.semantic.gen_instr('STDOUT')

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

        self.print_production('Write', 'write ( <Expression>);')
        return True

    def assign(self):
        """   <Assign> ::= <Identifier> := <Expression> ;   """

        self.next_tok()

        if self.next_token.token is not "Identifier":
            self.consume = False
            return False

        self.semantic.gen_instr('PUSHM', self.semantic.get_addr(self.next_token.lexeme))

        save = self.next_token.lexeme
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

        addr = self.semantic.get_addr(save)
        self.semantic.gen_instr('POPM', addr)

        self.next_tok()
        if self.lexeme_is_not(";"):
            self.error(';')
            return False
        self.print_token()

        self.print_production('Assign', '<Identifier> := <Expression> ;')
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
            self.print_production('Return', 'return ;')
        else:
            self.print_production('Return', 'return <Expression> ;')
        return True

    def _while(self):
        """   <While> ::= while ( <Condition> ) <Statement>    """

        self.next_tok()

        if self.lexeme_is_not("while"):
            return False

        # Save current address so we can jump back to it at end of loop
        # Then we can re-run the comparison
        addr = self.semantic.addr()
        self.semantic.gen_instr("LABEL")

        self.print_token()
        self.next_tok()
        if self.lexeme_is_not("("):
            self.error('(')
            return False
        self.print_token()
        if not self.condition():
            self.consume = False
            return False

        # TODO-- Conditional semantics
        self.semantic.push_jump_stack() 
        # Saves current address for JUMPZ, so later it can be back-patched
        # This is so if the comparison is false
        #   we can jump to a point outside of the loop
        self.semantic.gen_instr('JUMPZ')

        self.next_tok()
        if self.lexeme_is_not(")"):
            self.error(')')
            return False
        self.print_token()
        if not self.statement():
            self.error('<Statement>')
            self.consume = False
            return False

        # End of while loop, jump back to 'addr' to restart
        self.semantic.gen_instr('JUMP', addr)
        # Back-patch out 'while condition'  ( backpatch JUMPZ)
        self.semantic.back_patch()

        self.print_production('While', 'while ( <Condition> ) <Statement>')
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

        self.semantic.push_jump_stack()
        # Save current instruction address (JUMPZ) to back-patch
        self.semantic.gen_instr('JUMPZ')

        self.next_tok()
        if self.lexeme_is_not(")"):
            self.error(')')
            return False
        self.print_token()
        if not self.statement():
            self.error('<Statement>')
            self.consume = False


        self.next_tok()
        if self.lexeme_is_not("else"):
            if self.lexeme_is_not("fi"):
                # Case: Missing else and fi
                self.error('\'else\' or \'fi\'')
                return False
            self.consume = True
            self.print_production('If', 'if ( <Condition>  ) <Statement> fi')

            # Back-patch our JUMPZ
            self.semantic.back_patch()

            return True
                
        # Back-patch our JUMPZ
        self.semantic.gen_instr('JUMP',)
        self.semantic.back_patch()
        self.semantic.push_jump_stack(self.semantic.addr() - 1)

        # Case: if ( <Condition>  ) <Statement> fi
        self.print_token()
        # if self.lexeme_is_not("else"):
        #     print("\t<fi>")  # TODO WTF is this?
        #     return True
        if not self.statement():
            self.error('<Statement>')
            self.consume = False
            return False
        self.next_tok()
        if self.lexeme_is_not("fi"):
            self.error('fi')
            return False
        self.semantic.back_patch()
        self.print_token()

        self.print_production('If', 'if ( <Condition>  ) <Statement> else <Statement> fi')
        return True

    def statement(self):
        """   <Statement> ::=  <Compound> | <Assign> | <If> |  <Return> | <Write> | <Read> | <While>   """

        if self.compound():
            self.print_production('Statement', '<Compound>')
            return True
        if self.assign():
            self.print_production('Statement', '<Assign>')
            return True
        if self._if():
            self.print_production('Statement', '<If>')
            return True
        if self._return():
            self.print_production('Statement', '<Return>')
            return True
        if self.write():
            self.print_production('Statement', '<Write>')
            return True
        if self.read():
            self.print_production('Statement', '<Read>')
            return True
        if self._while():
            self.print_production('Statement', '<While>')
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
            self.print_production('Statement List', '<Statement>  |  <Statement> <Statement List>')
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

        self.print_production('Compound', '{ <Statement List> }')
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

        self.print_production('Body', '{ <Statement List> }')
        return True

    def function(self):
        """   <Function> ::=  @  <Identifier> ( <Opt Parameter List> ) <Opt Declaration List> <Body>   """

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

        self.print_production('Function', '@ <Identifier> ( <Opt Parameter List> ) <Opt Declaration List> <Body>')
        return True

    def function_definitions(self):
        """   <Function Definitions>  ::= <Function> | <Function> <Function Definitions>    """

        if not self.function():
            self.consume = False
            return False
        if not self.function_definitions():
            self.consume = False
        self.print_production('Function Definitions', '<Function> | <Function> <Function Definitions>')
        return True

    def opt_function_definitions(self):
        """   <Opt Function Definitions> ::= <Function Definitions> | <Empty>   """

        if not self.function_definitions():
            self.consume = False
            self.print_production('Opt Function Definitions', '<Empty>')
        else:
            self.print_production('Opt Function Definitions', '<Function Definitions>')
        return True

    def rat17f(self):
        """   <Rat17F>  ::=  <Opt Function Definitions>
                         %%  <Opt Declaration List> <Statement List>    """
        if not self.opt_function_definitions():
            self.consume = False
        self.next_tok()
        if self.lexeme_is_not("%%"):
            self.error('%%')
            print("\n=== FAILED SYNTAX ANALYSIS ===")
            return False
        self.print_token()
        if not self.opt_declaration_list():
            self.consume = False
        if not self.statement_list():
            self.error('<Statement List>')
            print("\n=== FAILED SYNTAX ANALYSIS ===")
            self.consume = False
            return False

        self.print_production('Rat17f', '<Opt Function Definitions> %% <Opt Declaration List> <Statement List>')

        if self.has_errors:
            print("\n=== FAILED SYNTAX ANALYSIS ===")
        else:
            print("\n=== PASSED SYNTAX ANALYSIS ===")
        self.semantic.print_table()
        return True


def main():
    """ Runs Syntax Analysis upon a given file """
    ### Arguments: [optional]-- relative file path

    if len(sys.argv) == 2:
        file = sys.argv[1]
    else:
        file = "input.txt"

    my_file = Path(file)
    if my_file.is_file():
        print("\'{}\' found, processing...".format(file))
    else:
        print("\'{}\' is not a valid file!".format(file))
        exit()

    CONSOLE_DEBUG = False
    while(True):
        # dbg = input("Do you want console output? 1: Yes, 2: No \n>> ")
        dbg = '1'
        if dbg not in {'1', '2'}:
            print("Invalid input.")
            continue
        if dbg is '1':
            CONSOLE_DEBUG = True
        break

    my_SA = SyntaxAnalyzer(file, CONSOLE_DEBUG)
    input("Press enter to exit.")


if __name__ == "__main__":
    main()
