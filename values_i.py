###########################################
# VALUES
###########################################

import math
from runtime_result_i import *
from Interpreter_i import *
from context_i import *
from symbol_table_i import *
import os
from error_i import *
import random
from importer import Manager

class Runtime:
	developement_mode = True
	cwd = os.getcwd()

class Value:
	def __init__(self):
		self.set_pos()
		self.set_context()

	def set_pos(self, pos_start=None, pos_end=None):
		self.pos_start = pos_start
		self.pos_end = pos_end
		return self

	def set_context(self, context=None):
		self.context = context
		return self

	def added_to(self, other):
		return None, self.illegal_operation(other)

	def subbed_by(self, other):
		return None, self.illegal_operation(other)

	def multed_by(self, other):
		return None, self.illegal_operation(other)

	def dived_by(self, other):
		return None, self.illegal_operation(other)

	def powed_by(self, other):
		return None, self.illegal_operation(other)

	def get_comparison_eq(self, other):
		return None, self.illegal_operation(other)

	def get_comparison_ne(self, other):
		return None, self.illegal_operation(other)

	def get_comparison_lt(self, other):
		return None, self.illegal_operation(other)

	def get_comparison_gt(self, other):
		return None, self.illegal_operation(other)

	def get_comparison_lte(self, other):
		return None, self.illegal_operation(other)

	def get_comparison_gte(self, other):
		return None, self.illegal_operation(other)

	def withed_by(self, other):
		return None, self.illegal_operation(other)

	def ored_by(self, other):
		return None, self.illegal_operation(other)

	def inverted(self, other):
		return None, self.illegal_operation(other)

	def execute(self, args, no_value):
		return RTResult().failure(self.illegal_operation())
	
	def load(self, libs):
		return RTResult().failure(self.illegal_operation())

	def copy(self):
		raise Exception('No copy method defined')

	def is_true(self):
		return False

	def illegal_operation(self, other=None):
		if not other: other = self
		return RunTimeError(
			self.pos_start, other.pos_end,
			'Illegal operation',
			self.context
		)

class Number(Value):
	def __init__(self, value):
		super().__init__()
		self.value = value

	def added_to(self, other):
		if isinstance(other, Number):
			return Number(self.value + other.value).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def subbed_by(self, other):
		if isinstance(other, Number):
			return Number(self.value - other.value).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def multed_by(self, other):
		if isinstance(other, Number):
			return Number(self.value * other.value).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def dived_by(self, other):
		if isinstance(other, Number):
			if other.value == 0:
				return None, RunTimeError(
					other.pos_start, other.pos_end,
					'Division by zero',
					self.context
				)

			return Number(self.value / other.value).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def powed_by(self, other):
		if isinstance(other, Number):
			return Number(self.value ** other.value).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def get_comparison_eq(self, other):
		if isinstance(other, Number):
			return Number(int(self.value == other.value)).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def get_comparison_ne(self, other):
		if isinstance(other, Number):
			return Number(int(self.value != other.value)).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def get_comparison_lt(self, other):
		if isinstance(other, Number):
			return Number(int(self.value < other.value)).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def get_comparison_gt(self, other):
		if isinstance(other, Number):
			return Number(int(self.value > other.value)).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def get_comparison_lte(self, other):
		if isinstance(other, Number):
			return Number(int(self.value <= other.value)).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def get_comparison_gte(self, other):
		if isinstance(other, Number):
			return Number(int(self.value >= other.value)).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def withed_by(self, other):
		if isinstance(other, Number):
			return Number(int(self.value and other.value)).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def ored_by(self, other):
		if isinstance(other, Number):
			return Number(int(self.value or other.value)).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def inverted(self):
		return Number(1 if self.value == 0 else 0).set_context(self.context), None

	def copy(self):
		copy = Number(self.value)
		copy.set_pos(self.pos_start, self.pos_end)
		copy.set_context(self.context)
		return copy
	
	def get_value(self):
		return self.value

	def is_true(self):
		return self.value != 0

	def __str__(self):
		return str(self.value)

	def __repr__(self):
		return str(self.value)

