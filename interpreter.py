import sys
sys.setrecursionlimit(20_000)

class SchemeError(Exception):
    """
    A type of exception to be raised if there is an error with a Scheme
    program.  Should never be raised directly; rather, subclasses should be
    raised.
    """

    pass


class SchemeSyntaxError(SchemeError):
    """
    Exception to be raised when trying to evaluate a malformed expression.
    """

    pass


class SchemeNameError(SchemeError):
    """
    Exception to be raised when looking up a name that has not been defined.
    """

    pass


class SchemeEvaluationError(SchemeError):
    """
    Exception to be raised if there is an error during evaluation other than a
    SchemeNameError.
    """

    pass


############################
# Tokenization and Parsing #
############################


def number_or_symbol(value):
    """
    Helper function: given a string, convert it to an integer or a float if
    possible; otherwise, return the string itself
    
    """
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value


def tokenize(source):
    """
    Splits an input string into meaningful tokens (left parens, right parens,
    other whitespace-separated values).  Returns a list of strings.

    Arguments:
        source (str): a string containing the source code of a Scheme
                      expression
    """
    res = []
    lines = source.split("\n")
    for line in lines:
        token = ""
        for word in line:
            if word == ";":
                break
            if word in "()":
                token += " " + word + " "
            else:
                token += word
        res.extend(token.split())
    return res


def parse(tokens):
    """
    Parses a list of tokens, constructing a representation where:
        * symbols are represented as Python strings
        * numbers are represented as Python ints or floats
        * S-expressions are represented as Python lists

    Arguments:
        tokens (list): a list of strings representing tokens
    """
    if len(tokens) == 1:
        if tokens[0] in "()":
            raise SchemeSyntaxError
        return number_or_symbol(tokens[0])
    if len(tokens) > 1 and (tokens[0] != "(" or tokens[-1] != ")"):
        raise SchemeSyntaxError(tokens)

    def get_ind(s):
        num_open, num_close = 1, 0
        for i in range(s + 1, len(tokens) - 1):
            if tokens[i] == "(":
                num_open += 1
            elif tokens[i] == ")":
                num_close += 1
            if num_close == num_open:
                return i
        raise SchemeSyntaxError

    def parse_tok(s, e):
        result = []
        while s < e:
            if tokens[s] not in "()":
                result.append(number_or_symbol(tokens[s]))
                s += 1
            elif tokens[s] == "(":
                result.append(parse_tok(s + 1, get_ind(s)))
                s = get_ind(s) + 1
            else:
                raise SchemeSyntaxError
        return result

    return parse_tok(1, len(tokens) - 1)


######################
# Built-in Functions #
######################


class Pair:
    def __init__(self, car, cdr):
        self.car = car
        self.cdr = cdr


null = None


def multiply(args):
    res = 1
    for i in args:
        res *= i
    return res


def divide(args):
    return args[0] if len(args) == 1 else args[0] / multiply(args[1:])


comparison = {
    "equal?": lambda x, y: x == y,
    "<=": lambda x, y: x <= y,
    ">=": lambda x, y: x >= y,
    ">": lambda x, y: x > y,
    "<": lambda x, y: x < y,
}


def compare(func, arg, frame):
    func = comparison[func]
    for i in range(0, len(arg) - 1):
        if not func(evaluate(arg[i], frame), evaluate(arg[i + 1], frame)):
            return "#f"
    return "#t"


def combinator(combi, arg, frame):
    """and or not"""
    if combi == "not":
        if len(arg) != 1:
            raise SchemeEvaluationError
        return "#t" if evaluate(arg[0], frame) == "#f" else "#f"
    if combi == "and":
        for val in arg:
            if evaluate(val, frame) == "#f":
                return "#f"
        return "#t"
    for val in arg:
        if evaluate(val, frame) == "#t":
            return "#t"
    return "#f"


def condition(pred, t, f, frame):
    if evaluate(pred, frame) == "#t":
        return evaluate(t, frame)
    return evaluate(f, frame)


