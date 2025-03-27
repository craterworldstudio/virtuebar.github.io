from token_i import *
from constants_i import *
from error_i import *
from position_i import Position
from parser_i import *
from nodes_i import *
import os

###########################################
# LEXER
###########################################

class Lexer:
	def __init__(self, fn, text, path=False):
		self.text = text
		self.fn = os.path.basename(fn) if path == True else "<shell>"
		self.pos = Position(-1, 0, -1, fn, text)
		self.current_char = None
		self.advance()

	def getLineData(self):
		return self.linecount, self.Prog

	def advance(self):
		self.pos.advance(self.current_char) 
		self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

	def make_tokens(self):
		tokens = []
		self.untacted_indexes = []

		self.linecount = 0
		while self.current_char != None:

			if self.current_char in ' \t':
				self.advance()
						
			elif self.current_char in DIGITS:
				tokens.append(self.make_number())

			elif self.current_char in LETTERS:
				tokens.append(self.make_identifier())

			elif self.current_char == '"':
				tokens.append(self.make_stringwith2q())

			elif self.current_char == "'":
				tokens.append(self.make_stringwith1q())

			elif self.current_char == '$':
				self.advance()

				if self.current_char == '>':
					self.skip_comment(True)

				if self.current_char == '{':
					tokens.append(Token(TT_HLCRBRAC, pos_start = self.pos))
					self.advance()

				if self.current_char == '$':
					self.skip_comment()

			elif self.current_char in [';', '\n']:
				tokens.append(Token(TT_NEWLINE, pos_start=self.pos))
				self.untacted_indexes.append(self.pos)
				self.advance()

			elif self.current_char == '+':
				tokens.append(Token(TT_PLUS, pos_start = self.pos))
				self.advance()

			elif self.current_char == '-':
				tokens.append(Token(TT_MINUS, pos_start = self.pos))
				self.advance()
		
			elif self.current_char == '*':
				tokens.append(Token(TT_MUL, pos_start = self.pos))
				self.advance()
	
			elif self.current_char == '/':
				tokens.append(Token(TT_DIV, pos_start = self.pos))
				self.advance()
						
			elif self.current_char == '(':
				tokens.append(Token(TT_LPAREN, pos_start = self.pos))
				self.advance()
				
			elif self.current_char == ')':
				tokens.append(Token(TT_RPAREN, pos_start = self.pos))
				self.advance()				

			elif self.current_char == '[':
				tokens.append(Token(TT_LSQUARE, pos_start = self.pos))
				self.advance()
						
			elif self.current_char == ']':
				tokens.append(Token(TT_RSQUARE, pos_start = self.pos))
				self.advance()

			elif self.current_char == '~':
				tokens.append(Token(TT_POWER, pos_start = self.pos))
				self.advance()

			elif self.current_char == '{':
				tokens.append(Token(TT_LCRBRAC, pos_start= self.pos))
				self.advance()

			elif self.current_char == '}':
				self.advance()
				if self.current_char == '$':
					tokens.append(Token(TT_HRCRBRAC, pos_start= self.pos))
				else:
					tokens.append(Token(TT_RCRBRAC, pos_start= self.pos))
					self.advance()

			elif self.current_char == ".":
				tokens.append(Token(TT_ATTR, value='.',pos_start = self.pos))
				self.advance()

			elif self.current_char == '!':
				tok, error = self.make_not_equals()
				if error: return [], error
				tokens.append(tok)

			elif self.current_char == '=':
				tokens.append(self.make_equals())

			elif self.current_char == '<':
				tokens.append(self.make_less_than())

			elif self.current_char == '>':
				tokens.append(self.make_greater_than())

			elif self.current_char == ',':
				tokens.append(Token(TT_COMMA, pos_start = self.pos))
				self.advance()

			elif self.current_char == ':':
				tokens.append(Token(TT_COLON, pos_start = self.pos))
				self.advance()

			else:
				pos_start = self.pos.copy()
				char = self.current_char
				self.advance()
				return [], [],IllegalCharError(pos_start, self.pos, "'" + char + "'")
		
		tokens.append(Token(TT_EOF, pos_start = self.pos))
		self.untacted_indexes.append(self.pos)
		self.make_line_division(tokens)
		#print(self.linecount)
		#print(tokens)#, self.untacted_indexes)
		return tokens, (self.linecount, self.Prog, self.untacted_indexes), None

	def make_line_division(self, tokens):
		line = []
		TotalProgram = []
		
		SEP1 = TT_NEWLINE
		SEP2 = TT_EOF

		SEP = (SEP1, SEP2)
		#print(SEP)

		for i in tokens:
			#print(i, type(i))
			#print(True if i == TT_NEWLINE else False)
			#print(str(i))
			if str(i) in SEP:
				
				TotalProgram.append(line)
				line = []
			else:
				line.append(i)

		self.Prog = TotalProgram
		self.linecount = len(TotalProgram)
		#print(self.Prog, self.linecount)


	def make_number(self):
		num_str = ''
		dot_count = 0
		pos_start = self.pos.copy()

		while self.current_char != None and self.current_char in DIGITS + '.' :
			if self.current_char == '.':
				if dot_count == 1: break
				dot_count += 1
				num_str += '.'
			else:
				num_str += self.current_char
			self.advance()


		if dot_count == 0:
			return Token(TT_INT, int(num_str), pos_start, self.pos)
		else:
			return Token(TT_FLOAT, float(num_str), pos_start, self.pos)

	def make_identifier(self):
		iden_str = ''
		pos_start = self.pos.copy()

		while self.current_char != None and self.current_char in LETTERS_DIGITS + '_':
			iden_str += self.current_char
			self.advance()

		tok_type = TT_KEYWORD if iden_str in KEYWORDS else TT_IDENTIFIER
		#print(tok_type, iden_str)
		return Token(tok_type, iden_str, pos_start, self.pos)

	def make_not_equals(self):
		pos_start = self.pos.copy()
		self.advance()

		if self.current_char == '=':
			self.advance()
			return Token(TT_NE, pos_start=pos_start,pos_end=self.pos), None

		self.advance()
		return None, ExpectedCharError(pos_start, self.pos, "'=' after '!'")
		
	def make_equals(self):
		tok_type = TT_EQ
		pos_start = self.pos.copy()
		self.advance()

		if self.current_char == '=':
			self.advance()
			tok_type = TT_EE

		elif self.current_char == '>':
			self.advance()
			tok_type = TT_ARROW

		return Token(tok_type, pos_start = pos_start, pos_end = self.pos)

	def make_less_than(self):
		tok_type = TT_LT
		pos_start = self.pos.copy()
		self.advance()

		if self.current_char == '=':
			self.advance()
			tok_type = TT_LTE

		return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

	def make_greater_than(self):
		tok_type = TT_GT
		pos_start = self.pos.copy()
		self.advance()

		if self.current_char == '=':
			self.advance()
			tok_type = TT_GTE

		return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

	def make_stringwith2q(self):
		string = ''
		pos_start = self.pos.copy()
		escape_character = False
		e_c_starter = '//'
		self.advance()

		escape_characters = {
			'n': '/n', #new line
			't': '/t', #tab space
			'r': '/r'  #carriage return
		}
		while self.current_char != None and (self.current_char != '"' or escape_character):
			if escape_character:
				string += escape_characters.get(self.current_char, self.current_char)
				escape_character = False
			else:
				if self.current_char == e_c_starter:
					escape_character = True
				else:
					string += self.current_char
			self.advance()
		
		self.advance()
		return Token(TT_STRING, string, pos_start, self.pos)
	
	def make_stringwith1q(self):
		string = ''
		pos_start = self.pos.copy()
		escape_character = False
		e_c_starter = '//'
		self.advance()

		escape_characters = {
			'n': '/n', #new line
			't': '/t', #tab space
			'r': '/r'  #carriage return
		}
		while self.current_char != None and (self.current_char != "'" or escape_character):
			if escape_character:
				string += escape_characters.get(self.current_char, self.current_char)
				escape_character = False
			else:
				if self.current_char == e_c_starter:
					escape_character = True
				else:
					string += self.current_char
			self.advance()
		
		self.advance()
		return Token(TT_STRING, string, pos_start, self.pos)

	def skip_comment(self, multi=False):
		self.advance()

		if multi:
			while self.current_char != '$':
				self.advance()
		else:
			while self.current_char not in '\n;':
				self.advance()

		self.advance()
