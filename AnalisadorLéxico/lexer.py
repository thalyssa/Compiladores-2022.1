import traceback
from abc import ABC, abstractmethod


# -----------------------------------------------------
# -----------------------------------------------------
# ----------------------- TOKEN -----------------------
# -----------------------------------------------------
# -----------------------------------------------------
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


# -----------------------------------------------------
# -----------------------------------------------------
# ----------------------- LEXER -----------------------
# -----------------------------------------------------
# -----------------------------------------------------
class Lexer:
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
                        LEX_DICT.OTHER['EOF'],
                        'EOF',
                        (self.row, self.col)
                    )

            current_char = self.next_char()
            process_state = None

            current_state = STATES[self.state](self)

            process_state = current_state.process_state(current_char)
            if process_state:
                return process_state


# ------------------------------------------------------
# ------------------------------------------------------
# --------------------- VALIDATION ---------------------
# ------------------------------------------------------
# ------------------------------------------------------
class Validation():
    def __init__(self, string):
        self.string = string

    def is_letter(self):
        return self.string.isalpha()

    def is_digit(self):
        return self.string.isdigit()

    def is_alphanumeric(self):
        return self.string.isalnum()

    def is_upper_case(self):
        return self.string.isupper()

    def is_lower_case(self):
        return self.string.islower()

    def is_operator(self):
        return self.string in ['<', '>', '=', '!']

    def is_space(self):
        return self.string.isspace()


# ----------------------------------------------------
# ----------------------------------------------------
# ---------------------- STATES ----------------------
# ----------------------------------------------------
# ----------------------------------------------------
class State(ABC):
    def __init__(self, lexer):
        self.lexer = lexer
    
    @abstractmethod
    def process_state(self, current_char):
        pass


class State_One(State):
    def process_state(self, current_char):
        validate = Validation(current_char)
        if validate.is_space():
            self.lexer.state = 1
        elif validate.is_lower_case():
            self.lexer.lexem += current_char
            self.lexer.state = 2
        elif validate.is_digit():
            self.lexer.lexem += current_char
            self.lexer.state = 4
        elif validate.is_operator():
            self.lexer.lexem += current_char
            self.lexer.state = 8
        elif current_char == '\"':
            self.lexer.lexem += current_char
            self.lexer.state = 9
        elif validate.is_upper_case():
            self.lexer.lexem += current_char
            self.lexer.state = 12
        elif current_char == '@':
            self.lexer.lexem += current_char
            self.lexer.state = 14
        elif current_char in OPERATORS_LIST:
            self.lexer.lexem += current_char
            self.lexer.col += 1
            return Token(
                LEX_DICT.OPERATORS[current_char],
                self.lexer.lexem,
                (self.lexer.row, self.lexer.col)
            )
        elif current_char in DELIMITERS_LIST:
            self.lexer.lexem += current_char
            self.lexer.col += 1
            return Token(
                LEX_DICT.DELIMITERS[current_char],
                self.lexer.lexem,
                (self.lexer.row, self.lexer.col)
            )
        else:
            Token(
                LEX_DICT.ERRORS['ERR_UNKNOWN'],
                self.lexer.lexem,
                (self.lexer.row, self.lexer.col)
            )


class State_Two(State):
    def process_state(self, current_char):
        validate = Validation(current_char)
        if validate.is_space() or validate.is_operator() or not validate.is_alphanumeric():
            self.lexer.back()
            self.lexer.state = 3
        elif validate.is_digit() or validate.is_upper_case() or validate.is_lower_case():
            self.lexer.lexem += current_char
        else:
            self.lexer.col += 1
            Token(
                LEX_DICT.ERRORS['ERR_IDENTIFIER'],
                self.lexer.lexem,
                (self.lexer.row, self.lexer.col)
            )


class State_Three(State):
    def process_state(self, current_char):
        self.lexer.back()
        self.lexer.col += 1
        return Token(
            LEX_DICT.IDENTIFIERS['ID'],
            self.lexer.lexem,
            (self.lexer.row, self.lexer.col)
        )


class State_Four(State):
    def process_state(self, current_char):
        validate = Validation(current_char)
        if current_char == '.':
            self.lexer.lexem += current_char
            self.lexer.state = 5
            self.lexer.col += 1
        elif not validate.is_alphanumeric():
            self.lexer.back()
            self.lexer.state = 6
        elif validate.is_digit():
            self.lexer.lexem += current_char
        else:
            self.lexer.col += 1
            Token(
                LEX_DICT.ERRORS['ERR_NUMERIC'],
                self.lexer.lexem,
                (self.lexer.row, self.lexer.col)
            )


class State_Five(State):
    def process_state(self, current_char):
        validate = Validation(current_char)
        if validate.is_digit():
            self.lexer.lexem += current_char
        elif validate.is_space() or validate.is_operator() or not validate.is_alphanumeric():
            self.lexer.back()
            self.lexer.state = 7
        else:
            self.lexer.col += 1
            Token(
                LEX_DICT.ERRORS['ERR_NUMERIC'],
                self.lexer.lexem,
                (self.lexer.row, self.lexer.col)
            )