class List(Value):
	'''List Value Type'''
	def __init__(self, elements):
		super().__init__()
		self.elements = elements

	def added_to(self, other):
		new_list = self.copy()
		new_list.elements.append(other)
		return new_list, None

	def subbed_by(self, other):
		if isinstance(other, Number):
			new_list = self.copy()
			try:
				new_list.elements.pop(other.value)
				return new_list, None
			except:
				return None, RunTimeError(
				other.pos_start, other.pos_end,
				'Element at this index could not be removed from list because index is out of bounds',
				self.context
				)
		else:
			return None, Value.illegal_operation(self, other)

	def multed_by(self, other):
		if isinstance(other, List):
			new_list = self.copy()
			new_list.elements.extend(other.elements)
			return new_list, None
		else:
			return None, Value.illegal_operation(self, other)

	def get_item(self, other):
		if isinstance(other, Number):
			try:
				return self.elements[other.value], None
			except:
				return None, RunTimeError(
				other.pos_start, other.pos_end,
				'Element at this index could not be retrieved from list because index is out of bounds',
				self.context
			)
		else:
			return None, Value.illegal_operation(self, other)
  
	def copy(self):
		copy = List(self.elements)
		copy.set_pos(self.pos_start, self.pos_end)
		copy.set_context(self.context)
		return copy

	def __str__(self):
		return f'[{", ".join([str(x) for x in self.elements])}]'
	
	def __repr__(self):
		return f'[{", ".join([repr(x) for x in self.elements])}]'

class BaseFunction(Value):
	'''Base Function Value Type'''
	def __init__(self, name):
		super().__init__()
		self.name = name or "<anonymous>"

	def generate_new_context(self):
		new_context = Context(self.name, self.context, self.pos_start)
		new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)
		return new_context

	def check_args(self, arg_names, args):
		res = RTResult()

		if len(args) > len(arg_names):
			return res.failure(RunTimeError(
			self.pos_start, self.pos_end,
		f"{len(args) - len(arg_names)} too many args passed into {self}",
		self.context
	  	))
	
		if len(args) < len(arg_names):
			return res.failure(RunTimeError(
			self.pos_start, self.pos_end,
			f"{len(arg_names) - len(args)} too few args passed into {self}",self.context ))

		return res.success(None)

	def populate_args(self, arg_names, args, exec_ctx):
		for i in range(len(args)):
			arg_name = arg_names[i]
			arg_value = args[i]
			arg_value.set_context(exec_ctx)
			exec_ctx.symbol_table.set(arg_name, arg_value)

	def check_and_populate_args(self, arg_names, args, exec_ctx):
		res = RTResult()
		res.register(self.check_args(arg_names, args))
		if res.should_return(): return res
		self.populate_args(arg_names, args, exec_ctx)
		return res.success(None)

class Function(BaseFunction):
	'''Function Value Type'''
	def __init__(self, name, body_node, arg_names, auto_return):
		super().__init__(name)
		self.body_node = body_node
		self.arg_names = arg_names
		self.auto_return = auto_return

	def execute(self, args, Interpreter):
		res = RTResult()
		interpreter = Interpreter()
		exec_ctx = self.generate_new_context()

		res.register(self.check_and_populate_args(self.arg_names, args, exec_ctx))
		if res.should_return(): return res

		value = res.register(interpreter.visit(self.body_node, exec_ctx))
		if res.should_return() and res.func_value_return == None: return res

		return_value = (value if self.auto_return else None) or res.func_value_return or Number.null
		return res.success(return_value)

	def copy(self):
		copy = Function(self.name, self.body_node, self.arg_names, self.auto_return)
		copy.set_context(self.context)
		copy.set_pos(self.pos_start, self.pos_end)
		return copy

	def __repr__(self):
		return f"<function {self.name}>"

