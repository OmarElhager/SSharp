# engine.py
# S# v8 — real bytecode compiler + VM
# features:
# - let / print / return
# - if / while
# - functions + recursion
# - classes + objects + methods + self
# - import "file.s#"
# - file execution
# - bytecode VM
# - parser-based compiler

import re
import os

# =====================================================
# GLOBAL REGISTRIES
# =====================================================
FUNCTIONS = {}
CLASSES = {}
LOADED_FILES = set()

# =====================================================
# OPCODES
# =====================================================
PUSH = "PUSH"
LOAD = "LOAD"
STORE = "STORE"

ADD = "ADD"
SUB = "SUB"
MUL = "MUL"
DIV = "DIV"

EQ = "EQ"
GT = "GT"
LT = "LT"

PRINT = "PRINT"

JMP = "JMP"
JMPF = "JMPF"

CALL = "CALL"
RET = "RET"

NEW = "NEW"
GETATTR = "GETATTR"
SETATTR = "SETATTR"
MCALL = "MCALL"

POP = "POP"

# =====================================================
# TOKENIZER
# =====================================================
def tokenize(text):
    return re.findall(
        r'"[^"]*"|\d+|==|!=|<=|>=|[A-Za-z_]\w*|[{}()\[\].,:+\-*/<>]|=',
        text
    )

# =====================================================
# AST PARSER
# =====================================================
class Parser:
    def __init__(self, tokens):
        self.t = tokens
        self.i = 0

    def peek(self):
        if self.i < len(self.t):
            return self.t[self.i]
        return None

    def eat(self):
        x = self.peek()
        self.i += 1
        return x

    def parse(self):
        return self.expr()

    def expr(self):
        node = self.term()

        while self.peek() in ("+", "-", "==", ">", "<"):
            op = self.eat()
            right = self.term()
            node = ("binop", op, node, right)

        return node

    def term(self):
        node = self.factor()

        while self.peek() in ("*", "/"):
            op = self.eat()
            right = self.factor()
            node = ("binop", op, node, right)

        return node

    def factor(self):
        tok = self.peek()

        if tok is None:
            raise Exception("Unexpected EOF")

        if tok.isdigit():
            self.eat()
            return ("num", int(tok))

        if tok.startswith('"'):
            self.eat()
            return ("str", tok[1:-1])

        if tok == "(":
            self.eat()
            node = self.expr()
            self.eat()
            return node

        if re.match(r"[A-Za-z_]\w*", tok):
            name = self.eat()

            # object.method(...)
            if self.peek() == ".":
                self.eat()
                method = self.eat()
                self.eat()  # (
                args = []

                if self.peek() != ")":
                    while True:
                        args.append(self.expr())
                        if self.peek() == ",":
                            self.eat()
                            continue
                        break
                self.eat()

                return ("mcall", name, method, args)

            # function/class(...)
            if self.peek() == "(":
                self.eat()
                args = []

                if self.peek() != ")":
                    while True:
                        args.append(self.expr())
                        if self.peek() == ",":
                            self.eat()
                            continue
                        break
                self.eat()

                return ("call", name, args)

            return ("var", name)

        raise Exception("Unexpected token " + str(tok))


# =====================================================
# BYTECODE COMPILER
# =====================================================
def compile_ast(node):
    t = node[0]

    if t == "num":
        return [(PUSH, node[1])]

    if t == "str":
        return [(PUSH, node[1])]

    if t == "var":
        return [(LOAD, node[1])]

    if t == "call":
        name = node[1]
        args = node[2]

        bc = []
        for a in args:
            bc += compile_ast(a)

        bc.append((CALL, name, len(args)))
        return bc

    if t == "mcall":
        obj = node[1]
        method = node[2]
        args = node[3]

        bc = [(LOAD, obj)]

        for a in args:
            bc += compile_ast(a)

        bc.append((MCALL, method, len(args)))
        return bc

    if t == "binop":
        op = node[1]
        left = compile_ast(node[2])
        right = compile_ast(node[3])

        bc = left + right

        if op == "+": bc.append(ADD)
        elif op == "-": bc.append(SUB)
        elif op == "*": bc.append(MUL)
        elif op == "/": bc.append(DIV)
        elif op == "==": bc.append(EQ)
        elif op == ">": bc.append(GT)
        elif op == "<": bc.append(LT)

        return bc

    raise Exception("Unknown AST")