def cons(p1, p2):
    return Pair(p1, p2)


def get_car(arg):
    if not isinstance(arg, Pair):
        raise SchemeEvaluationError
    return arg.car


def get_cdr(arg):
    if not isinstance(arg, Pair):
        raise SchemeEvaluationError
    return arg.cdr


def make_list(arg):
    def make(ind):
        if ind + 1 > len(arg):
            return null
        return Pair(arg[ind], make(ind + 1))

    return make(0)


def is_list(arg):
    if not isinstance(arg, Pair) and arg != null:
        return "#f"
    if arg == null:
        return "#t"
    return is_list(arg.cdr)


def length(arg):
    if is_list(arg) == "#f":
        raise SchemeEvaluationError(arg)
    if arg == null:
        return 0
    return 1 + length(arg.cdr)


def get_at(ll, ind):
    if is_list(ll) == "#f":
        if isinstance(ll, Pair) and ind == 0:
            return ll.car
        raise SchemeEvaluationError
    if not isinstance(ind, int) or ind >= length(ll):
        raise SchemeEvaluationError
    if not ind:
        return ll.car
    return get_at(ll.cdr, ind - 1)


def copy_list(l1, l2):
    if l1 == null:
        return l2
    return Pair(l1.car, copy_list(l1.cdr, l2))


def append_list(arg):
    if not arg:
        return null
    if is_list(arg[0]) == "#f":
        raise SchemeEvaluationError
    if len(arg) == 1:
        return copy_list(arg[0], null)
    return copy_list(copy_list(arg[0], null), append_list(arg[1:]))


def begin(arg):
    return arg[-1]


scheme_builtins = {
    "+": sum,
    "-": lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
    "*": multiply,
    "/": divide,
    "and": combinator,
    "or": combinator,
    "not": combinator,
    "if": condition,
    "list": make_list,
    "list?": is_list,
    "length": length,
    "list-ref": get_at,
    "append": append_list,
    "car": get_car,
    "cdr": get_cdr,
    "cons": cons,
    "begin": begin,
}


class Frame:
    """Frame"""

    def __init__(self, parent):
        self.parent = parent
        self.variable = {}
        self.count = 0

    def add_var(self, name, val):
        self.variable[name] = val

    def get_var(self, name):
        if isinstance(name, (float, int)):
            raise SchemeEvaluationError
        if name in self.variable:
            return self.variable[name]
        if self.parent is not None:
            return self.parent.get_var(name)
        raise SchemeNameError(name)


Builtin = Frame(None)
Builtin.variable = scheme_builtins


def make_initial_frame():
    return Frame(Builtin)


class Func:
    """Function"""

    def __init__(self, frame, param, expression):
        self.frame = frame
        self.param = param
        self.myframe = None

        def exp():
            return evaluate(expression, self.myframe)

        self.expression = exp


##############
# Evaluation #
##############