class File_IO(Value):
	
	def __init__(self, file:None, fileName) -> None:
		super().__init__()
		self.file = file
		self.OpenfileName = fileName
		self.fileAlreadyOpened = False
		self.openModeType = None
		self.permissions = []
		self.set_pos()
		self.set_context()
		self.setDefinedAttr()

	def get_attr(self, func, args=[]):
		return self.func(args)

	def setDefinedAttr(self, permissions=None, file=None, filename=None, mode=None, fileAlreadyOpened=False):
		self.permissions = permissions if permissions is not None else []
		self.file = file if file is not None else None
		self.OpenfileName = filename
		self.openModeType = mode if mode is not None else  None
		self.fileAlreadyOpened = fileAlreadyOpened
		return self

	def set_pos(self, pos_start=None, pos_end=None):
		self.pos_start = pos_start
		self.pos_end = pos_end
		return self

	def set_context(self, context=None):
		self.context = context
		return self

	def OpenFile(self, fileio, path, mode):
		fileio.OpenfileName = path
		fileio.fileAlreadyOpened = True
		fileio.openModeType = mode
		
		#print(fileio.permissions)

		file = open(path, mode)
		fileio.file = file
		return file
	
	def modeDetermination(self,  mode):
		mode = str(mode).lower()

		if mode == 'r':
			self.permissions.append('read')
		if mode == 'w':
			self.permissions.append('write')
		if mode == 'a':
			self.permissions.append('append')
		if mode == 'c':
			self.permissions.append('create')
		if mode == 'x':
			self.permissions.append('destroy')
	
	def ReadFile(self, FiIO, file):
		#print(FiIO.permissions)
		if 'read' in FiIO.permissions:
			data = file.read()
			error = None
		else:
			data = None
			error = (PrivilagedAccessError(
				self.pos_start, self.pos_end,
				"Selected File doesn't have read privilages."
			))
		return data, error

	def WriteFile(self, FiIO, file, text):
		#print(FiIO.permissions)
		if 'write' in FiIO.permissions:
			file.write(text.value)
			data = True
			error = None
		else:
			data = False
			error = (PrivilagedAccessError(
				self.pos_start, self.pos_end,
				"Selected File doesn't have write privilages."
			))
		return data, error
	
	def isExist(self, path):
		status = os.path.isfile(path)
		#print(status)

	def copy(self):
		copy = File_IO(self.file, self.OpenfileName)
		copy.set_context(self.context)
		copy.set_pos(self.pos_start, self.pos_end)
		copy.setDefinedAttr(self.permissions, self.file)

		return copy

	def __repr__(self):
		return f"<FileObject File.{self.file}>"

class String(Value):
	def __init__(self, value):
		super().__init__()
		self.value = value

	def added_to(self, other):
		if isinstance(other, String):
			return String(self.value + other.value).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def multed_by(self, other):
		if isinstance(other, Number):
			return String(self.value * other.value).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def is_true(self):
		return len(self.value) > 0

	def len_str(self):
		return len(self.value)

	def copy(self):
		copy = String(self.value)
		copy.set_pos(self.pos_start, self.pos_end)
		copy.set_context(self.context)
		return copy

	def __str__(self):
		return f'"{self.value}"'

	def __repr__(self):
		return f'{self.value}'

###################################################################################
# GLOBAL CONSTANTS
###################################################################################
Number.null = String("null")
Number.none = String(None)
Number.false = Number(0)
Number.true = Number(1)
Number.math_PI = Number(math.pi)
###################################################################################s

class BuiltInFunction(BaseFunction):
	def __init__(self, name=None):
		super().__init__(name)
		self.manager = Manager()
		self.manager.setInterpreterLibPath()

	def execute(self, args, no_value):
		res = RTResult()
		exec_ctx = self.generate_new_context()

		method_name = f'execute_{self.name}'
		method = getattr(self, method_name, self.no_visit_method)

		res.register(self.check_and_populate_args(method.arg_names, args, exec_ctx))
		if res.should_return(): return res

		return_value = res.register(method(exec_ctx))
		if res.should_return(): return res
		return res.success(return_value)
	
	def load(self, libs):
		res = RTResult()
		self.libs_to_be_imported =  libs
		print(self, libs)
		raw_list = []
		for lib in self.libs_to_be_imported:
			raw_list.append(lib.value)

		self.manager.register_libraries(raw_list)
		return res.success(Number.none)

	def no_visit_method(self, node, context):
		raise Exception(f'No execute_{self.name} method defined')

	def copy(self):
		copy = BuiltInFunction(self.name)
		copy.set_context(self.context)
		copy.set_pos(self.pos_start, self.pos_end)
		return copy

	def __repr__(self):
		return f"<built-in function {self.name}>"

	#################################################################################################

