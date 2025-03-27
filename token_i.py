###########################################
# TOKENS
###########################################

TT_INT          = 'INT'
TT_FLOAT        = 'FLOAT'
TT_STRING       = 'STRING'
TT_IDENTIFIER   = 'IDENTIFIER'
TT_KEYWORD      = 'KEYWORD'
'''
Keywords
- val - variable
- with - and operator
- or - or operator
- inver - not operator
- const - Constant
- if - If statement
- act - Do if statement
- elif - Else If statement
- other - Else statement
- for - For Loop statement
- while - While Loop statement
- to - In for Loop statement
- step - Amount of Value to skip while iterating
- func - Function Declaration Statement
- end - End a loop, condition or function statement
- return - return value/values
- break - break out a loop
- skip - Skip a iteration
- goto - goto a specific line
- SET - SET the attr of a var or func
- GET - GET the attr of a var or func
- addlib - Add a library or a Header file to the source file
- Header - Define the starting of a header file code in a header file
- CWD - Define the current working directory
- abs - Define a absolute value for a operator. In use- Addlib

'''

TT_ATTR         = 'ATTR' #Attribute '.'

TT_EE           = 'EE'   #Dounle Equals to
TT_NE           = 'NE'   #Not Equals to
TT_LT           = 'LT'   #Less Than
TT_GT           = 'GT'   #Greater Than
TT_LTE          = 'LTE'  #Less than equals to
TT_GTE          = 'GTE'  #Greater then equals to
TT_EQ           = 'EQ'   #Equals

TT_PLUS         = 'PLUS'
TT_MINUS        = 'MINUS'
TT_MUL          = 'MUL'
TT_DIV          = 'DIV'
TT_POWER        = 'POWER'

TT_LPAREN       = 'LPAREM'
TT_RPAREN       = 'RPAREM'
TT_LSQUARE      = 'LSQUARE'
TT_RSQUARE      = 'RSQUARE'
TT_LCRBRAC      = 'LCRBRAC'
TT_RCRBRAC      = 'RCRBRAC'
TT_HLCRBRAC     = 'HLCRBRAC'
TT_HRCRBRAC     = 'HRCRBRAC'
TT_COMMA        = 'COMMA'
TT_NEWLINE      = 'NEWLINE'
TT_ARROW        = 'ARROW'
TT_COLON        = 'COLON'

TT_EOF          = 'EOF'                 #End of file

#No. of tokens currently = 26

KEYWORDS = [
    'val',
    'with',  #AND
    'or',
    'inver', #Not
    'const',  #Constant
    'if',
    'act', # Do
    'elif',  #Else If
    'other',  #Else
    'for',
    'to',
    'step',
    'while',
    'end', #End a statement
    'func', #Function
    'return', #Returns value/values
    'skip',
    'break',
    'goto', # go to a specific line
    'SET', # SET the attr of a var or func
    'GET', #GET the attr of a var or func
    'addlib', #import a lib
    'Header', # Declare a Header File
    'CWD', # Define the C.W.D for the source file
    'abs', # Define a absolute value for a operator
    'stdlib' # import a built-in lib
]

class Token:
    def __init__(self, type_, value = None, pos_start=None, pos_end=None):
        self.type = type_
        self.value = value

        if pos_start: 
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()

        if pos_end: self.pos_end = pos_end

    def matches(self, type_, value):
        return self.type == type_ and self.value == value

    def __repr__(self):
        if self.value: return f'{self.type}:{self.value}'
        return f'{self.type}'
