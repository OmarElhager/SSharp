<img width="529" height="136" alt="ssharp-original" src="https://github.com/user-attachments/assets/6e117ed2-d3b5-40c4-9f28-bf0a627429db" />

S# is a custom programming language built from scratch in Python.  
It features a custom interpreter, functions, recursion, control flow, variables, and expandable language architecture.

---

## Features

- Variables (`let`)
- Arithmetic expressions
- Print statements
- If / While control flow
- Functions + recursion
- Return values
- Multi-line programs
- Custom S# syntax
- Expandable architecture for future compiler / VM versions

---

## Examples

### Functions + Recursion

```s#
func fact(n):
    if n == 0:
        return 1
    return n * fact(n - 1)

print fact(5)
````

**Output:**

```
120
```

---

### Fibonacci (Recursion)

```s#
func fib(n):
    if n == 0:
        return 0
    if n == 1:
        return 1
    return fib(n - 1) + fib(n - 2)

print fib(6)
```

**Output:**

```
8
```

---

### Variables + Math

```s#
let a = 10
let b = 20
let c = a + b * 2

print c
```

**Output:**

```
50
```

---

### If Statement

```s#
let age = 18

if age >= 18:
    print "adult"
```

**Output:**

```
adult
```

---

### While Loop

```s#
let x = 5

while x > 0:
    print x
    let x = x - 1
```

**Output:**

```
5
4
3
2
1
```

---

### Function with Parameters

```s#
func add(a, b):
    return a + b

print add(7, 3)
```

**Output:**

```
10
```

---

### Function Without Return

```s#
func greet(name):
    print name

greet("Omar")
```

**Output:**

```
Omar
```

---

### Countdown Example

```s#
func countdown(n):
    while n > 0:
        print n
        let n = n - 1

countdown(3)
```

**Output:**

```
3
2
1
```

---

### Nested Expressions

```s#
let result = (5 + 3) * 2
print result
```

**Output:**

```
16
```

---

### Strings

```s#
print "hello world"
```

**Output:**

```
hello world
```

---

## How to Run

```bash
python runner.py
```

Write your code inside:

```
program.s#
```

---