# =====================================================
# LINE COMPILER
# =====================================================
def compile_block(lines):
    bc = []
    i = 0

    while i < len(lines):
        raw = lines[i]
        line = raw.strip()

        if not line:
            i += 1
            continue

        # import
        if line.startswith("import "):
            fname = line[7:].strip().replace('"', "")
            load_file(fname)
            i += 1
            continue

        # class
        if line.startswith("class "):
            name = line.split()[1].replace(":", "")

            block = []
            i += 1
            while i < len(lines) and lines[i].startswith("    "):
                block.append(lines[i][4:])
                i += 1

            compile_class(name, block)
            continue

        # func
        if line.startswith("func "):
            header = line
            name = header.split()[1].split("(")[0]
            params = header[header.find("(")+1:header.find(")")].split(",")
            params = [x.strip() for x in params if x.strip()]

            block = []
            i += 1
            while i < len(lines) and lines[i].startswith("    "):
                block.append(lines[i][4:])
                i += 1

            FUNCTIONS[name] = (params, compile_block(block))
            continue

        # if
        if line.startswith("if "):
            cond = line[3:].replace(":", "")
            cond_ast = Parser(tokenize(cond)).parse()

            block = []
            i += 1
            while i < len(lines) and lines[i].startswith("    "):
                block.append(lines[i][4:])
                i += 1

            body = compile_block(block)

            bc += compile_ast(cond_ast)
            bc.append((JMPF, len(body) + 1))
            bc += body
            continue

        # while
        if line.startswith("while "):
            cond = line[6:].replace(":", "")
            cond_ast = Parser(tokenize(cond)).parse()

            block = []
            i += 1
            while i < len(lines) and lines[i].startswith("    "):
                block.append(lines[i][4:])
                i += 1

            body = compile_block(block)
            cond_bc = compile_ast(cond_ast)

            start = len(bc)

            bc += cond_bc
            bc.append((JMPF, len(body) + 2))
            bc += body
            bc.append((JMP, -(len(cond_bc) + len(body) + 1)))
            continue

        # return
        if line.startswith("return "):
            expr = line[7:]
            ast = Parser(tokenize(expr)).parse()
            bc += compile_ast(ast)
            bc.append(RET)
            i += 1
            continue

        # print
        if line.startswith("print "):
            expr = line[6:]
            ast = Parser(tokenize(expr)).parse()
            bc += compile_ast(ast)
            bc.append(PRINT)
            i += 1
            continue

        # let
        if line.startswith("let "):
            left, right = line[4:].split("=", 1)
            name = left.strip()
            expr = right.strip()

            ast = Parser(tokenize(expr)).parse()
            bc += compile_ast(ast)
            bc.append((STORE, name))
            i += 1
            continue

        # plain expr
        ast = Parser(tokenize(line)).parse()
        bc += compile_ast(ast)
        bc.append(POP)

        i += 1

    return bc


# =====================================================
# CLASS COMPILER
# =====================================================
def compile_class(name, lines):
    methods = {}
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        if line.startswith("func "):
            header = line
            fname = header.split()[1].split("(")[0]
            params = header[header.find("(")+1:header.find(")")].split(",")
            params = [x.strip() for x in params if x.strip()]

            block = []
            i += 1

            while i < len(lines) and lines[i].startswith("    "):
                block.append(lines[i][4:])
                i += 1

            methods[fname] = (params, compile_block(block))
            continue

        i += 1

    CLASSES[name] = methods


# =====================================================
# VM
# =====================================================
def run(bytecode, scope=None):
    if scope is None:
        scope = {}

    stack = []
    ip = 0

    while ip < len(bytecode):
        ins = bytecode[ip]

        if isinstance(ins, tuple):
            op = ins[0]

            if op == PUSH:
                stack.append(ins[1])

            elif op == LOAD:
                stack.append(scope.get(ins[1]))

            elif op == STORE:
                scope[ins[1]] = stack.pop()

            elif op == CALL:
                name = ins[1]
                argc = ins[2]

                args = [stack.pop() for _ in range(argc)][::-1]

                # class constructor
                if name in CLASSES:
                    obj = {"__class__": name, "__fields__": {}}

                    if "init" in CLASSES[name]:
                        params, body = CLASSES[name]["init"]

                        local = {"self": obj}
                        for p, a in zip(params, args):
                            local[p] = a

                        run(body, local)

                    stack.append(obj)

                else:
                    params, body = FUNCTIONS[name]

                    local = {}
                    for p, a in zip(params, args):
                        local[p] = a

                    ret = run(body, local)
                    stack.append(ret)

            elif op == MCALL:
                method = ins[1]
                argc = ins[2]

                args = [stack.pop() for _ in range(argc)][::-1]
                obj = stack.pop()

                cname = obj["__class__"]
                params, body = CLASSES[cname][method]

                local = {"self": obj}

                for p, a in zip(params, args):
                    local[p] = a

                ret = run(body, local)
                stack.append(ret)

            elif op == JMP:
                ip += ins[1]
                continue

            elif op == JMPF:
                val = stack.pop()
                if not val:
                    ip += ins[1]
                    continue

        else:
            if ins == ADD:
                b = stack.pop(); a = stack.pop(); stack.append(a+b)
            elif ins == SUB:
                b = stack.pop(); a = stack.pop(); stack.append(a-b)
            elif ins == MUL:
                b = stack.pop(); a = stack.pop(); stack.append(a*b)
            elif ins == DIV:
                b = stack.pop(); a = stack.pop(); stack.append(a/b)
            elif ins == EQ:
                b = stack.pop(); a = stack.pop(); stack.append(a==b)
            elif ins == GT:
                b = stack.pop(); a = stack.pop(); stack.append(a>b)
            elif ins == LT:
                b = stack.pop(); a = stack.pop(); stack.append(a<b)
            elif ins == PRINT:
                print(stack.pop())
            elif ins == POP:
                if stack: stack.pop()
            elif ins == RET:
                return stack.pop() if stack else None

        ip += 1

    return None


# =====================================================
# FILE LOADER
# =====================================================
def load_file(fname):
    if fname in LOADED_FILES:
        return

    LOADED_FILES.add(fname)

    if not os.path.exists(fname):
        raise Exception("File not found: " + fname)

    with open(fname, "r") as f:
        code = f.read()

    compile_block(code.split("\n"))


# =====================================================
# ENTRY
# =====================================================
def compile_and_run(code):
    bytecode = compile_block(code.split("\n"))
    run(bytecode)