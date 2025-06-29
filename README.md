# PyLisp: A Scheme-like LISP Interpreter in Python

![Python Version](https://img.shields.io/badge/python-3.x-blue.svg)

A lightweight, from-scratch interpreter for a variant of the Scheme LISP programming language, implemented entirely in Python. This project can parse and evaluate LISP code provided as a string or from a file, supporting functions, conditionals, variables, and basic data structures.

## Key Features

- **Core Operations:** Supports basic arithmetic (`+`, `-`, `*`, `/`) and logical (`>`, `<`, `=`, `and`, `or`) operators.
- **Control Flow:** Implements conditional `if` statements for branching logic.
- **Variable Scoping:** Allows for defining and deleting variables within the environment.
- **First-Class Functions:** Supports defining named functions, as well as anonymous `lambda` functions.
- **Data Structures:** Includes support for basic data structures like linked lists and arrays.
- **Custom Error Handling:** Features its own set of error types for robust evaluation.
- **File & String Evaluation:** Can interpret code directly from a string or from a `.txt` file.

## Getting Started

To get a local copy up and running, follow these simple steps.

### Prerequisites

All you need is Python 3.x installed on your machine.

### Installation

1.  Clone the repository:
    ```sh
    git clone https://github.com/Jonathan-Tjandra/LISP_Interpreter.git
    ```
2.  Navigate to the project directory:
    ```sh
    cd LISP_Interpreter
    ```
    There are no external dependencies to install.

## Usage API

The interpreter can be used in two primary ways. Assuming your main Python file is named `interpreter.py`:

### 1. Interactive Evaluation (Single Expression)

Use the `evaluate_exp()` function to evaluate a single line of LISP code and interact with the results in Python.

**Python Code (`main.py`):**
```python
# Assuming your file with the functions is interpreter.py
from interpreter import evaluate_exp, length

# Example 1: Defining a variable
# The interpreter executes the definition and returns the value.
result_val = evaluate_exp("(define x 7)")
print(f"Result of defining x: {result_val}")
# Expected output: Result of defining x: 7

# Example 2: Working with lists
# The interpreter returns a list object that can be inspected in Python.
l1 = evaluate_exp("(list 1 2 3)")
print(f"List created. Accessing elements via .car/.cdr: {l1.car}, {l1.cdr.car}, {l1.cdr.cdr.car}")
# Expected output: List created. Accessing elements via .car/.cdr: 1, 2, 3

# Assuming you have a helper 'length' function available in your Python code
print(f"Length of the list: {length(l1)}")
# Expected output: Length of the list: 3
```

### 2. File-Based Evaluation

Use the `evaluate_file()` function to execute a script from a `.txt` file. This is ideal for more complex programs. The interpreter will return the value of the last expression evaluated in the file.

**Example LISP file (`examples/reduce_example.txt`):**
```lisp
; Example demonstrating a more complex recursive function: reduce

(define (reduce func l st) ; reduce function
  (if (equal? l ())
      st
      (if (equal? (cdr l) ())
          (func st (car l))
          (reduce func (cdr l) (func st (car l))))))

; Use the reduce function to sum a list of numbers
(reduce + (list 1 2 3 4 5) 0) ; Returns 15
```

**Python Code (`main.py`):**
```python
from interpreter import evaluate_file

result = evaluate_file("examples/reduce_example.txt")
print(f"The result from the reduce script is: {result}")
# Expected output: The result from the reduce script is: 15
```