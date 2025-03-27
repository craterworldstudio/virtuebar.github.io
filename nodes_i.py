###########################################
# NODES
###########################################

class NumberNode: # Float / Integer None
	def __init__(self, tok, _type=None):
		self.tok = tok
		self._type = _type

		self.pos_start = self.tok.pos_start
		self.pos_end = self.tok.pos_end

	def __repr__(self):
		return f'{self.tok}'

class ListNode:
	def __init__(self, element_nodes, pos_start, pos_end, _type = None):
		self.element_nodes = element_nodes
		self._type = _type

		self.pos_start = pos_start
		self.pos_end = pos_end

class StringNode:
	def __init__(self, tok, _type=None):
		self.tok = tok
		self._type = _type

		self.pos_start = self.tok.pos_start
		self.pos_end = self.tok.pos_end

	def __repr__(self):
		return f'{self.tok}'

class VarAccessNode:
	def __init__(self, var_name_tok, _type=None):
		self.var_name_tok = var_name_tok
		self._type = _type

		self.pos_start = self.var_name_tok.pos_start
		self.pos_end = self.var_name_tok.pos_end

class GoToNode:
	def __init__(self, line, pos_start, pos_end,_type=None) -> None:
		self.line = line
		
		self._type = _type
		self.pos_start = pos_start
		self.pos_end = pos_end

class VarAssignNode:
	def __init__(self, var_name_tok, value_node, _type):
		self.var_name_tok = var_name_tok
		self.value_node = value_node
		self._type = _type

		self.pos_start = self.var_name_tok.pos_start
		self.pos_end = self.value_node.pos_end

class BinOpNode: # Binary Operator None
	def __init__(self, left_node, op_tok, right_node, _type=None):
		self.left_node = left_node
		self.op_tok = op_tok
		self.right_node = right_node
		self._type = _type

		self.pos_start = self.left_node.pos_start
		self.pos_end = self.right_node.pos_end

	def __repr__(self):
		return f'({self.left_node}, {self.op_tok}, {self.right_node})'

class UnaryOpNode:
	def __init__(self, op_tok, node, _type=None):
		self.op_tok = op_tok
		self.node = node
		self._type = _type

		self.pos_start = self.op_tok.pos_start
		self.pos_end = self.node.pos_end

	def __repr__(self):
		return f'({self.op_tok}, {self.node})'

class IfNode:
	def __init__(self, cases, else_case, _type=None) -> None:
		self.cases = cases
		self.else_case = else_case
		self._type = _type

		self.pos_start = self.cases[0][0].pos_start
		self.pos_end = (self.else_case or self.cases[len(self.cases) - 1])[0].pos_end

class ForNode:
	def __init__(self, var_name_tok, start_value_node, end_value_node, step_value_node, body_node, return_null, _type = None):
		self.var_name_tok = var_name_tok
		self.start_value_node = start_value_node
		self.end_value_node = end_value_node
		self.step_value_node = step_value_node
		self.body_node = body_node
		self.return_null = return_null
		self._type = _type

		self.pos_start = self.var_name_tok.pos_start
		self.pos_end = self.body_node.pos_end

class WhileNode:
	def __init__(self, condition_node, body_node, return_null, _type=None):
		self.condition_node = condition_node
		self.body_node = body_node
		self.return_null = return_null
		self._type = _type

		self.pos_start = self.condition_node.pos_start
		self.pos_end = self.body_node.pos_end

class FuncDefNode:
	def __init__(self, var_name_tok, arg_name_toks, body_node, auto_return, _type=None):
		self.var_name_tok = var_name_tok
		self.arg_name_toks = arg_name_toks
		self.body_node = body_node
		self.auto_return = auto_return
		self._type = _type

		if self.var_name_tok:
			self.pos_start = self.var_name_tok.pos_start
		elif len(self.arg_name_toks) > 0:
			self.pos_start = self.arg_name_toks[0].pos_start
		else:
			self.pos_start = self.body_node.pos_start

		self.pos_end = self.body_node.pos_end

class CallNode:
	def __init__(self, node_to_call, arg_nodes, _type=None):
		self._type = _type
		self.node_to_call = node_to_call
		self.arg_nodes = arg_nodes

		self.pos_start = self.node_to_call.pos_start

		if len(self.arg_nodes) > 0:
			self.pos_end = self.arg_nodes[len(self.arg_nodes) - 1].pos_end
		else:
			self.pos_end = self.node_to_call.pos_end

class ReturnNode:
	def __init__(self, node_to_return, pos_start, pos_end, _type=None) -> None:
		self.node_to_return = node_to_return
		self.pos_start = pos_start
		self.pos_end = pos_end
		self._type = _type

class SkipNode:
	def __init__(self, pos_start, pos_end, _type = None):
		self.pos_start = pos_start
		self.pos_end = pos_end
		self._type = _type

class BreakNode:
	def __init__(self, pos_start, pos_end, _type = None):
		self.pos_start = pos_start
		self.pos_end = pos_end
		self._type = _type

class GetNode:
	def __init__(self, parent, attr, pos_start, pos_end, _type = None):
		self.parent_type = parent
		self.Attr = attr
		self.pos_start = pos_start
		self.pos_end = pos_end
		self._type = _type

class SetNode:
	def __init__(self, parent, attr, value, pos_start, pos_end, _type = None):
		self.parent_type = parent
		self.Attr = attr
		self.value = value
		self.pos_start = pos_start
		self.pos_end = pos_end
		self._type = _type

class CWDNode:
	def __init__(self, directory_path, pos_start, pos_end, _type = None):
		self.directory_path = directory_path
		self.pos_start = pos_start
		self.pos_end = pos_end
		self._type = _type
		
class AddLibNode:
	def __init__(self, file_name, is_abs, pos_start, pos_end, _type = None):
		self.file_name = file_name
		self.is_abs = is_abs
		self.pos_start = pos_start
		self.pos_end = pos_end
		self._type = _type

class STDLibNode:
	def __init__(self, lib_name, pos_start, pos_end, _type = None):
		self.lib_name = lib_name
		self.pos_start = pos_start
		self.pos_end = pos_end
		self._type = _type