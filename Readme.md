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

There are 2 ways to use this library. 

### Primary Error Detection

The Primary Error Detection layer is responsible for identifying low-level structural and content modifications between two trees (typically a reference and a hypothesis tree). It serves as the foundational layer for subsequent high-level error interpretation. This component relies on the Zhang-Shasha Edit Distance Algorithm, a classic algorithm for computing the minimum-cost sequence of operations needed to transform one tree into another. The algorithm outputs three types of edit operations:
- Insertions
- Deletions
- Updates

Each operation corresponds to a specific node-level change and includes metadata `context`. These operations collectively represent the raw set of changes (or "primary errors") from which higher-level interpretations can be derived.

```python
from ast-error-detection import get_primary_code_errors

# Example erroneous code to analyze
code_1 = """ 
# Code snippet here
"""
# Example expected code
code_2 = """ 
# Code snippet here
"""

# Convert AST to custom node representation
result = get_primary_code_errors(code_1, code_2)

# Print the results
print(result)
```

#### Output Format

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


### Typology Based Error Detection

While primary error detection provides atomic operations, Typology-Based Error Detection serves as a semantic interpretation layer. It classifies the primary operations into predefined error types (typologies), allowing for more meaningful feedback and error analysis.

This module:
- Consumes the output of the Primary Error Detection layer.
- Applies a mapping schema to group and classify operations into specific typology classes.
- Detects compound or context-dependent errors by evaluating relationships between multiple primary operations. (logic of each error is defined in the Table below)

Unlike simple pairwise comparison, this component supports comparison of one erroneous code instance against multiple possible correct codes.
- The first input is the hypothesis (erroneous AST).
- The second input is a list of reference ASTs (multiple correct solutions).
- The system computes the edit distance to each reference, selects the closest match, and performs typology-based annotation against that reference.

This ensures the most contextually relevant and minimal-error interpretation is selected for annotation.

```python
from ast-error-detection import get_typology_based_code_error

# Example erroneous code to analyze
code_1 = """ 
# Code snippet here
"""
# Example expected code list
expected_codes = [
  """ 
  # Code snippet 1
  """,
  """ 
  # Code snippet 2
  """
]

# Convert AST to custom node representation
result = get_typology_based_code_error(code_1, expected_codes)

# Print the results
print(result)
```

#### Output Format

A list of string (Error tags) from the predefined set of Error tags (Ref Table below)

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

### Output with Primary error Detection 
```python
[('CONST_VALUE_MISMATCH', "Const: 'Hello'", "Const: 'Hello1'", "Module > Call: print > Const: 'Hello'")]
```

### Output with Typology error Detection

```python
['FUNCTION_CALL_PARAMETER_ERROR']
```

### List of error tags 

