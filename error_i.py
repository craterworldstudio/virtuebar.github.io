from position_i import *
from string_with_arrows import *

###########################################
# ERRORS
###########################################

class Error:
	def __init__(self, pos_start, pos_end, error_name, details, ctx = None):
		self.error_name = error_name
		self.details = details
		self.pos_start = pos_start
		self.pos_end = pos_end
		self.fn_name = (pos_start.fn if ctx == None else ctx.display_name)

	def as_string(self):
		result = f'{self.error_name}: {self.details}'
		result += f'\nFile {self.fn_name}, line {self.pos_start.ln + 1}'
		result += '\n \n ' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
		return result

class IllegalCharError(Error):

	def __init__(self, pos_start, pos_end, details):
		super().__init__(pos_start, pos_end, 'Illegal Character', details)

class DefinedTypeError(Error):

	def __init__(self, pos_start, pos_end, details):
		super().__init__(pos_start, pos_end, 'Type Error', details)

class InvalidSyntaxError(Error):

	def __init__(self, pos_start, pos_end, details=''):
		super().__init__(pos_start, pos_end, 'Invalid Syntax', details)

class ExpectedCharError(Error):

	def __init__(self, pos_start, pos_end, details):
		super().__init__(pos_start, pos_end, 'Exprected Character', details)

class RunTimeError(Error):

	def __init__(self, pos_start, pos_end, details, context):
		self.context = context
		#print(self.context.display_name)
		super().__init__(pos_start, pos_end, 'Runtime Error', details, self.context)

	def as_string(self):
		result  = self.generate_traceback()
		result += f'{self.error_name}: {self.details}'
		result += '\n\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
		return result

	def generate_traceback(self):
		result = ''
		pos = self.pos_start
		ctx = self.context

		while ctx:
			result = f'  File {ctx.display_name}, line {str(pos.ln + 1)}, in {ctx.display_name}\n' + result
			pos = ctx.parent_entry_pos
			ctx = ctx.parent


		return 'Latest Call Traceback:\n' + result

class IncorrectValueTypeError(Error):

	def __init__(self, pos_start, pos_end, details=''):
		super().__init__(pos_start, pos_end, 'Incorrect ValueType Error', details)

class DevelopmentModeAccessError(Error):
	def __init__(self, pos_start, pos_end, details=''):
		super().__init__(pos_start, pos_end, 'Development Mode Error', details)

class DataFileNotFoundError(Error):
	def __init__(self, pos_start, pos_end, details):
		super().__init__(pos_start, pos_end, 'Data File Not Found', details)

class PrivilagedAccessError(Error):
	def __init__(self, pos_start, pos_end, details):
		super().__init__(pos_start, pos_end, 'Invalid Privilage Error', details)

class IncorrectValueAccessError(Error):
	def __init__(self, pos_start, pos_end, details):
		super().__init__(pos_start, pos_end, 'Incorrect Value Access Error', details)
