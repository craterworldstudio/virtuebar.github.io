from context_i import Context
from lexer_i import *
from parser_i import *
from symbol_table_i import *
from Interpreter_i import *
from values_i import *

###########################################
# RUN
###########################################

#region Values
global_symbol_table = SymbolTable()
global_symbol_table.set("NoC", [Number.null, 'Null'])
global_symbol_table.set("None", [Number.none, 'None'])
global_symbol_table.set("True", [Number.true, 'True'])
global_symbol_table.set("False", [Number.false, 'False'])
global_symbol_table.set("pi", Number.math_PI)

#none_val = String("None")
#endregion

#region IO
global_symbol_table.set("out", BuiltInFunction.printout)
global_symbol_table.set("rut", BuiltInFunction.printreturn)
global_symbol_table.set("tin", BuiltInFunction.typein)
global_symbol_table.set("m_tin", BuiltInFunction.multi_typein)
global_symbol_table.set("tin_int", BuiltInFunction.typein_int)
#endregion

#region Clean up and Verification
global_symbol_table.set("clr", BuiltInFunction.clear)
global_symbol_table.set("cls", BuiltInFunction.clear)
global_symbol_table.set("is_num", BuiltInFunction.is_number)
global_symbol_table.set("is_str", BuiltInFunction.is_string)
global_symbol_table.set("is_list", BuiltInFunction.is_list)
global_symbol_table.set("is_func", BuiltInFunction.is_function)
#endregion

#region List Manupulation
global_symbol_table.set("append", BuiltInFunction.append)
global_symbol_table.set("pop", BuiltInFunction.pop)
global_symbol_table.set("extend", BuiltInFunction.extend)
global_symbol_table.set("max", BuiltInFunction.max)
global_symbol_table.set("min", BuiltInFunction.min)
#endregion

#region Math
global_symbol_table.set("floor", BuiltInFunction.floor)
global_symbol_table.set("ceil", BuiltInFunction.ceil)
global_symbol_table.set("sqre", BuiltInFunction.square)
global_symbol_table.set("cube", BuiltInFunction.cube)
global_symbol_table.set("tess", BuiltInFunction.tessaract)
global_symbol_table.set("add", BuiltInFunction.add)
global_symbol_table.set("sub", BuiltInFunction.subt)
global_symbol_table.set("mul", BuiltInFunction.mult)
global_symbol_table.set("div", BuiltInFunction.divi)
global_symbol_table.set("sqrt", BuiltInFunction.sqrt)
global_symbol_table.set("cbrt", BuiltInFunction.cbrt)
global_symbol_table.set("ranint", BuiltInFunction.ranint)
global_symbol_table.set("len", BuiltInFunction.len)
global_symbol_table.set("map", BuiltInFunction.map)
global_symbol_table.set("range", BuiltInFunction.range)
#endregion

#region String Manupulation
global_symbol_table.set("concat", BuiltInFunction.contatinate)
global_symbol_table.set("sub_str", BuiltInFunction.substring)
global_symbol_table.set("rplc", BuiltInFunction.replace)
global_symbol_table.set("lwr", BuiltInFunction.lowercase)
global_symbol_table.set("upr", BuiltInFunction.uppercase)
global_symbol_table.set("split", BuiltInFunction.split)
global_symbol_table.set("join", BuiltInFunction.join)
#endregion

#region File Handling
global_symbol_table.set("open", BuiltInFunction.open)
global_symbol_table.set("read", BuiltInFunction.read)
global_symbol_table.set("write", BuiltInFunction.write)
#endregion

global_symbol_table.set("run", BuiltInFunction.run)
global_symbol_table.set("clean", BuiltInFunction.clean)
global_symbol_table.set("glob_attr", BuiltInFunction.global_attributes)
global_symbol_table.set("stay", BuiltInFunction.stay)
global_symbol_table.set("test", BuiltInFunction.test)
global_symbol_table.set("get_cwd", BuiltInFunction.get_cwd)

def run(fn, text, path = None, header = False):

    #Generate tokens

    lexer = Lexer(fn, text, path)
    data = lexer.make_tokens()
    #print("Data:",data)
    tokens, ProgData, error = data
    #print(tokens)
    if error: return None, error

    # Generate Abstract Syntax Tree
    parser = Parser(tokens, header)
    ast = parser.parse()
    #print(ast.node)
    
    if ast.error: return None, ast.error

    #Run program
    interpreter = Interpreter(tokens, ProgData, global_symbol_table, BuiltInFunction)
    #print(lexer.fn)
    context = Context(lexer.fn)
    context.symbol_table = global_symbol_table
    result = interpreter.visit(ast.node, context)
    

    #print("FINAL", result.value.elements, result.error)

    try:
        if type(result.value) == values_i.List:
            #print(type(result.value), result.value, result.value.elements)
            #print(type(result.value.elements), result.value.elements)
            for i in result.value.elements:
                #print(19002, i, type(i), type(Number.none), Number.none)
                if i.value is None:
                    #print(1)
                    #print(1, i, type(i))
                    ind = result.value.elements.index(i)
                    #print(ind)
                    del result.value.elements[ind]

        else:
            if result.value == None:
                #print(result.value)
                result.value = None
    except:
        pass
    
    return result.value, result.error