def evaluate(tree, frame=make_initial_frame()):
    """
    Evaluate the given syntax tree according to the rules of the Scheme
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    """
    if isinstance(tree, str) and tree in {"#t", "#f"}:
        return tree
    if isinstance(tree, (float, int)):
        return tree
    if isinstance(tree, str):
        return frame.get_var(tree)
    if tree == []:
        return null
    if tree[0] == "define":
        if isinstance(tree[1], list):
            return evaluate(
                ["define", tree[1][0], ["lambda", tree[1][1:], tree[2]]], frame
            )
        else:
            res = evaluate(tree[2], frame)
            frame.add_var(tree[1], res)
            return res
    if tree[0] == "del":
        if tree[1] in frame.variable:
            val = frame.variable[tree[1]]
            del frame.variable[tree[1]]
            return val
        raise SchemeNameError("not found")
    if tree[0] == "lambda":
        func = Func(frame, tree[1], tree[2])
        frame.add_var(tree[0], func)
        return func
    if tree[0] == "let":
        new_frame = Frame(frame)
        for name, value in tree[1]:
            new_frame.add_var(name, evaluate(value, frame))
        return evaluate(tree[2], new_frame)
    if tree[0] == "set!":
        expr = evaluate(tree[2], frame)
        find_frame = frame
        while tree[1] not in find_frame.variable and find_frame.parent != null:
            find_frame = find_frame.parent
        if tree[1] not in find_frame.variable:
            raise SchemeNameError
        find_frame.variable[tree[1]] = expr
        return expr
    if isinstance(tree[0], str) and tree[0] in comparison:
        return compare(tree[0], tree[1:], frame)
    if isinstance(tree[0], list):
        frame.count += 1
        c = frame.count
        evaluate(["define", "()" + str(frame.count), tree[0]], frame)
        return evaluate(["()" + str(c)] + tree[1:], frame)
    get_func = frame.get_var(tree[0])
    if isinstance(get_func, Func):
        args = [
            evaluate(tree[i], frame) for i in range(1, len(tree))
        ]  # evaluate args in current frame
        func_class = get_func
        func_frame = Frame(func_class.frame)  # func_frame is new frame
        if len(args) != len(func_class.param):  # check num of args == num pf parameter
            raise SchemeEvaluationError
        for name, val in zip(func_class.param, args):
            func_frame.add_var(name, val)  # assign param name to value
        func_class.myframe = func_frame
        return func_class.expression()
    if get_func in [scheme_builtins["if"]]:
        return get_func(tree[1], tree[2], tree[3], frame)
    if get_func in [scheme_builtins[name] for name in ["and", "or", "not"]]:
        return get_func(tree[0], tree[1:], frame)
    if get_func in [scheme_builtins[name] for name in ["cons", "list-ref"]]:
        if len(tree) != 3:
            raise SchemeEvaluationError
        return get_func(evaluate(tree[1], frame), evaluate(tree[2], frame))
    if get_func in [
        scheme_builtins[name] for name in ["car", "cdr", "list?", "length"]
    ]:
        test_existence = [evaluate(tree[i], frame) for i in range(1, len(tree))]
        if len(tree) != 2:
            raise SchemeEvaluationError
        return get_func(evaluate(tree[1], frame))
    return get_func([evaluate(tree[i], frame) for i in range(1, len(tree))])


def remove_space(file):
    all_line = file.split("\n")
    new = ""
    def remove_comment(s):
        new_s = ""
        for char in s:
            if char == ";":
                return new_s
            new_s += char
        return new_s
    return new.join(map(remove_comment, all_line))


def get_line(code):
    """get line from output of remove space"""
    all_line = []
    ob, cb = 0, 0
    line = ""
    in_paren = False
    for char in code:
        if char == "(":
            if not in_paren and line:
                all_line.append(line)
                line = ""
            line += "("
            ob += 1
            in_paren = True
            continue
        line += char
        if char not in "()":
            continue
        cb += 1
        if cb >= ob:
            all_line.append(line)
            line = ""
            in_paren = False
    return all_line


def evaluate_exp(s):
    return evaluate(parse(tokenize(s)))


def evaluate_file(file_name, frame=make_initial_frame()):
    file = open(file_name, "r").read()
    all_line = get_line(remove_space(file))
    res = None
    for line in all_line:
        res = evaluate(parse(tokenize(line)), frame)
    return res

###########
# Example #
###########

x = evaluate_exp("(define x 7)")
print(x) # 7

l1 = evaluate_exp("(list 1 2 3)")
print(l1.car, l1.cdr.car, l1.cdr.cdr.car, length(l1)) # 1 2 3 3

file_1 = evaluate_file("test1.txt")
print(file_1) # 12

file_2  = evaluate_file("test2.txt")
print(file_2) # 27

file_3 = evaluate_file("test3.txt")
print(file_3) # 10

file_4 = evaluate_file("test4.txt")
print(file_4) # 15
