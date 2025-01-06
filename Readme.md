# AST ERROR DETECTION

## Overview

**ast-error-detection** is a Python library designed for analyzing and annotating algorithmic errors in code. It leverages the Abstract Syntax Tree (AST) module from Python's standard library to identify, categorize, and contextualize errors. The output of the library is a list of errors, where each error is a dictionary describing the issue and its context.

This library is under an ongoing scientific study. If you use it for academic purposes, please cite the forthcoming publication (details will be provided).

---

## Features

- Parses and processes Python code using the AST module.
- Identifies and categorizes errors with detailed contextual information.
- Provides actionable insights for debugging.

---

## Installation

Install the package via pip:

```bash
pip install ast_error_detection
```

---

## Usage

Here’s a basic example of how to use the library:

```python
from ast-error-detection import get_code_errors

# Example erroneous code to analyze
code_1 = """ 
# Code snippet here
"""
# Example expected code
code_2 = """ 
# Code snippet here
"""

# Convert AST to custom node representation
result = get_code_errors(code_1, code_2)

# Print the results
print(result)
```

### Output Format

The output is always a list of errors. Each error is a dictionary structured as follows:

- **For `delete` or `insert` errors (3 elements):**
  - `error`: Description of the error.
  - `value`: The value to delete or insert.
  - `context`: Contextual location of the error (see below).

- **For `update` errors (4 elements):**
  - `error`: Description of the error.
  - `old_value`: The old value to update.
  - `new_value`: The new value to update.
  - `context`: Contextual location of the error.

#### Context Format

The context describes where the error occurred in the code execution hierarchy. For example:

`Module > Function Name > For Loop > If > Condition`

This indicates that the error is in the condition of an `if` statement inside a `for` loop within a function in the module.

---

## Example

### Input Code 1
```python
print('Hello')
```

### Input Code 2
```python
print('Hello1')
```

### Output
```bash
[('CONST_VALUE_MISMATCH', "Const: 'Hello'", "Const: 'Hello1'", "Module > Call: print > Const: 'Hello'")]
```

---

## License

This project is licensed under the GNU Affero General Public License v3 (AGPL-3.0). If you wish to use this library for proprietary or commercial purposes, you must obtain a separate license. 

Please contact Badmavasan [Lip6] at [badmavasan.kirouchenassamy@lip6.fr] for commercial licensing inquiries.

---

## Scientific Publication

This library is part of an ongoing scientific study. If you use it for academic purposes, please cite the forthcoming publication:

```
[Publication details will be added here once available.]
```

Stay tuned for updates!
