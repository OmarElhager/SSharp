import re

# =========================
# GLOBALS
# =========================
functions = {}

# =========================
# RETURN SIGNAL
# =========================
class ReturnSignal(Exception):
    def __init__(self, value):
        self.value = value

# =========================
# ARG SPLITTER
# =========================
def split_args(s):
    args = []
    cur = ""
    depth = 0

    for ch in s:
        if ch == "," and depth == 0:
            args.append(cur.strip())
            cur = ""
        else:
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
            cur += ch

    if cur.strip():
        args.append(cur.strip())

    return args

# =========================
# FUNCTION CALLER
# =========================
def call_function(name, args):
    if name not in functions:
        raise Exception(f"Undefined function {name}")

    params, body = functions[name]
    scope = {}

    for p, a in zip(params, args):
        scope[p] = a

    try:
        run_block(body, scope)
    except ReturnSignal as r:
        return r.value

    return None

# =========================
# EVAL EXPRESSIONS
# =========================
def eval_expr(expr, scope):
    expr = expr.strip()

    # string
    if expr.startswith('"') and expr.endswith('"'):
        return expr[1:-1]

    # repeatedly resolve function calls
    pattern = r'([A-Za-z_]\w*)\(([^()]*)\)'

    while re.search(pattern, expr):
        match = re.search(pattern, expr)

        name = match.group(1)
        raw_args = match.group(2).strip()

        args = []
        if raw_args:
            args = split_args(raw_args)
            args = [eval_expr(a, scope) for a in args]

        result = call_function(name, args)

        expr = expr[:match.start()] + str(result) + expr[match.end():]

    # variables
    for name in sorted(scope.keys(), key=len, reverse=True):
        expr = re.sub(rf'\b{name}\b', str(scope[name]), expr)

    return eval(expr, {"__builtins__": {}}, {})

# =========================
# EXECUTION
# =========================
def run_block(lines, scope):
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        if not line:
            i += 1
            continue

        # print
        if line.startswith("print "):
            print(eval_expr(line[6:], scope))

        # let
        elif line.startswith("let "):
            rest = line[4:]
            name, expr = rest.split("=", 1)
            scope[name.strip()] = eval_expr(expr.strip(), scope)

        # if
        elif line.startswith("if ") and line.endswith(":"):
            cond = line[3:-1]
            body = []

            i += 1
            while i < len(lines) and lines[i].startswith("    "):
                body.append(lines[i][4:])
                i += 1

            if eval_expr(cond, scope):
                run_block(body, dict(scope))

            continue

        # while
        elif line.startswith("while ") and line.endswith(":"):
            cond = line[6:-1]
            body = []

            i += 1
            while i < len(lines) and lines[i].startswith("    "):
                body.append(lines[i][4:])
                i += 1

            while eval_expr(cond, scope):
                run_block(body, scope)

            continue

        # return
        elif line.startswith("return "):
            raise ReturnSignal(eval_expr(line[7:], scope))

        i += 1

# =========================
# MAIN ENTRY
# =========================
def compile_and_run(source):
    global functions
    functions = {}

    lines = source.split("\n")
    main = []

    i = 0
    while i < len(lines):
        line = lines[i]

        if line.strip().startswith("func "):
            header = line.strip()

            name = header.split()[1].split("(")[0]
            params_txt = header[header.find("(")+1:header.find(")")]
            params = [p.strip() for p in params_txt.split(",") if p.strip()]

            body = []
            i += 1

            while i < len(lines) and lines[i].startswith("    "):
                body.append(lines[i][4:])
                i += 1

            functions[name] = (params, body)
            continue

        else:
            main.append(line)

        i += 1

    run_block(main, {})
