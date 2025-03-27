from error_i import *
from runtime_result_i import *
from values_i import *

from token_i import *
from context_i import *
from values_i import String, Number, Function, Value, List, BuiltInFunction
from parser_i import Parser
import values_i

import os

###########################################
# Interpreter
###########################################


class Interpreter:
	def __init__(self, raw_Tokens=None, lineData=(0, [], []), global_symbol_table=None, bIF: BuiltInFunction = BuiltInFunction) -> None:
		#print(lineData)
		self.rawTokens = raw_Tokens
		self.line, self.TotalProg, self.untacted_indexes = lineData
		self.global_symbol_table = global_symbol_table
		self.cwd = os.getcwd()
		self.libs = []
		self.bIF = bIF()

		
	def visit(self, node, context):
		#print(2, node.element_nodes)
		method_name = f'visit_{type(node).__name__}'
		#print(method_name)
		method = getattr(self, method_name, self.no_visit_method)
		#print(method)
		return method(node, context)

	def no_visit_method(self, node, context):
		raise Exception(f'No visit_{type(node).__name__} method defined')

	################################################################

	def visit_NumberNode(self, node, context):
		return RTResult().success(
			Number(node.tok.value).set_context(
				context).set_pos(node.pos_start, node.pos_end)
		)

	def visit_ListNode(self, node, context):
		
		res = RTResult()
		elements = []

		for element_node in node.element_nodes:
			result = res.register(self.visit(element_node, context))
			try:
				#print(result.value, Number.none, type(result.value), type(Number.none))
				if result.value == None:
					continue
				else:
					#print("!!!")
					elements.append(result)
			except AttributeError:
				elements.append(result)
			if res.should_return(): return res

		return res.success(
	  		List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
			)

	def visit_VarAccessNode(self, node, context):
		res = RTResult()
		var_name = node.var_name_tok.value
		value = context.symbol_table.get(var_name)

		if not value:
			return res.failure(RunTimeError(
				node.pos_start, node.pos_end,
				f"'{var_name}' is not defined",
				context
			))

		if type(value).__name__ == 'list':
			var_value = value[0]
		else:
			var_value = value
		var_value = var_value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
		(f'{ var_value = }')
		returnNull = False
		if var_value == "null":
			returnNull = True
		return res.success(var_value, returnNull)

	def visit_VarAssignNode(self, node, context):
		res = RTResult()
		var_name = node.var_name_tok.value
		value = res.register(self.visit(node.value_node, context))
		Var_type = node._type

		if res.should_return(): return res
		if Var_type in ['val', 'const', 'ATTR']:
			if Var_type == 'const':
				if var_name in context.symbol_table.symbols.keys():
					var_value = context.symbol_table.get(var_name)
					var_type = var_value[1]
					return res.failure(DefinedTypeError(
						node.pos_start, node.pos_end,
						f"'{var_name}' is already as {var_type}!"
					))
				context.symbol_table.set(var_name, [value, Var_type])
				return res.success(Number.none)
			
			if Var_type == 'ATTR':
				return res.failure(IncorrectValueAccessError(
					node.pos_start, node.pos_end,
					f"'{var_name}' of Type {var_type} cannot be set with the syntax! Use 'SET'"
				))
			else:
				context.symbol_table.set(var_name, [value, Var_type])
			return res.success(Number.none)

	def visit_GoToNode(self, node, context):
		res = RTResult()

		lineno = res.register(self.visit(node.line, context))
		if res.should_return(): return res

		INTlineno = lineno.get_value()

		def get_rest_of_Prog(idx):
			#print("INDEX LISTS ", self.untacted_indexes)
			EOF_idx = self.untacted_indexes[-1]
			Ln = len(self.untacted_indexes) - 1
			if idx <= 0 or idx > len(self.rawTokens):
				return []  # Invalid index, return an empty list
    
			ProgList = self.TotalProg[idx - 1:]
			FinalProgList = []

			idx_count = 0

			for line in ProgList:
				for token in line:
					FinalProgList.append(token)
				FinalProgList.append(Token(TT_NEWLINE, pos_start=self.untacted_indexes[0]))
				idx_count += 1
			FinalProgList.append(Token(TT_EOF, pos_start=EOF_idx))

			#print(FinalProgList)
			return FinalProgList

		
		restOfTheProg = get_rest_of_Prog(INTlineno)

		#print("REST OF THE PROGRAM ",restOfTheProg)

		# Generate Abstract Syntax Tree
		parser = Parser(restOfTheProg)
		ast = parser.parse()
		#print(ast.node)
			
		if ast.error: return None, ast.error

		#Run program
		interpreter = Interpreter((self.line, self.TotalProg))                                                                                          
		context = Context(context.display_name)
		context.symbol_table = self.global_symbol_table
		result = interpreter.visit(ast.node, context)

		#print(dir(result))

		try:

			if type(result.value) == values_i.List:
				#print(result, result.value, result.value.elements)
				#print(type(result.value.elements), result.value.elements)
				for i in result.value.elements:
					#print(i, 1)
					if str(i) == "null":
						a = [1, 2]
						#print(1, i, type(i))
						ind = result.value.elements.index(i)
						#print(ind)
						del result.value.elements[ind]

		except:
			pass

		return res.success(Number.none)
		
	def visit_BinOpNode(self, node, context):
		res = RTResult()
		left = res.register(self.visit(node.left_node, context))
		if res.should_return(): return res
		right = res.register(self.visit(node.right_node, context))
		if res.should_return(): return res

		if node.op_tok.type == TT_PLUS:
			result, error = left.added_to(right)
		elif node.op_tok.type == TT_MINUS:
			result, error = left.subbed_by(right)
		elif node.op_tok.type == TT_MUL:
			result, error = left.multed_by(right)
		elif node.op_tok.type == TT_DIV:
			result, error = left.dived_by(right)
		elif node.op_tok.type == TT_POWER:
			result, error = left.powed_by(right)
		elif node.op_tok.type == TT_EE:
			result, error = left.get_comparison_eq(right)
		elif node.op_tok.type == TT_NE:
			result, error = left.get_comparison_ne(right)
		elif node.op_tok.type == TT_LT:
			result, error = left.get_comparison_lt(right)
		elif node.op_tok.type == TT_GT:
			result, error = left.get_comparison_gt(right)
		elif node.op_tok.type == TT_LTE:
			result, error = left.get_comparison_lte(right)
		elif node.op_tok.type == TT_GTE:
			result, error = left.get_comparison_gte(right)
		
		# To Get an Element from List
		elif node.op_tok.type == TT_COLON:
			result, error = left.get_item(right)

		#elif node.op_tok.type == TT_ATTR:
		#	result, error = left.get_attr(right)

		elif node.op_tok.matches(TT_KEYWORD, 'with'):
			result, error = left.withed_by(right)
		elif node.op_tok.matches(TT_KEYWORD, 'or'):
			result, error = left.ored_by(right)

		if error:
			return res.failure(error)
		else:
			return res.success(result.set_pos(node.pos_start, node.pos_end))

	def visit_UnaryOpNode(self, node, context):
		res = RTResult()
		number = res.register(self.visit(node.node, context))
		if res.should_return(): return res

		error = None

		if node.op_tok.type == TT_MINUS:
			number, error = number.multed_by(Number(-1))

		elif node.op_tok.matches(TT_KEYWORD, 'inver'): number, error = number.inverted()

		if error: return res.failure(error)
		else: return res.success(number.set_pos(node.pos_start, node.pos_end))

	def visit_IfNode(self, node, context):
		res = RTResult()

		for condition, expr, return_null in node.cases:
			condition_value = res.register(self.visit(condition, context))
			if res.should_return(): return res

			if condition_value.is_true():
				expr_value = res.register(self.visit(expr, context))
				if res.should_return(): return res
				return res.success(Number.none if return_null else expr_value)

		if node.else_case:
			else_value = res.register(self.visit(node.else_case, context))
			if res.should_return(): return res
			return res.success(Number.none if return_null else else_value)

		return res.success(Number.none)

	def visit_ForNode(self, node, context):
		res = RTResult()
		elements = []

		start_value = res.register(self.visit(node.start_value_node, context))
		if res.should_return(): return res

		end_value = res.register(self.visit(node.end_value_node, context))
		if res.should_return(): return res

		if node.step_value_node:
			step_value = res.register(
				self.visit(node.step_value_node, context))
			if res.should_return(): return res
		else:
			step_value = Number(1)

		i = start_value.value

		if step_value.value >= 0:
			def condition(): return i < end_value.value
		else:
			def condition(): return i > end_value.value

		while condition():
			context.symbol_table.set(node.var_name_tok.value, Number(i))
			i += step_value.value

			value = res.register(self.visit(node.body_node, context))
			if res.should_return() and res.loop_skip == False and res.loop_break == False: return res

			if res.loop_skip:
				continue

			if res.loop_break: 
				break

			elements.append(value)

		return res.success(
			Number.none if node.return_null else
			List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
		)

	def visit_WhileNode(self, node, context):
		res = RTResult()
		elements = []

		while True:
			condition = res.register(self.visit(node.condition_node, context))
			if res.should_return(): return res

			if not condition.is_true():
				break

			value = res.register(self.visit(node.body_node, context))
			if res.should_return() and res.loop_skip == False and res.loop_break == False: return res

			if res.loop_skip:
				continue

			if res.loop_break: 
				break

			elements.append(value)

		return res.success(
			Number.none if node.return_null else
			List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
		)

	def visit_FuncDefNode(self, node, context):
		res = RTResult()

		func_name = node.var_name_tok.value if node.var_name_tok else None
		body_node = node.body_node
		arg_names = [arg_name.value for arg_name in node.arg_name_toks]
		func_value = Function(func_name, body_node, arg_names, node.auto_return).set_context(
			context).set_pos(node.pos_start, node.pos_end)

		if node.var_name_tok:
			context.symbol_table.set(func_name, [func_value, 'func'])

		return res.success(func_value)

	def visit_CallNode(self, node, context):
		res = RTResult()
		args = []

		value_to_call = res.register(self.visit(node.node_to_call, context))
		if res.should_return(): return res
		value_to_call = value_to_call.copy().set_pos(node.pos_start, node.pos_end)

		for arg_node in node.arg_nodes:
			args.append(res.register(self.visit(arg_node, context)))
			if res.should_return(): return res

		return_value = res.register(value_to_call.execute(args, Interpreter))
		if res.should_return(): return res
		return_value = return_value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
		return res.success(return_value)

	def visit_StringNode(self, node, context):
		return RTResult().success(
			String(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end)
		)
	
	def visit_CWDNode(self, node, context):
		res = RTResult()

		self.cwd = res.register(self.visit(node.directory_path, context)) # or node.directory_path.tok.value
		values_i.Runtime.cwd = self.cwd
		#print(self.cwd)

		return res.success(Number.none)
			
	def visit_AddLibNode(self, node, context):
		res = RTResult()

		filename = res.register(self.visit(node.file_name, context)) # or node.file_name.tok.value

		if node.is_abs == False:
			full_path = f"{self.cwd.value}\\{filename.value}.virh"
		elif node.is_abs == True:
			full_path = filename

		fn = String(full_path).value

		#print(fn)

		try:
			with open(fn, "r") as file:
				script = file.read()
		except Exception as e:
			return res.failure(RunTimeError(
				node.pos_start, node.pos_end,
				f"Failed to load header \"{fn}\"\n" + str(e),
				context
			))

		from run_i import run
		_ , error = run(fn, script, True, True)
		
		if error: return RTResult().failure(RunTimeError(
			node.pos_start, node.pos_end,
			f"Failed to finish executing script \"{fn}\"\n" + 
			error.as_string(),
			context
			))
		
		return res.success(Number.none)
	
	def visit_STDLibNode(self, node, context):
		res = RTResult()
		libname = res.register(self.visit(node.lib_name, context))

		self.libs.append(libname)
		print(self.bIF)
		#return_value = res.register(BuiltInFunction.)
		self.bIF.load(self.libs)

		return res.success(Number.none)



	def visit_SetNode(self, node, context):
		res = RTResult()

		parent = node.parent_type
		attr = node.Attr.value
		value = res.register(self.visit(node.value, context))

		if res.should_return(): return res

		#print(parent, attr, type(parent), type(attr))

		result = ''.join(map(lambda item: str(item.value), parent)) + '.' + str(attr)
		#print(result)
		context.symbol_table.set(String(result).value, [value, 'ATTR'])

		return res.success(value)

	def visit_GetNode(self, node, context):
		res = RTResult()
		parent = node.parent_type
		attr = node.Attr.value

		result = String(''.join(map(lambda item: str(item.value), parent)) + '.' + str(attr))
		#print(result, result.value)
		value = context.symbol_table.get(result.value)

		if not value:
			return res.failure(RunTimeError(
				node.pos_start, node.pos_end,
				f"'{result}' is not defined",
				context
			))

		if type(value).__name__ == 'list':
			var_value = value[0]
		else:
			var_value = value
		var_value = var_value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
		(f'{ var_value = }')
		returnNull = False
		if var_value == "null":
			returnNull = True
		return res.success(var_value, returnNull)

	def visit_ReturnNode(self, node, context):
		res = RTResult()

		if node.node_to_return:
			value = res.register(self.visit(node.node_to_return, context))
			if res.should_return(): return res
		else:
			value = Number.null
		
		return res.success_return(value)

	def visit_SkipNode(self, node, context):
		return RTResult().success_skip()

	def visit_BreakNode(self, node, context):
		return RTResult().success_break()