| **ERROR** | **DETAILS / EXAMPLES** | **TASK TYPE(S)** | **ERROR TAG** | **IN LIBRARY?** |
|:---------:|:----------------------|:-----------------|:-------------:|:---------------:|
| | **VARIABLES** | | | |
| (**VA-Err1**) Error in variable declaration and initialization | Wrong type chosen for the variable or wrong value during initialization | VA – Produce a variable (and children) | **VARIABLE_DECLARATION_INITIALIZATION_ERROR** | ✗ |
| (**VA-Err2**) Missing variable increment | Typical counter problem: variable never modified or reset each time | — | **VARIABLE_MISSING_INCREMENT** | ✗ |
| (**VA-Err3**) Invalid variable name | Forbidden character or reserved keyword used | VA – Choose a valid name | **VARIABLE_INVALID_NAME** | ✗ |
| | **CONDITIONAL STATEMENTS** | | | |
| (**CS-Err1**) Incorrect number of branches | A case is missing or branches overlap | IC – Determine the necessary branches; partition the cases | **CONDITIONAL_MISSING_BRANCH** | ✗ |
| (**CS-Err2**) Misplaced instructions in a conditional | An instruction is in the wrong branch or outside the conditional | IC – Assign the right action to each branch | **CONDITIONAL_MISPLACED_INSTRUCTIONS** | ✗ |
| | **FUNCTIONS** | | | |
| (**F-Err1**) Function definition error | Missing/incorrect parameters, wrong preconditions, incorrect return | F – Define parameters, preconditions, returns | **FUNCTION_DEFINITION_ERROR** | ✗ |
| (**F-Err2**) Function call parameter error | Called with wrong parameters or return value not captured | — | **FUNCTION_CALL_PARAMETER_ERROR** | ✗ |
| (**F-Err3**) Invalid function or parameter name | Forbidden character or reserved keyword used | F – Name function and parameters | **FUNCTION_INVALID_NAME** | ✗ |
| | **LOOPS** | | | |
| (**LO-Err1**) Loop iterator usage error | Wrong start/end values or iterator ignored | B – Correct use of loop iterator | **LOOP_ITERATOR_USAGE_ERROR** | ✗ |
| (**LO-Err2**) Off-by-one loop error | Loop runs one time too many or too few | B – Determine iteration count | **LOOP_OFF_BY_ONE_ERROR** | ✗ |
| (**LO-Err3**) Wrong loop iteration count (> 2) | Loop executes an entirely wrong number of times | B – Determine iteration count | **LOOP_WRONG_ITERATION_COUNT** | ✗ |
| (**LO-Err4**) Start condition error | Incorrect initial loop condition | B – Stop condition (unbounded loop) | **LOOP_START_CONDITION_ERROR** | ✗ |
| (**LO-Err5**) Update condition error | Stop condition never updated or updated incorrectly | B – Modify stop condition | **LOOP_UPDATE_CONDITION_ERROR** | ✗ |
| (**LO-Err6**) Missing instruction in loop body (not present anywhere) | Expected instruction absent from both loop and program | B – Instructions each iteration | **LOOP_BODY_MISSING_INSTRUCTIONS** | ✗ |
| (**LO-Err7**) Missing instruction in loop body (moved elsewhere) | Instruction exists but outside the loop | B – Instructions each iteration | **LOOP_BODY_INSTRUCTIONS_MOVED_OUT** | ✗ |
| (**LO-Err8**) Incorrect instruction close to expected | Instruction present but incorrect / nearly correct | B – Instructions each iteration | **LOOP_BODY_INCORRECT_INSTRUCTIONS_NEAR** | ✗ |
| (**LO-Err9**) Extra unwanted instruction in loop body | Superfluous instruction unrelated to task | B – Instructions each iteration | **LOOP_BODY_EXTRA_INSTRUCTIONS** | ✗ |
| | **EXPRESSIONS** | | | |
| (**EXP-Err1**) Boolean condition error | Uses `<` instead of `≤`, etc. | IC – Correct boolean expression | **EXPRESSION_BOOLEAN_CONDITION_ERROR** | ✗ |
| (**EXP-Err2**) Assignment expression error | Part of expression missing or wrong operator | VA – Assign correct expression | **EXPRESSION_ASSIGNMENT_ERROR** | ✗ |
| | **PROGRAM & ALGORITHM** | | | |
| (**PA-Err1**) Problem decomposition / strategy error | Program omits expected control structures | P/A – Design & decompose algorithm | **PROGRAM_DECOMPOSITION_STRATEGY_ERROR** | ✗ |
| (**PA-Err2**) Requirements misunderstood | Program correct but solves a different task | — | **PROGRAM_REQUIREMENTS_MISUNDERSTOOD** | ✗ |
| (**PA-Err3**) Incomplete program | Correct fragments present but sequence missing | A – Complete instructions | **PROGRAM_INCOMPLETE** | ✗ |
| (**PA-Err4**) Program not optimized | Task done but redundantly (no loops/functions) | P/A – Optimize or adapt algorithm | **PROGRAM_NOT_OPTIMIZED** | ✗ |

These error tags were created as part of an ongoing research project that systematically analyzes novice programming mistakes in a controlled study. The formal paper detailing the methodology and validation of the taxonomy is still in preparation and has not yet been published.

---

## License

This project is licensed under the GNU Affero General Public License v3 (AGPL-3.0). If you wish to use this library for proprietary or commercial purposes, you must obtain a separate license. 

Please contact Badmavasan at [badmavasan.kirouchenassamy@lip6.fr] for commercial licensing inquiries.

---

## Scientific Publication

This library is part of an ongoing scientific study. If you use it for academic purposes, please cite the forthcoming publication:

```
[Publication details will be added here once available.]
```

Stay tuned for updates!