#region ############################### I/O SYSTEM ###############################
	def execute_printout(self, exec_ctx):
		print(str(exec_ctx.symbol_table.get('value')))
		return RTResult().success(Number.none)
	execute_printout.arg_names = ["value"]

	def execute_printreturn(self, exec_ctx):
		statement = String(str(exec_ctx.symbol_table.get('value')))
		return RTResult().success(statement)
	execute_printreturn.arg_names = ["value"]

	def execute_typein(self, exec_ctx):
		text = input()
		return RTResult().success(String(text))
	execute_typein.arg_names = []

	def execute_typein_int(self, exec_ctx):
		while True:
			text = input()
			try:
				number = int(text)
				break
			except ValueError:
				print(f"'{text}' must be an integer. Try again!")
		return RTResult().success(Number(number))
	execute_typein_int.arg_names = []

	def execute_multi_typein(self, exec_ctx):
		NumberOfInputs = exec_ctx.symbol_table.get('Number')

		if not isinstance(NumberOfInputs, Number):
			return RTResult().failure(RunTimeError(
				self.pos_start, self.pos_end,
				"Argument must be number",
				exec_ctx
			))
		
		NumberOfInputs = NumberOfInputs.value
		inputs = []

		for i in range(0, NumberOfInputs):
			a = input()
			inputs.append(a)
		
		return RTResult().success(List(inputs))
	execute_multi_typein.arg_names = ['Number']

#endregion

#region ############################## Verification Commands #############################

	def execute_clear(self, exec_ctx):
		os.system('cls' if os.name == 'nt' else 'clear')
		return RTResult().success(Number.none)
	execute_clear.arg_names = []

	def execute_is_number(self, exec_ctx):
		is_number = isinstance(exec_ctx.symbol_table.get("value"), Number)
		return RTResult().success(Number.true if is_number else Number.false)
	execute_is_number.arg_names = ['value']
		
	def execute_is_string(self, exec_ctx):
		is_string = isinstance(exec_ctx.symbol_table.get("value"), String)
		return RTResult().success(Number.true if is_string else Number.false)
	execute_is_string.arg_names = ['value']
		
	def execute_is_list(self, exec_ctx):
		is_list = isinstance(exec_ctx.symbol_table.get("value"), List)
		return RTResult().success(Number.true if is_list else Number.false)
	execute_is_list.arg_names = ['value']
		
	def execute_is_function(self, exec_ctx):
		is_function = isinstance(exec_ctx.symbol_table.get("value"), BaseFunction)
		return RTResult().success(Number.true if is_function else Number.false)
	execute_is_function.arg_names = ['value']

	def execute_clean(self, exec_ctx):
		item = exec_ctx.symbol_table.get("item")
		exec_ctx.symbol_table.remove(item)
		del item
		return RTResult().success(Number.none)
	execute_clean.arg_names = ['item']

#endregion

