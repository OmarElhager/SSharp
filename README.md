# S# Programming Language

S# is a custom programming language built from scratch in Python.  
It features a bytecode compiler, virtual machine, functions, recursion, and object-oriented programming.

---

## Features

- Variables (`let`)
- Arithmetic expressions
- If / While control flow
- Functions + recursion
- Classes + methods
- Objects (`self`)
- Import system
- Bytecode virtual machine

---

## Example

### Functions + Recursion

```s#
func fact(n):
    if n == 0:
        return 1
    return n * fact(n - 1)

print fact(5)
```

**Output:**
```
120
```

---

### Classes

```s#
class Person:
    func greet():
        print "hello"

let p = Person()
p.greet()
```

**Output:**
```
hello
```

---

## How to Run

```bash
python runner.py
```

Write your code in:

```
program.s#
```

---

## Project Goal

This project explores:

- programming language design
- compilers
- virtual machines
- low-level execution models

It is a learning project focused on understanding how real programming languages work internally.
