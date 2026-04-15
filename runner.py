from engine import compile_and_run

with open("program.s#", "r") as f:
    code = f.read()

compile_and_run(code)