#region ############################### List Operations ###############################

	def execute_len(self, exec_ctx):
		value = exec_ctx.symbol_table.get("list")
		
		if not (isinstance(value, List) or isinstance(value, String)):
			return RTResult().failure(RunTimeError(
				self.pos_start, self.pos_end,
				"Argument must be a list or string",
				exec_ctx
			))
		if isinstance(value, List):
			return RTResult().success(Number(len(value.elements)))
		elif isinstance(value, String):
			return RTResult().success(Number(len(str(value))))
	execute_len.arg_names = ['list']

	def execute_append(self, exec_ctx):
		list_ = exec_ctx.symbol_table.get("list")
		value = exec_ctx.symbol_table.get("value")

		if not isinstance(list_, List):
			return RTResult().failure(RunTimeError(
				self.pos_start, self.pos_end,
				"First argument must be a list",
				exec_ctx
			))

		list_.elements.append(value)
		return RTResult().success(Number.none)
	execute_append.arg_names = ['list', 'value']

	def execute_pop(self, exec_ctx):
		list_ = exec_ctx.symbol_table.get("list")
		index = exec_ctx.symbol_table.get("index")

		if not isinstance(list_, List):
			return RTResult().failure(RunTimeError(
				self.pos_start, self.pos_end,
				"First argument must be list",
				exec_ctx
	  	))

		if not isinstance(index, Number):
			return RTResult().failure(RunTimeError(
				self.pos_start, self.pos_end,
				"Second argument must be number",
				exec_ctx
			))

		try:
			element = list_.elements.pop(index.value)
		except:
			return RTResult().failure(RunTimeError(
			self.pos_start, self.pos_end,
			'Element at this index could not be removed from list because index is out of bounds',
			exec_ctx
		))

		return RTResult().success(element)
	execute_pop.arg_names = ['list', 'index']

	def execute_extend(self, exec_ctx):
		listA = exec_ctx.symbol_table.get("listA")
		listB = exec_ctx.symbol_table.get("listB")

		if not isinstance(listA, List):
			return RTResult().failure(RunTimeError(
			self.pos_start, self.pos_end,
			"First argument must be list",
			exec_ctx
		))

		if not isinstance(listB, List):
			return RTResult().failure(RunTimeError(
			self.pos_start, self.pos_end,
			"Second argument must be list",
			exec_ctx
		))

		listA.elements.extend(listB.elements)
		return RTResult().success(Number.none)
	execute_extend.arg_names = ['listA', 'listB']

	def execute_map(self, exec_ctx):
		elements = exec_ctx.symbol_table.get("elements")
		func = exec_ctx.symbol_table.get("func")

		new_elements = []

		for i in range(0, len(elements)):
			new_elements.append(func(elements[i]))

		return RTResult().success(List(new_elements))
	execute_map.arg_names = ["elements", "func"]

	def execute_join(self, exec_ctx):
		elements = exec_ctx.symbol_table.get("elements")
		if i != len - 1: separator = exec_ctx.symbol_table.get("separator")

		result = ""
		length = len(elements)

		for i in range(0, length):
			result += elements[i]
			result += separator

		return RTResult().success(String(result))
	execute_join.arg_names = ["elements", "separator"]

	def execute_max(self, exec_ctx):
		Alist = exec_ctx.symbol_table.get("Alist")

		if not isinstance(Alist, List):
			return RTResult().failure(RunTimeError(
				self.pos_start, self.pos_end,
				"Argument must be list",
				exec_ctx
	  	))
		elements = []
		for i in Alist.elements:
			elements.append(int(i.get_value()))
		result = max(elements)

		return RTResult().success(Number(result))
	execute_max.arg_names = ["Alist"]

	def execute_min(self, exec_ctx):
		Alist = exec_ctx.symbol_table.get("Alist")

		if not isinstance(Alist, List):
			return RTResult().failure(RunTimeError(
				self.pos_start, self.pos_end,
				"Argument must be list",
				exec_ctx
	  	))
		elements = []
		for i in Alist.elements:
			elements.append(int(i.get_value()))
		result = min(elements)

		return RTResult().success(Number(result))
	execute_min.arg_names = ["Alist"]

#endregion

