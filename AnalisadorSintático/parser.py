import traceback
from abc import ABC, abstractmethod

class Token:
    def __init__(self, tkn_cat, lexem, position):
        self.tkn_cat = tkn_cat
        self.lexem = lexem
        self.position = position
    
    def __repr__(self):
        position = f'[{self.position[0]:>4}, {self.position[1]:>4}]'
        value_category = f'({self.tkn_cat[1]:>4}, {self.tkn_cat[0]:<20})'
        lexem = f'{self.lexem}'
        return f'              {position} {value_category:<25} {lexem}'

class Parser(ABC):
    def __init__(self, file_path):
        self.lexem = ''
        self.row = self.col = self.pos = 1
        self.state = self.pos = 0
        self.current_line = ' '
        self.content = list(self.current_line)

        try:
            self.file_reader = open(file_path, 'rb')
        except IOError as e:
            print(f'Error: {e}')
            traceback.print_exc()
    
    def next_line(self):
        aux = ''

        try:
            aux = self.file_reader.readline().decode('utf-8')
        except IOError as e:
            print(f'Error: {e}')
            traceback.print_exc()
        
        if aux != '':
            self.current_line = aux
            self.print_info()
            self.current_line += ' '
            self.row += 1
            self.pos = self.col = 0

            return True

        return False
    
    def next_char(self):
        self.pos += 1
        return self.content[self.pos - 1]

    def back(self):
        self.pos -= 1
    
    def print_info(self):
        print(f'{self.row} - {self.current_line}')

    def is_EOF(self):
        return self.pos == len(self.content)
    
    def next_token(self):
        self.state = 1
        self.lexem = ''
        while True:
            if self.is_EOF():
                if self.next_line():
                    self.content = list(self.current_line)
                else:
                    return Token(
                        PARSER_DICT.OTHER['EOF'],
                        'EOF',
                        (self.row, self.col)
                    )

            current_char = self.next_char()
            process_state = None

            current_state = PARSER_STATES[self.state](self)

            process_state = current_state.process_state(current_char)
            if process_state:
                return process_state

class NodePair:
    def __init__(self, rightNode: Token, leftNode: Token):
        self.rightNode = rightNode
        self.leftNode = leftNode
    
    def __repr__(self):
        self.rightNode.__repr__()
        self.leftNode.__repr__()
        return

class VariableTable:
    # Classe para a tabela de variáveis

    varTable = {}
    
    #Adiciona uma variável na tabela
    def add_variable(varTable, var, value):
        if var not in varTable:
            varTable[var] = value
            return True
        else:
            print('ERRO: Variável já instanciada')
            return False
    
    #Muda o valor da variável na tabela
    def change_variable_value(varTable, var, value):
        if var not in varTable:
            print('ERRO: Variável não encontrada')
            return False
        else:
            varTable[var] = value
            return True
    
    #Retorna o valor de uma variável na tabela
    def get_variable_value(varTable, var):
        if var not in varTable:
            print('ERRO: Variável não encontrada')
            return False
        else:
            return varTable.get(var)

#Incompleto
class State(ABC):
    def __init__(self, lexer):
        self.lexer = lexer
    
    @abstractmethod
    def process_state(self, current_char):
        pass

    def State_One():
        pass
    
    PARSER_STATES = {
    1:  State_One,
    2:  State_Two,
    3:  State_Three,
    4:  State_Four,
    5:  State_Five,
    6:  State_Six,
    7:  State_Seven,
    8:  State_Eight,
    9:  State_Nine,
    10: State_Ten,
    11: State_Eleven,
    12: State_Twelve,
    13: State_Thirteen,
    14: State_Fourteen
}

class PARSER_DICT:
        RESERVED_WORDS = {
        'Int':      ('RW_INT',      1 ),
        'float':    ('RW_FLOAT',    2 ),
        'Char':     ('RW_CHAR',     3 ),
        'String':   ('RW_STRING',   4 ),
        'Bool':     ('RW_BOOL',     5 ),
        'Begin':    ('RW_BEGIN',    6 ),
        'End':      ('RW_END',      7 ),
        'If':       ('RW_IF',       8 ),
        'Else':     ('RW_ELSE',     9 ),
        'While':    ('RW_WHILE',    10),
        'From':     ('RW_FROM',     11),
        'To':       ('RW_TO',       12),
        'Increase': ('RW_INCREASE', 13),
        'Get':      ('RW_GET',      14),
        'Show':     ('RW_SHOW',     15),
        'Return':   ('RW_RETURN',   16),
        'Function': ('RW_FUNCTION', 17),
        'True':     ('RW_TRUE',     18),
        'False':    ('RW_FALSE',    19),
        'Array':    ('RW_ARRAY',    20),
        'Empty':    ('RW_EMPTY',    21),
        'And':      ('OPE_CONJ',    22),
        'Or':       ('OPE_DISJ',    23)
    }

        OPERATORS = {
            '+':       ('OPE_ADD',  24),
            '-':       ('OPE_SUB',  25),
            '*':       ('OPE_MUL',  26),
            '/':       ('OPE_DIV',  27),
            '=':       ('OPE_ATR',  28),
            '<':       ('OPE_LT',   29),
            '>':       ('OPE_GT',   30),
            'OPE_LE':  ('OPE_LE',   31),
            'OPE_GE':  ('OPE_GE',   32),
            'OPE_REL': ('OPE_REL',  33),
            '!':       ('OPE_NEG',  34)
        }

        IDENTIFIERS = {
            'ID':          ('ID',          35),
            'IDEN_INT':    ('IDEN_INT',    36),
            'IDEN_FLOAT':  ('IDEN_FLOAT',  37),
            'IDEN_BOOL':   ('IDEN_BOOL',   38),
            'IDEN_CHAR':   ('IDEN_CHAR',   39),
            'IDEN_STRING': ('IDEN_STRING', 40),
            'IDEN_ARRAY':  ('IDEN_ARRAY',  41)
        }

        DELIMITERS = {
            'Begin': ('DELI_BEGIN',   42),
            'End':   ('DELI_END',     43),
            '(':     ('DELI_OPAREN',  44),
            ')':     ('DELI_CPAREN',  45),
            '[':     ('DELI_OBRAC',   46),
            ']':     ('DELI_CBRAC',   47),
            '{':     ('DELI_OCURLY',  48),
            '}':     ('DELI_CCURLY',  49),
            ',':     ('DELI_COMMA',   50),
            ';':     ('DELI_SEMICOL', 51)
        }

        ERRORS = {
            'ERR_UNKNOWN':    ('ERR_UNKNOWN',    52),
            'ERR_IDENTIFIER': ('ERR_IDENTIFIER', 53),
            'ERR_NUMERIC':    ('ERR_NUMERIC',    54),
            'ERR_RW':         ('ERR_RW',         55),
            'ERR_CHARACTER':  ('ERR_CHARACTER',  56),
        }

        OTHER = {
            'EOF':     ('OTHER_EOF',     57),
            'COMMENT': ('OTHER_COMMENT', 58)
        }

        OPERATORS_LIST = ['+', '-', '*', '/', '!']
        DELIMITERS_LIST = ['(', ')', '[', ']', '{', '}', ',', ';']