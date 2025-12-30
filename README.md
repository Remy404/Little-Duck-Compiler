# 🦆 Little Duck Compiler

**Little Duck** is a functional compiler for a strongly-typed programming language, designed and developed as a capstone project for the **Compiler Design** course. This project implements the entire compilation pipeline, from lexical analysis to execution within a custom-built Virtual Machine.



## 🛠️ Technical Specifications

* **Lexical & Syntax Analysis**: Built with **PLY (Python Lex-Yacc)** to handle context-free grammars and tokenization.
* **Semantic Analysis**: Implements a robust **Semantic Cube** for type-checking validation and a Symbol Table for scope management.
* **Code Generation**: Produces **Quadruples** as an intermediate code representation to optimize execution flow.
* **Virtual Machine**: A custom-built engine that manages virtual memory segmentation (Local, Global, Constant, and Temporary) and executes instructions in real-time.

## 🚀 Language Features

* **Control Structures**: Supports conditional logic (`if-else`) and loops (`while`).
* **Data Types**: Handles `int` and `float` with strict type-checking.
* **Functions**: Supports function declarations, modularity, and parameter passing.
* **I/O Operations**: Built-in `print` function for data output.

## 🏗️ System Architecture

The compilation process follows four critical stages:

1. **Scanner & Parser**: Validates source code structure against the defined grammar.
2. **Semantic Cube**: A logical matrix used to validate type compatibility across all operations.
3. **Quadruple Generation**: Translates source code into 4-element instructions (operator, operand1, operand2, result).
4. **Virtual Machine**: The execution core that interprets quadruples and manages virtual memory addresses during runtime.

### Prerequisites
* Python 3.x
* PLY (Python Lex-Yacc) library