#region ############################### MATH FUNCTIONS ###############################

	def execute_floor(self, exec_ctx):
		num = exec_ctx.symbol_table.get("float")
		try:
			num = float(num.value)
		except:
			print(f'{num} cannot be floored. Try with a float or integer value.')
		
		num = math.floor(num)
		return RTResult().success(Number(num))
	execute_floor.arg_names = ['float']

	def execute_ceil(self, exec_ctx):
		num = exec_ctx.symbol_table.get("float")
		try:
			num = float(num.value)
		except:
			print(f'{num} cannot be ceiled. Try with a float or integer value.')
		
		num = math.ceil(num)
		return RTResult().success(Number(num))
	execute_ceil.arg_names = ['float']

	def execute_square(self, exec_ctx):
		value = exec_ctx.symbol_table.get("value")
		value = value.value
		try:
			number = int(value)
		except ValueError:
			try: 
				number = float(value)
			except:
				return RTResult(IncorrectValueTypeError(
					self.pos_start, self.pos_end,
					f"'{value}' must be an float or an integer. Try again!",
					exec_ctx
					))

		number = number ** 2
		return RTResult().success(Number(number))
	execute_square.arg_names = ['value']

	def execute_cube(self, exec_ctx):
		value = exec_ctx.symbol_table.get("value")
		value = value.value
		try:
			number = int(value)
		except ValueError:
			try: 
				number = float(value)
			except:
				return RTResult(IncorrectValueTypeError(
					self.pos_start, self.pos_end,
					f"'{value}' must be an float or an integer. Try again!",
					exec_ctx
					))

		number = number ** 3
		return RTResult().success(Number(number))
	execute_cube.arg_names = ['value']

	def execute_tessaract(self, exec_ctx):
		value = exec_ctx.symbol_table.get("value")
		value = value.value
		try:
			number = int(value)
		except ValueError:
			try: 
				number = float(value)
			except:
				return RTResult(IncorrectValueTypeError(
					self.pos_start, self.pos_end,
					f"'{value}' must be an float or an integer. Try again!"
					))

		number = number ** 4
		return RTResult().success(Number(number))
	execute_tessaract.arg_names = ['value']

	def execute_add(self, exec_ctx):
		numA = exec_ctx.symbol_table.get("NumberA")
		numb = exec_ctx.symbol_table.get("NumberB")
		numa = numA.value
		numb = numb.value

		result = numa + numb

		return RTResult().success(Number(result)) 
	execute_add.arg_names = ['NumberA', 'NumberB']

	def execute_subt(self, exec_ctx):
		numA = exec_ctx.symbol_table.get("NumberA")
		numb = exec_ctx.symbol_table.get("NumberB")
		numa = numA.value
		numb = numb.value

		result = numa - numb
		return RTResult().success(Number(result)) 
	execute_subt.arg_names = ['NumberA', 'NumberB']

	def execute_mult(self, exec_ctx):
		numA = exec_ctx.symbol_table.get("NumberA")
		numb = exec_ctx.symbol_table.get("NumberB")
		numa = numA.value
		numb = numb.value

		result = numa * numb
		return RTResult().success(Number(result)) 
	execute_mult.arg_names = ['NumberA', 'NumberB']

	def execute_divi(self, exec_ctx):
		numA = exec_ctx.symbol_table.get("NumberA")
		numb = exec_ctx.symbol_table.get("NumberB")
		numa = numA.value
		numb = numb.value

		result = numb / numa
		return RTResult().success(Number(result)) 
	execute_divi.arg_names = ['NumberA', 'NumberB']

	def execute_sqrt(self, exec_ctx):
		value = exec_ctx.symbol_table.get("value")
		value = value.value

		result = math.sqrt(value)

		return RTResult().success(Number(result))
	execute_sqrt.arg_names = ['value']

	def execute_cbrt(self, exec_ctx):
		value = exec_ctx.symbol_table.get("value")
		value = value.value

		result = math.cbrt(value)

		return RTResult().success(Number(result))
	execute_cbrt.arg_names = ['value']

	def execute_ranint(self, exec_ctx):
		maxint = int(exec_ctx.symbol_table.get("maxint"))
		minint = int(exec_ctx.symbol_table.get("minint"))

		result = random.randint(maxint, minint)
		return RTResult().success(Number(result))
	execute_ranint.arg_names = ['maxint', 'minint']

	def execute_range(self, exec_ctx):
		min_int = int(exec_ctx.symbol_table.get("min").value)
		max_int = int(exec_ctx.symbol_table.get("max").value)
		RangedNumbers = []
		for i in range(min_int, max_int):
			RangedNumbers.append(Number(i))
		return RTResult().success(List(RangedNumbers))
	execute_range.arg_names = ["min", "max"]
#endregion

#region ################################ String Manupulation #################################

	def execute_contatinate(self, exec_ctx):
		itema = str(exec_ctx.symbol_table.get("itema").value)
		itemb = str(exec_ctx.symbol_table.get("itemb").value)
		result = itema + itemb
		return RTResult().success(String(result))
	execute_contatinate.arg_names = ["itema", "itemb"]

	def execute_substring(self, exec_ctx):
		item = str(exec_ctx.symbol_table.get("item").value)
		if isinstance(exec_ctx.symbol_table.get("value"), String):
			return RTResult().failure(RunTimeError(
				self.pos_start, self.pos_end,
				"First Argument must be String",
				exec_ctx
			))

		try:
			startpos = int(exec_ctx.symbol_table.get("startpos").value)
		except:
			startpos = 0
		
		try:
			endpos = int(exec_ctx.symbol_table.get("endpos").value)
		except:
			endpos = -1

		try:
			step = int(exec_ctx.symbol_table.get("step").value)
		except:
			step = 1

		substring = item[startpos:endpos:step]
		return RTResult().success(String(substring))
	execute_substring.arg_names = ["item", "startpos", "endpos", "step"]

	def execute_replace(self, exec_ctx):
		item = str(exec_ctx.symbol_table.get("item").value)
		#print(type(exec_ctx.symbol_table.get("orgWord")))
		Orgword = str(exec_ctx.symbol_table.get("orgWord").value)
		ReplWord = str(exec_ctx.symbol_table.get("replWord").value)

		result = item.replace(Orgword, ReplWord)
		return RTResult().success(String(result))
	execute_replace.arg_names = ["item", "orgWord", "replWord"]

	def execute_lowercase(self, exec_ctx):
		item = str(exec_ctx.symbol_table.get("item").value)

		result = item.lower()
		return RTResult().success(String(result))
	execute_lowercase.arg_names = ['item']

	def execute_uppercase(self, exec_ctx):
		item = str(exec_ctx.symbol_table.get("item").value)

		result = item.upper()
		return RTResult().success(String(result))
	execute_uppercase.arg_names = ['item']

	def execute_split(self, exec_ctx):
		item = str(exec_ctx.symbol_table.get("item").value)
		sep = str(exec_ctx.symbol_table.get("separator").value)

		spliteditem = item.split(sep=sep)
		resultList = []

		for i in spliteditem:
			resultList.append(String(i))
		
		return RTResult().success(List(resultList))
	execute_split.arg_names = ["item", "separator"]

	
