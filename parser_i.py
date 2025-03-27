from token_i import *
from nodes_i import *
from error_i import *
import inspect

###########################################
# PARSE RESULT
###########################################


class ParseResult:
	def __init__(self):
		self.error = None
		self.node = None
		self.last_registered_advance_count = 0
		self.advance_count = 0
		self.to_reverse_count = 0

	def register_advancement(self):
		self.last_registered_advance_count = 0
		#print("Advancing...")
		self.advance_count += 1

	def register(self, res):
		self.last_registered_advance_count = res.advance_count
		self.advance_count += res.advance_count
		if res.error: self.error = res.error
		return res.node

	def success(self, node):
		self.node = node
		try: self.type = node._type
		except: pass
		return self

	def failure(self, error):
		#print(self.advance_count)
		if not self.error or self.advance_count == 0:
			#print("Failure Detected!")
			self.error = error
		return self

	def try_register(self, res):
		if res.error:
			self.to_reverse_count = res.advance_count
			return None
		return self.register(res)

###########################################
# PARSER
###########################################


class Parser:
	def __init__(self, tokens, header = False):
		self.tokens = tokens
		self.tok_idx = 0
		self.current_tok = self.tokens[self.tok_idx]
		#self.advance()
		self.header = header
		self.headerFileStart = False
		self.headerFileEnd = False

	def advance(self):
		self.tok_idx += 1
		caller_frame = inspect.stack()[1]
		line_number = caller_frame[0].f_lineno
		#print("ADV: ",self.current_tok, f' called from line {line_number}')
		self.update_current_tok()
		return self.current_tok

	def reverse(self, amount=1):
		self.tok_idx -= amount
		self.update_current_tok()
		return self.current_tok

	def update_current_tok(self):
		if self.tok_idx >= 0 and self.tok_idx < len(self.tokens):
			self.current_tok = self.tokens[self.tok_idx]
			#print(self.current_tok, f'{self.tok_idx}/{len(self.tokens)}')

	def parse(self):
		res = self.statements()
		#print(self.current_tok.type)
		#print(res.error)
		#print('EEND ',self.current_tok)
		
		if not res.error and self.current_tok.type != TT_EOF:
			#print('EEND ',self.current_tok)
			if self.current_tok.type == TT_HRCRBRAC and self.headerFileEnd == True:
				res.register_advancement()
				self.advance()
				#print('EEND ',self.current_tok)
				if self.current_tok.type != TT_EOF:
					return res.failure(InvalidSyntaxError(
					self.current_tok.pos_start, self.current_tok.pos_end,
					"Expected '+', '-', '*', '/' or '^'"
				))
			else:
				#print(1)
				return res.failure(InvalidSyntaxError(
					self.current_tok.pos_start, self.current_tok.pos_end,
					"Expected '+', '-', '*', '/' or '^'"
				))
			
		if self.current_tok.type == TT_EOF and self.headerFileEnd == False and self.header == True:
			return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				" the '}$' at the end for the header file"
			))

		return res

	###################################

	def statements(self):
		res = ParseResult()
		statements = []
		pos_start = self.current_tok.pos_start.copy()

		while self.current_tok.type == TT_NEWLINE:
			res.register_advancement()
			self.advance()
		if self.header == True:
			#print(self.current_tok)
			
			if self.current_tok.matches(TT_KEYWORD, 'Header'):
				self.header = False
				self.headerFileStart = True
				res.register_advancement()
				self.advance()

				if self.current_tok.type != TT_HLCRBRAC:
					return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				"Expected '${'" ))

				res.register_advancement()
				self.advance()

				#print(self.current_tok)
				while self.current_tok.type == TT_NEWLINE:
					res.register_advancement()
					self.advance()

				#print(self.current_tok)
				statement = res.register(self.statement())
				if res.error: return res
				statements.append(statement)

				more_statements = True

				while True:
					newline_count = 0
					while self.current_tok.type == TT_NEWLINE:
						res.register_advancement()
						self.advance()
						newline_count += 1

					if newline_count == 0:
						more_statements = False

					if not more_statements: break

					#if self.current_tok.type != TT_RCRBRAC:
					#	return res.failure(InvalidSyntaxError(
					#	self.current_tok.pos_start, self.current_tok.pos_end,
					#	"Expected '}'"
					#	))
					#res.register_advancement()
					#self.advance()

					statement = res.try_register(self.statement())
					if not statement: 
						self.reverse(res.to_reverse_count)
						more_statements = False
						continue
					statements.append(statement)

				return res.success(ListNode(
					statements,
					pos_start,
					self.current_tok.pos_end.copy()
				))
			else:
				#if not self.current_tok.matches(TT_KEYWORD, 'Header') and self.headerFileStart == False:
				#print(self.current_tok)
				#else:
				return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				"Expected  a 'Header' keyword at the starting for header file" #a 'run' function or
			))


		else:
			statement = res.register(self.statement())
			if res.error: return res
			statements.append(statement)

			more_statements = True

			while True:
				newline_count = 0
				while self.current_tok.type == TT_NEWLINE:
					res.register_advancement()
					self.advance()
					newline_count += 1

				if newline_count == 0:
					more_statements = False

				if not more_statements: break
				statement = res.try_register(self.statement())
				if not statement: 
					self.reverse(res.to_reverse_count)
					more_statements = False
					continue
				statements.append(statement)

			return res.success(ListNode(
				statements,
				pos_start,
				self.current_tok.pos_end.copy()
			))
			 
	def statement(self):
		res = ParseResult()
		pos_start = self.current_tok.pos_start.copy()

		if self.current_tok.matches(TT_KEYWORD, 'return'):
			res.register_advancement()
			self.advance()

			expr = res.try_register(self.expr())
			if not expr:
				self.reverse(res.to_reverse_count)
			return res.success(ReturnNode(expr, pos_start, self.current_tok.pos_start.copy()))

		if self.current_tok.matches(TT_KEYWORD, 'skip'):
			res.register_advancement()
			self.advance()

			return res.success(SkipNode(pos_start, self.current_tok.pos_start.copy()))

		if self.current_tok.matches(TT_KEYWORD, 'break'):
			res.register_advancement()
			self.advance()

			return res.success(BreakNode(pos_start, self.current_tok.pos_start.copy()))
		
		if self.current_tok.type == TT_HRCRBRAC:
			self.headerFileEnd = True
			res.register_advancement()
			self.advance()

		expr = res.register(self.expr())

		if res.error: return res.failure(InvalidSyntaxError(
			self.current_tok.pos_start, self.current_tok.pos_end,
			"Expected 'addlib', 'return', 'skip', 'break','val', 'const', 'if', 'for', 'while', 'func', int, float, identifier, 'SET', 'GET', '+', '-', '(', '[', '}$','goto' or 'inver"
		))
		if self.current_tok.type == TT_HRCRBRAC:
			self.headerFileEnd = True

		return res.success(expr)

	def if_expr(self):
		res = ParseResult()
		all_cases = res.register(self.if_expr_cases('if'))
		if res.error: return res
		cases, else_case = all_cases
		return res.success(IfNode(cases, else_case))

	def if_expr_rule2(self):
		return self.if_expr_cases('elif')

	def if_expr_rule3(self):
		res = ParseResult()
		else_case = None

		if self.current_tok.matches(TT_KEYWORD, 'other'):
			res.register_advancement()
			self.advance()
			
			if self.current_tok.type == TT_NEWLINE:
				res.register_advancement()
				self.advance()

				statements = res.register(self.statements())
				if res.error: return res
				else_case = (statements, True)

				if self.current_tok.matches(TT_KEYWORD, 'end'):
					res.register_advancement()
					self.advance()
				else:
					return res.failure(InvalidSyntaxError(
						self.current_tok.pos_start, self.current_tok.pos_end,
						"Expected 'end'"
					))
			else:
				expr = res.register(self.statement())
				if res.error: return res
				else_case = (expr, False)
		
		return res.success(else_case)

	def if_expr_others(self):
		res = ParseResult()
		cases, else_case = [], None

		if self.current_tok.matches(TT_KEYWORD, 'elif'):
			all_cases = res.register(self.if_expr_rule2())
			if res.error: return res
			cases, else_case = all_cases
		else:
			else_case = res.register(self.if_expr_rule3())
			if res.error: return res

		return res.success((cases, else_case))

	def if_expr_cases(self, case_keyword):
		res = ParseResult()
		cases = []
		else_case = None

		if not self.current_tok.matches(TT_KEYWORD, case_keyword):
			return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				f"Expected '{case_keyword}'"
			))

		res.register_advancement()
		self.advance()

		condition = res.register(self.expr())
		if res.error: return res

		if not self.current_tok.matches(TT_KEYWORD, 'act'):
			return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				f"Expected 'act'"
			))

		res.register_advancement()
		self.advance()

		if self.current_tok.type == TT_NEWLINE:
			res.register_advancement()
			self.advance()

			statements = res.register(self.statements())
			if res.error: return res
			cases.append((condition, statements, True))

			if self.current_tok.matches(TT_KEYWORD, 'end'):
				res.register_advancement()
				self.advance()
			else:
				all_cases = res.register(self.if_expr_others())
				if res.error: return res
				new_cases, else_case = all_cases
				cases.extend(new_cases)
		
		else:
			expr = res.register(self.statement())
			if res.error: return res
			cases.append((condition, expr, False))

			all_cases = res.register(self.if_expr_others())
			if res.error: return res
			new_cases, else_case = all_cases
			cases.extend(new_cases)

		return res.success((cases, else_case))

	def goto_expr(self):
		res = ParseResult()

		res.register_advancement()
		self.advance()

		if self.current_tok.type != TT_INT:
			return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				f"Expected a Number(Integer)!"
			))
		
		line = self.current_tok
		#print("Line ", line)	
		res.register_advancement()
		self.advance()

		return res.success(GoToNode(NumberNode(line), self.current_tok.pos_start, self.current_tok.pos_start.copy()))
	
	def addlib_expr(self):
		res = ParseResult()

		res.register_advancement()
		self.advance()

		if self.current_tok.matches(TT_KEYWORD, 'abs'):
			res.register_advancement()
			self.advance()

			if self.current_tok.type != TT_STRING:
				return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				f"Expected a Absolute Path(String)!"
				))

			filename = self.current_tok
			res.register_advancement()
			self.advance()
			return res.success(AddLibNode(StringNode(filename), True, self.current_tok.pos_start, self.current_tok.pos_start.copy()))
		
		if self.current_tok.type != TT_IDENTIFIER:
			return res.failure(InvalidSyntaxError(
			self.current_tok.pos_start, self.current_tok.pos_end,
			f"Expected a Valid Filename(Identifier)!"
		))

		filename = self.current_tok
		res.register_advancement()
		self.advance()
		return res.success(AddLibNode(StringNode(filename), False, self.current_tok.pos_start, self.current_tok.pos_start.copy()))


	def cwd_expr(self):
		res = ParseResult()

		res.register_advancement()
		self.advance()

		if self.current_tok.type == TT_STRING:
			cwd = self.current_tok
		else:
			return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				f"Expected a Path(String)!"
			))
		
		res.register_advancement()
		self.advance()
		return res.success(CWDNode(StringNode(cwd), self.current_tok.pos_start, self.current_tok.pos_start.copy()))
	
	def stdlib_expr(self):
		res = ParseResult()

		res.register_advancement()
		self.advance()

		if self.current_tok.type == TT_IDENTIFIER:
			stdlib = self.current_tok
		else:
			return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				f"Expected a valid package!"
			))
		
		res.register_advancement()
		self.advance()
		return res.success(STDLibNode(StringNode(stdlib), self.current_tok.pos_start, self.current_tok.pos_start.copy()))
	
	def for_expr(self):
		res = ParseResult()

		if not self.current_tok.matches(TT_KEYWORD, 'for'):
			return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				f"Expected 'for'"
			))

		res.register_advancement()
		self.advance()

		if self.current_tok.type != TT_IDENTIFIER:
			return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				f"Expected identifier"
			))

		var_name = self.current_tok
		res.register_advancement()
		self.advance()

		if self.current_tok.type != TT_EQ:
			return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				f"Expected '='"
			))

		res.register_advancement()
		self.advance()

		start_value = res.register(self.statement())
		if res.error: return res

		if not self.current_tok.matches(TT_KEYWORD, 'to'):
			return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				f"Expected 'to'"
			))

		res.register_advancement()
		self.advance()

		end_value = res.register(self.expr())
		if res.error: return res

		if self.current_tok.matches(TT_KEYWORD, 'step'):
			res.register_advancement()
			self.advance()

			step_value = res.register(self.expr())
			if res.error: return res
		else:
			step_value = None

		if not self.current_tok.matches(TT_KEYWORD, 'act'):
			return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				f"Expected 'act'"
			))

		res.register_advancement()
		self.advance()

		if self.current_tok.type == TT_NEWLINE:
			res.register_advancement()
			self.advance()

			body = res.register(self.statements())
			if res.error: return res

			if not self.current_tok.matches(TT_KEYWORD, 'end'):
				return res.failure(InvalidSyntaxError(
					self.current_tok.pos_start, self.current_tok.pos_end,
					f"Expected 'end'"
				))

			res.register_advancement()
			self.advance()

			return res.success(ForNode(var_name, start_value, end_value, step_value, body, True))


		body = res.register(self.statement())
		if res.error: return res

		return res.success(ForNode(var_name, start_value, end_value, step_value, body, False))

	def while_expr(self):
		res = ParseResult()

		if not self.current_tok.matches(TT_KEYWORD, 'while'):
			return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				f"Expected 'while'"
			))

		res.register_advancement()
		self.advance()

		condition = res.register(self.expr())
		if res.error: return res

		if not self.current_tok.matches(TT_KEYWORD, 'act'):
			return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				f"Expected 'act'"
			))

		res.register_advancement()
		self.advance()

		if self.current_tok.type == TT_NEWLINE:
			res.register_advancement()
			self.advance()

			code = res.register(self.statements())
			if res.error: return res

			if not self.current_tok.matches(TT_KEYWORD, 'end'):
				return res.failure(InvalidSyntaxError(
					self.current_tok.pos_start, self.current_tok.pos_end,
					f"Expected 'end'"
				))

			res.register_advancement()
			self.advance()

			return res.success(WhileNode(condition, code, True))

		code = res.register(self.statement())
		if res.error: return res

		return res.success(WhileNode(condition, code, False))

	def func_def(self):
		res = ParseResult()

		if not self.current_tok.matches(TT_KEYWORD, 'func'):
			return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				f"Expected 'func'"
			))

		res.register_advancement()
		self.advance()

		if self.current_tok.type == TT_IDENTIFIER:
			var_name_tok = self.current_tok
			res.register_advancement()
			self.advance()
			if self.current_tok.type != TT_LPAREN:
				return res.failure(InvalidSyntaxError(
					self.current_tok.pos_start, self.current_tok.pos_end,
					f"Expected '('"
				))
		else:
			var_name_tok = None
			if self.current_tok.type != TT_LPAREN:
				return res.failure(InvalidSyntaxError(
					self.current_tok.pos_start, self.current_tok.pos_end,
					f"Expected identifier or '('"
				))

		res.register_advancement()
		self.advance()

		arg_name_toks = []

		if self.current_tok.type == TT_IDENTIFIER:
			arg_name_toks.append(self.current_tok)
			res.register_advancement()
			self.advance()

			while self.current_tok.type == TT_COMMA:
				res.register_advancement()
				self.advance()

				if self.current_tok.type != TT_IDENTIFIER:
					return res.failure(InvalidSyntaxError(
						self.current_tok.pos_start, self.current_tok.pos_end,
						f"Expected identifier"
					))

				arg_name_toks.append(self.current_tok)
				res.register_advancement()
				self.advance()

			if self.current_tok.type != TT_RPAREN:
				return res.failure(InvalidSyntaxError(
					self.current_tok.pos_start, self.current_tok.pos_end,
					f"Exprect ',' or ')'"
				))

		else:
			if self.current_tok.type != TT_RPAREN:
				return res.failure(InvalidSyntaxError(
					self.current_tok.pos_start, self.current_tok.pos_end,
					f"Expected identifier or ')'"
				))

		res.register_advancement()
		self.advance()

		if self.current_tok.type == TT_ARROW:

			res.register_advancement()
			self.advance()

			node_to_return = res.register(self.expr())
			if res.error: return res

			return res.success(FuncDefNode(
					var_name_tok,
					arg_name_toks,
					node_to_return,
					True
				))

		if self.current_tok.type != TT_LCRBRAC:
			return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				"Exprected '=>' or '{'"
			))
		
		res.register_advancement()
		self.advance()

		body = res.register(self.statements())
		if res.error: return res

		if not self.current_tok.type == TT_RCRBRAC:
			return res.failure(InvalidSyntaxError(
			self.current_tok.pos_start, self.current_tok.pos_end,
			"Expected '}'"
		))

		res.register_advancement()
		self.advance()

		return res.success(FuncDefNode(
			var_name_tok,
			arg_name_toks,
			body, 
			False
			))

	def atom(self):
		res = ParseResult()
		tok = self.current_tok
		#print("Tok:",tok)

		if tok.type in (TT_INT, TT_FLOAT):
			res.register_advancement()
			self.advance()
			return res.success(NumberNode(tok))

		elif tok.type == TT_STRING:
			res.register_advancement()
			self.advance()
			return res.success(StringNode(tok))

		elif tok.type == TT_IDENTIFIER:
			res.register_advancement()
			self.advance()
			return res.success(VarAccessNode(tok))

		elif tok.type == TT_LPAREN:
			res.register_advancement()
			self.advance()
			expr = res.register(self.expr())
			if res.error: return res

			if self.current_tok.type == TT_RPAREN:
				res.register_advancement()
				self.advance()
				return res.success(expr)
			else:
				return res.failure(InvalidSyntaxError(
					self.current_tok.pos_start, self.current_tok.pos_end,
					"Expected ')'"
				))

		elif tok.matches(TT_KEYWORD, 'if'):
			if_expr = res.register(self.if_expr())
			if res.error: return res
			return res.success(if_expr)

		elif tok.matches(TT_KEYWORD, 'for'):
			for_expr = res.register(self.for_expr())
			if res.error: return res
			return res.success(for_expr)

		elif tok.matches(TT_KEYWORD, 'while'):
			while_expr = res.register(self.while_expr())
			if res.error: return res
			return res.success(while_expr)

		elif tok.matches(TT_KEYWORD, 'func'):
			#print('!')
			func_def = res.register(self.func_def())
			if res.error: return res
			return res.success(func_def)

		elif tok.type == TT_LSQUARE:
			list_expr = res.register(self.list_expr())
			if res.error: return res
			return res.success(list_expr)
		
		elif tok.matches(TT_KEYWORD, 'goto'):
			goto_expr = res.register(self.goto_expr())
			if res.error: return res
			return res.success(goto_expr)
		
		elif tok.matches(TT_KEYWORD, 'addlib'):
			addlib_expr = res.register(self.addlib_expr())
			if res.error: return res
			return res.success(addlib_expr)
		
		elif tok.matches(TT_KEYWORD, 'CWD'):
			cwd_expr = res.register(self.cwd_expr())
			if res.error: return res
			return res.success(cwd_expr)
		
		elif tok.matches(TT_KEYWORD, 'stdlib'):
			stdlib_expr = res.register(self.stdlib_expr())
			if res.error: return res
			return res.success(stdlib_expr)

		return res.failure(InvalidSyntaxError(
			tok.pos_start, tok.pos_end,
			"Expected 'addlib', int, float, identifier, '+', '-', '(', '[','if', 'for', 'while' or 'func'"
		))

	def power(self):
		return self.bin_op(self.call, (TT_POWER, ), self.factor)

	def call(self):
		res = ParseResult()
		atom = res.register(self.atom())
		if res.error: return res

		if self.current_tok.type == TT_LPAREN:
			res.register_advancement()
			self.advance()
			arg_nodes = []

			if self.current_tok.type == TT_RPAREN:
				res.register_advancement()
				self.advance()
			else:
				arg_nodes.append(res.register(self.expr()))
				if res.error:return res.failure(InvalidSyntaxError(
						self.current_tok.pos_start, self.current_tok.pos_end,
						"Expected ')', 'val', 'goto', 'if', 'for', 'while', 'func', int, float, identifier, '+', '-', '(' , '[' or 'inver'"
					))

				while self.current_tok.type == TT_COMMA:
					res.register_advancement()
					self.advance()

					arg_nodes.append(res.register(self.expr()))
					if res.error: return res

				if self.current_tok.type != TT_RPAREN:
					return res.failure(InvalidSyntaxError(
						self.current_tok.pos_start, self.current_tok.pos_end,
						f"Expected ',' or ')'"
					))
				#print(1, self.current_tok)
				res.register_advancement()
				self.advance()
				#print(2, self.current_tok)
			return res.success(CallNode(atom, arg_nodes))
		return res.success(atom)

	def factor(self):
		res = ParseResult()
		tok = self.current_tok

		if tok.type in (TT_PLUS, TT_MINUS):
			res.register_advancement()
			self.advance()
			factor = res.register(self.factor())
			if res.error: return res
			return res.success(UnaryOpNode(tok, factor))

		return self.power()

	def term(self):
		return self.bin_op(self.factor, (TT_MUL, TT_DIV, TT_COLON))

	def arith_expr(self):
		return self.bin_op(self.term, (TT_PLUS, TT_MINUS))

	def list_expr(self):
		res = ParseResult()
		element_nodes = []
		pos_start = self.current_tok.pos_start.copy()

		if self.current_tok.type != TT_LSQUARE:
			return res.failure(InvalidSyntaxError(
		    self.current_tok.pos_start, self.current_tok.pos_end,
		    f"Expected '['"
		  ))
		
		res.register_advancement()
		self.advance()

		if self.current_tok.type == TT_RSQUARE:
			res.register_advancement()
			self.advance()
		else:
			element_nodes.append(res.register(self.expr()))
			if res.error: return res.failure(InvalidSyntaxError(
		      self.current_tok.pos_start, self.current_tok.pos_end,
		      "Expected ']', 'val', 'if', 'for', 'while', 'func', int, float, identifier, '+', '-', '(', '[' or 'NOT'"
		    ))

			while self.current_tok.type == TT_COMMA:
				res.register_advancement()
				self.advance()

				element_nodes.append(res.register(self.expr()))
				if res.error: return res

			if self.current_tok.type != TT_RSQUARE:
				return res.failure(InvalidSyntaxError(
		    	self.current_tok.pos_start, self.current_tok.pos_end,
		    	f"Expected ',' or ']'"
		    	))

		res.register_advancement()
		self.advance()

		return res.success(ListNode(
			element_nodes,
			pos_start,
			self.current_tok.pos_end.copy()
		))

	def com_expr(self):
		res = ParseResult()

		if self.current_tok.matches(TT_KEYWORD, 'inver'):
			op_tok = self.current_tok
			res.register_advancement()
			self.advance()

			node = res.register(self.com_expr())
			if res.error: return res
			return res.success(UnaryOpNode(op_tok, node))

		node = res.register(self.bin_op(
			self.arith_expr, (TT_EE, TT_NE, TT_LT, TT_GT, TT_LTE, TT_GTE)))

		if res.error: return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				"Expected int, float, identifier, '+', '-', '(', '[' or 'inver'"
			))

		return res.success(node)

	def expr(self):
		res = ParseResult()
		self.attr_def = False
		#print(self.current_tok)

		if self.current_tok.matches(TT_KEYWORD, 'val'):
			res.register_advancement()
			self.advance()

			if self.current_tok.type != TT_IDENTIFIER:
				return res.failure(InvalidSyntaxError(
					self.current_tok.pos_start, self.current_tok.pos_end,
					"Expected identifier"
				))

			var_name = self.current_tok
			res.register_advancement()
			self.advance()

			if self.current_tok.type == TT_ATTR:
				self.attr_def = True
				res.register_advancement()
				self.advance()

			if self.current_tok.type != TT_EQ:
				return res.failure(InvalidSyntaxError(
					self.current_tok.pos_start, self.current_tok.pos_end,
					"Expected '='"
				))

			res.register_advancement()
			self.advance()
			expr = res.register(self.expr())
			if res.error: return res

			return res.success(VarAssignNode(var_name, expr, 'val'))

		if self.current_tok.matches(TT_KEYWORD, 'const'):
			res.register_advancement()
			self.advance()

			if self.current_tok.type != TT_IDENTIFIER:
				return res.failure(InvalidSyntaxError(
					self.current_tok.pos_start, self.current_tok.pos_end,
					"Expected identifier"
				))

			var_name = self.current_tok
			res.register_advancement()
			self.advance()

			if self.current_tok.type == TT_ATTR:
				self.attr_def = True
				res.register_advancement()
				self.advance()

			if self.current_tok.type != TT_EQ:
				return res.failure(InvalidSyntaxError(
					self.current_tok.pos_start, self.current_tok.pos_end,
					"Expected '='"
				))

			res.register_advancement()
			self.advance()
			expr = res.register(self.expr())
			if res.error: return res
			return res.success(VarAssignNode(var_name, expr, 'const'))
		
		if self.current_tok.matches(TT_KEYWORD, 'SET'):
			res.register_advancement()
			self.advance()

			self.key = []
			while self.current_tok.type != TT_EQ and self.current_tok.type != TT_NEWLINE:
				#print(self.current_tok.type)
				if self.current_tok.type == TT_NEWLINE:
					return res.failure(InvalidSyntaxError(
					self.current_tok.pos_start, self.current_tok.pos_end,
					"Expected '='"
				))
 
				if self.current_tok.type == TT_IDENTIFIER or self.current_tok.type == TT_ATTR:
					self.key.append(self.current_tok)
					res.register_advancement()
					self.advance()
				else:
					res.register_advancement()
					self.advance()
			#print(self.key)
			attr = self.key.pop(-1)
			parent = self.key

			if self.current_tok.type != TT_EQ:
				return res.failure(InvalidSyntaxError(
					self.current_tok.pos_start, self.current_tok.pos_end,
					"Expected '='"
				))

			res.register_advancement()
			self.advance()
			
			expr = res.register(self.expr())
			if res.error: return res
			#print(parent, attr)
			return res.success(SetNode(parent, attr, expr, self.current_tok.pos_start, self.current_tok.pos_start.copy()))
		
		
		if self.current_tok.matches(TT_KEYWORD, 'GET'):
			#print(self.current_tok)
			res.register_advancement()
			self.advance()
			#print(self.current_tok)
			if self.current_tok.type == TT_NEWLINE:
				#print("!``")
				return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				"Expected a Parent-Attribute"
				))
			#print(self.current_tok.type == TT_NEWLINE or self.current_tok.type == TT_EOF and self.key == [])
			self.key = []
			while self.current_tok.type != TT_EOF and self.current_tok.type != TT_NEWLINE:
				#print("!")
				if (self.current_tok.type == TT_NEWLINE or self.current_tok.type == TT_EOF) and self.key == []:
					#print("!")
					return res.failure(InvalidSyntaxError(
						self.current_tok.pos_start, self.current_tok.pos_end,
						"Expected an Attribute"
					))
		
		
				if self.current_tok.type == TT_IDENTIFIER or self.current_tok.type == TT_ATTR:
					#print(self.key)
					if self.key != [] and (self.key[-1] == TT_IDENTIFIER and self.current_tok.type != TT_ATTR):
						return res.failure(InvalidSyntaxError(
								self.current_tok.pos_start, self.current_tok.pos_end,
								"Expected a '.' Attribute Token in-between sub-attributes!"
							))
					elif self.key != [] and (self.key[-1] == TT_ATTR and self.current_tok.type != TT_ATTR):
						return res.failure(InvalidSyntaxError(
								self.current_tok.pos_start, self.current_tok.pos_end,
								"Expected a '.' Attribute Token in-between sub-attributes!"
							))
					else:
						self.key.append(self.current_tok)
					res.register_advancement()
					self.advance()
				else:
					res.register_advancement()
					self.advance()
					
			if  self.key == []:
				return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				"Expected a Attribute"
			))

			#print(self.key)
			
			try:
				attr = self.key.pop(-1)
			except:
				return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				"Expected a Attribute after Parent"
			))
			parent = self.key

			return res.success(GetNode(parent, attr,  self.current_tok.pos_start, self.current_tok.pos_start.copy()))

		node = res.register(self.bin_op(
			self.com_expr, ((TT_KEYWORD, "with"), (TT_KEYWORD, "or"))))

		if res.error: return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				"Expected 'val', 'const', 'SET', 'GET', 'if', 'for', 'while', 'func', 'goto', int, float, identifier, '+', '-', '(', '[' or 'inver'"
			))

		return res.success(node)

	###################################

	def bin_op(self, func_a, ops, func_b=None):
		if func_b == None:
			func_b = func_a

		res = ParseResult()
		left = res.register(func_a())
		if res.error: return res

		while self.current_tok.type in ops or (self.current_tok.type, self.current_tok.value) in ops:
			op_tok = self.current_tok
			res.register_advancement()
			self.advance()
			right = res.register(func_b())
			if res.error: return res
			left = BinOpNode(left, op_tok, right)

		return res.success(left)
