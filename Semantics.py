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
        self.type_stack = []


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
            print('ERROR: Identifier {} unidefined'.format(id_symbol))
            return False


    def get_type(self, id_symbol):
        '''   Gets the type of an identifier   '''
        if id_symbol in self.sym_table:
            return self.sym_table[id_symbol].type
        else:
            print('ERROR: Identifier {} unidefined'.format(id_symbol))
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