#endregion

#region File I/O
	def execute_open(self, exec_ctx):
		path = str(exec_ctx.symbol_table.get("path").value)
		mode = str(exec_ctx.symbol_table.get("mode").value)
		fPath = path[:-4]
		for i in range(0, 2):
			if fPath[2] == "\\":
				fName = fPath.split("\\")[-1]
			elif fPath[2] == "/":
				fName = fPath.split("/")[-1]
			else:
				fName = path
		
		fIO = File_IO(None,fName)

		file = fIO.OpenFile(fIO, path, mode)
		fIO.modeDetermination(mode)
		exec_ctx.symbol_table.set(fIO, fIO)
		fIO.file = file
		#print(path, fPath, fName, mode)
		return RTResult().success(fIO)
	execute_open.arg_names = ["path", "mode"]

 
	def execute_read(self, exec_ctx):
		fileio = exec_ctx.symbol_table.get("file")
		#print(fileio.fileAlreadyOpened)
		if not isinstance(fileio, File_IO) and fileio.fileAlreadyOpened:
			return RTResult().failure(RunTimeError(
				self.pos_start, self.pos_end,
				"First argument must be a file already opened file object",
				exec_ctx
			))
		#print(fileio.fileAlreadyOpened)
		try:
			data, error = fileio.ReadFile(fileio, fileio.file)
		except:
			file = exec_ctx.symbol_table.get("file")
			data, error = file.ReadFile(file, file.file)

		if data:
			data = data.split("\n")
			Filedata = []
			for i in data:
				Filedata.append(String(i))
			return RTResult().success(List(Filedata))
		elif error:
			return RTResult().failure(error)
	execute_read.arg_names = ["file"]
 
	def execute_write(self, exec_ctx):
		fileio = exec_ctx.symbol_table.get("file")
		text = exec_ctx.symbol_table.get("text")

		#print(fileio.fileAlreadyOpened)
		if not isinstance(fileio, File_IO) and fileio.fileAlreadyOpened:
			return RTResult().failure(RunTimeError(
				self.pos_start, self.pos_end,
				"First argument must be a file already opened file object",
				exec_ctx
			))
	
		try:
			data, error = fileio.WriteFile(fileio, fileio.file, text)
		except:
			file = exec_ctx.symbol_table.get("file")
			data, error = file.WriteFile(file, file.file, text)
   
		if error:
			return RTResult().failure(error)
   
		return RTResult().success(Number.none, True)
	execute_write.arg_names = ["file", "text"]
#endregion

#region ############################### Language Embeded Functions ###############################

	def execute_run(self, exec_ctx):
		fn = exec_ctx.symbol_table.get("fn")

		if not isinstance(fn, String):
			return RTResult().failure(RunTimeError(
				self.pos_start, self.pos_end,
				"Filename must be string data type!",
				exec_ctx
			))

		fn = str(os.path.basename(fn.value))
		#print(fn)
		if fn.endswith(".virh"):
			return RTResult().failure(RunTimeError(
			self.pos_start, self.pos_end,
			f"Cannot run Header files with run() function! \nUse addlib!\n",
			exec_ctx
			)) 
		try:
			with open(fn, "r") as file:
				script = file.read()
		except Exception as e:
			return RTResult().failure(RunTimeError(
				self.pos_start, self.pos_end,
				f"Failed to load script \"{fn}\"\n" + str(e),
				exec_ctx
			))

		from run_i import run
		_ , error = run(fn, script, path=True)
		
		if error: return RTResult().failure(RunTimeError(
			self.pos_start, self.pos_end,
			f"Failed to finish executing script \"{fn}\"\n" + 
			error.as_string(),
			exec_ctx
			))

		return RTResult().success(Number.none)
	execute_run.arg_names = ["fn"] # File name

	def execute_global_attributes(self, exec_ctx):
		Attributes = exec_ctx.symbol_table.getTable()
		AttrList = List([])
		for i in Attributes:
			for items in i.items():
				AttrList.elements.append(items)
		return RTResult().success(AttrList)
	execute_global_attributes.arg_names = []

	def execute_stay(self, exec_ctx):
		a = input("Press any key to continue....")
		return RTResult().success(Number.none)
	execute_stay.arg_names = []

	def execute_test(self, exec_ctx):
		if Runtime.developement_mode == True:
			print(File_IO.isExist(self.fIO,"G:\\Language\\Interpreter\\symbol_table_i.py"))
		else:
			return RTResult().failure(DevelopmentModeAccessError(
				self.pos_start, self.pos_end,
				f"This function is only available in development mode.\nDevelopmentMode: Inactive"
			))
		return RTResult().success(Number.none)
	execute_test.arg_names = []

	def execute_get_cwd(self, exec_ctx):
		cwd = Runtime.cwd
		return RTResult().success(String(cwd))
	execute_get_cwd.arg_names = []	