class State_Six(State):
    def process_state(self, current_char):
        self.lexer.back()
        self.lexer.col += 1
        return Token(
            LEX_DICT.IDENTIFIERS['IDEN_INT'],
            self.lexer.lexem,
            (self.lexer.row, self.lexer.col)
        )


class State_Seven(State):
    def process_state(self, current_char):
        self.lexer.back()
        self.lexer.col += 1
        return Token(
            LEX_DICT.IDENTIFIERS['IDEN_FLOAT'],
            self.lexer.lexem,
            (self.lexer.row, self.lexer.col)
        )


class State_Eight(State):
    def process_state(self, current_char):
        self.lexer.back()
        self.lexer.back()
        current_char = self.lexer.next_char()

        if current_char == '<':
            current_char = self.lexer.next_char()
            self.lexer.col += 1

            if current_char == '=':
                self.lexer.lexem += current_char
                return Token(
                    LEX_DICT.OPERATORS['OPE_LE'],
                    self.lexer.lexem,
                    (self.lexer.row, self.lexer.col)
                )
            else:
                self.lexer.back()
                return Token(
                    LEX_DICT.OPERATORS['<'],
                    self.lexer.lexem,
                    (self.lexer.row, self.lexer.col)
                )
        elif current_char == '>':
            current_char = self.lexer.next_char()
            self.lexer.col += 1

            if current_char == '=':
                self.lexer.lexem += current_char
                return Token(
                    LEX_DICT.OPERATORS['OPE_GE'],
                    self.lexer.lexem,
                    (self.lexer.row, self.lexer.col)
                )
            else:
                self.lexer.back()
                return Token(
                    LEX_DICT.OPERATORS['>'],
                    self.lexer.lexem,
                    (self.lexer.row, self.lexer.col)
                )
        elif current_char == '!' or current_char == '=':
            current_char = self.lexer.next_char()
            self.lexer.col += 1

            if current_char == '=':
                self.lexer.lexem += current_char
                return Token(
                    LEX_DICT.OPERATORS['OPE_REL'],
                    self.lexer.lexem,
                    (self.lexer.row, self.lexer.col)
                )
            else:
                self.lexer.back()
                return Token(
                    LEX_DICT.OPERATORS['!'],
                    self.lexer.lexem,
                    (self.lexer.row, self.lexer.col)
                )
        else:
            Token(
                LEX_DICT.ERRORS['ERR_UNKNOWN'],
                self.lexer.lexem,
                (self.lexer.row, self.lexer.col)
            )


class State_Nine(State):
    def process_state(self, current_char):
        if chr(32) <= current_char <= chr(126):
            self.lexer.lexem += current_char
            current_char = self.lexer.next_char()

            if current_char == '\"':
                self.lexer.lexem += current_char
                self.lexer.state = 10
            else:
                self.lexer.back()
                self.lexer.state = 11
        else:
            self.lexer.col += 1
            Token(
                LEX_DICT.ERRORS['ERR_CHAR'],
                self.lexer.lexem,
                (self.lexer.row, self.lexer.col)
            )


class State_Ten(State):
    def process_state(self, current_char):
        self.lexer.back()
        self.lexer.col += 1
        return Token(
            LEX_DICT.IDENTIFIERS['IDEN_CHAR'],
            self.lexer.lexem,
            (self.lexer.row, self.lexer.col)
        )


class State_Eleven(State):
    def process_state(self, current_char):
        if chr(32) <= current_char <= chr(126):
            self.lexer.lexem += current_char

            if current_char == '\"':
                self.lexer.col += 1
                return Token(
                    LEX_DICT.IDENTIFIERS['IDEN_STRING'],
                    self.lexer.lexem,
                    (self.lexer.row, self.lexer.col)
                )
        else:
            self.lexer.col += 1
            Token(
                LEX_DICT.ERRORS['ERR_CHARACTER'],
                self.lexer.lexem,
                (self.lexer.row, self.lexer.col)
            )


class State_Twelve(State):
    def process_state(self, current_char):
        validate = Validation(current_char)
        if validate.is_space() or not validate.is_lower_case():
            self.lexer.back()
            self.lexer.state = 13
        elif validate.is_lower_case():
            self.lexer.lexem += current_char


class State_Thirteen(State):
    def process_state(self, current_char):
        self.lexer.back()
        self.lexer.col += 1

        if LEX_DICT.RESERVED_WORDS[self.lexer.lexem][1] is not None:
            return Token(
                LEX_DICT.RESERVED_WORDS[self.lexer.lexem],
                self.lexer.lexem,
                (self.lexer.row, self.lexer.col)
            )
        else:
            return Token(
                LEX_DICT.ERRORS['ERR_RW'],
                self.lexer.lexem,
                (self.lexer.row, self.lexer.col)
            )


class State_Fourteen(State):
    def process_state(self, current_char):
        self.lexer.next_line()
        self.lexer.content = self.lexer.text
        self.lexem.lexem = ''
        self.lexer.state = 0


STATES = {
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

# ------------------------------------------------------
# ------------------------------------------------------
# ------------------ LEXEM DICTIONARY ------------------
# ------------------------------------------------------
# ------------------------------------------------------
class LEX_DICT:
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