#endregion

############################### Assignments ###############################



BuiltInFunction.printout    	  = BuiltInFunction("printout")
BuiltInFunction.printreturn 	  = BuiltInFunction("printreturn")
BuiltInFunction.typein      	  = BuiltInFunction("typein")
BuiltInFunction.multi_typein	  = BuiltInFunction("multi_typein")
BuiltInFunction.typein_int  	  = BuiltInFunction("typein_int")
BuiltInFunction.clear       	  = BuiltInFunction("clear")
BuiltInFunction.is_number   	  = BuiltInFunction("is_number")
BuiltInFunction.is_string   	  = BuiltInFunction("is_string")
BuiltInFunction.is_list     	  = BuiltInFunction("is_list")
BuiltInFunction.is_function 	  = BuiltInFunction("is_function")
BuiltInFunction.append      	  = BuiltInFunction("append")
BuiltInFunction.pop         	  = BuiltInFunction("pop")
BuiltInFunction.extend      	  = BuiltInFunction("extend")
BuiltInFunction.max				  = BuiltInFunction("max")
BuiltInFunction.min				  = BuiltInFunction("min")
BuiltInFunction.contatinate 	  = BuiltInFunction("contatinate")
BuiltInFunction.substring 		  = BuiltInFunction("substring")
BuiltInFunction.replace 		  = BuiltInFunction("replace")
BuiltInFunction.uppercase		  = BuiltInFunction("uppercase")
BuiltInFunction.lowercase		  = BuiltInFunction("lowercase")
BuiltInFunction.split			  = BuiltInFunction("split")
BuiltInFunction.floor 			  = BuiltInFunction("floor")
BuiltInFunction.ceil      		  = BuiltInFunction("ceil")
BuiltInFunction.square  		  = BuiltInFunction("square")
BuiltInFunction.cube			  = BuiltInFunction("cube")
BuiltInFunction.tessaract		  = BuiltInFunction("tessaract")
BuiltInFunction.add 			  = BuiltInFunction("add")
BuiltInFunction.subt			  = BuiltInFunction("subt")
BuiltInFunction.mult			  = BuiltInFunction("mult")
BuiltInFunction.divi			  = BuiltInFunction("divi")
BuiltInFunction.sqrt			  = BuiltInFunction("sqrt")
BuiltInFunction.cbrt			  = BuiltInFunction("cbrt")
BuiltInFunction.ranint			  = BuiltInFunction("ranint")
BuiltInFunction.range       	  = BuiltInFunction("range")
BuiltInFunction.run 			  = BuiltInFunction("run")
BuiltInFunction.len 			  = BuiltInFunction("len")
BuiltInFunction.map				  = BuiltInFunction("map")
BuiltInFunction.join 			  = BuiltInFunction("join")
BuiltInFunction.open			  = BuiltInFunction("open")
BuiltInFunction.read 			  = BuiltInFunction("read")
BuiltInFunction.write 			  = BuiltInFunction("write")
BuiltInFunction.clean			  = BuiltInFunction("clean")
BuiltInFunction.stay			  = BuiltInFunction("stay")
BuiltInFunction.test			  = BuiltInFunction("test")
BuiltInFunction.global_attributes = BuiltInFunction("global_attributes")
BuiltInFunction.get_cwd			  = BuiltInFunction("get_cwd")
