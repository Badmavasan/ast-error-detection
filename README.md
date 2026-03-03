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

---

## Internal Architecture & Implementation Reference

This section documents the internal mechanics of both annotation layers in detail. It is intended as a persistent reference for future development and context recovery.

### File Map

| File | Role |
|---|---|
| `node.py` | Custom tree `Node` class: label, children, parent, index, `get_path()` |
| `annotated_tree.py` | Zhang-Shasha annotated tree: post-order, LMD, keyroots, `nodes_path` |
| `convert_ast_to_custom_node.py` | Converts Python `ast` nodes → custom `Node` trees |
| `node_functions.py` | Tree utilities: `anonymize_variable_names`, `print_ast_nodes` |
| `zang_shasha_distance.py` | Core Zhang-Shasha algorithm; returns `(dist, ops)` where ops is a list of `{type, path, current, new}` dicts |
| `error_annotation.py` | **Layer 1** — produces primary errors from edit ops |
| `error_checks.py` | **Layer 2** — maps primary errors to typed error code strings |
| `error_diagnosis.py` | Entry points: `get_primary_code_errors`, `get_typology_based_code_error` |
| `constants.py` | All tag strings and regex context constants |

### Variable Anonymization (`node_functions.anonymize_variable_names`)

Applied in `get_primary_code_errors()` **after tree construction, before distance computation**.

**Why it is needed:** Two programs that solve the same problem but use different variable names (e.g. student uses `n`, correct solution uses `x`) would otherwise produce spurious `UNNECESSARY_VARIABLE` update operations for every single occurrence of those variables, drowning out the real errors.

**Algorithm:** Pre-order traversal of each tree. The first distinct variable name encountered is mapped to `VAR_0`, the second to `VAR_1`, and so on. The mapping is applied independently to each tree.

```
student:  n = 9; for k in range(4): avancer(n) ...
          ↓ anonymize (n→VAR_0, k→VAR_1)
          VAR_0 = 9; for VAR_1 in range(4): avancer(VAR_0) ...

correct:  x = 9; for k in range(5): avancer(x) ...
          ↓ anonymize (x→VAR_0, k→VAR_1)
          VAR_0 = 9; for VAR_1 in range(5): avancer(VAR_0) ...
```

After anonymization the only remaining difference is `Const: 4` vs `Const: 5` → `LO_FOR_NUMBER_ITERATION_ERROR_UNDER2`. No variable errors are produced.

**Handles:** `Var: name` and `Var: -name` (negated variable from `UnaryOp`). Does **not** anonymize `Arg:` (function parameter) or `Const:` nodes — only `Var:` nodes.

**Limitation — ordering sensitivity:** If two programs declare variables in a different order, the anonymous indices differ and a mismatch is still reported. This is intentional: declaration order is itself a structural property of the program.

### AST → Custom Node Mapping

| Python AST node | Custom Node label | Notes |
|---|---|---|
| `ast.Module` | `"Module"` | |
| `ast.For` | `"For"` | Children: `"Condition:"` (with loop var + iter), `"Body:"` |
| `ast.While` / `ast.If` | `"While"` / `"If"` | Children: `"Condition:"`, `"Body:"`, optional `"Else:"` |
| `ast.Assign` | `"Assign"` | Children: `Var: <name>` + value node(s) |
| `ast.BinOp` / `ast.AugAssign` | `"Operation: <op>"` | op in `{+, -, *, /, //, **, %}` |
| `ast.Compare` | `"Compare: <op>"` | e.g. `"Compare: <"` |
| `ast.Call` | `"Call: <func_name>"` | Arguments are children |
| `ast.Constant` | `"Const: <value>"` | Strings quoted: `"Const: 'hello'"` |
| `ast.Name` | `"Var: <name>"` | |
| `ast.FunctionDef` | `"Function: <name>"` | |
| `ast.Return` | `"Return"` | Value nodes as children |
| `ast.arg` | `"Arg: <name>"` | |
| `ast.UnaryOp` (USub) | `"Const: -<val>"` or `"Var: -<name>"` | |

`node.get_path()` returns the full root-to-self path list, e.g. `['Module', 'For[0]', 'Body:[1]', 'Call: print[0]', 'Operation: +[0]']`. The `[index]` suffix is added for every non-root node.

### Zhang-Shasha Edit Operations Format

Each op is a dict:
```python
{'type': 'insert',  'path': [...],  'current': None,       'new': 'Call: print'}
{'type': 'delete',  'path': [...],  'current': 'Const: 1', 'new': None}
{'type': 'update',  'path': [...],  'current': 'Const: 9', 'new': 'Const: 10'}
{'type': 'match',   'path': [...],  'current': 'For',      'new': 'For'}
```
`path` = `node.get_path()` (includes the node itself as the last element).

---

### Layer 1 — Primary Error Detection (`error_annotation.py`)

Called via `ErrorAnnotation().concatenate_all_errors(ops)`. Runs 5 detectors then applies high-level filtering.

#### Detector 1 — `detect_specific_missing_constructs` → MISSING_* tags

**Trigger:** `insert` operation whose node is NOT also being deleted or updated elsewhere (truly absent, not moved).

| Node type in `insert['new']` | Tag |
|---|---|
| `FOR` | `MISSING_FOR_LOOP` |
| `WHILE` | `MISSING_WHILE_LOOP` |
| `CALL` | `MISSING_CALL_STATEMENT` |
| `IF` | `MISSING_IF_STATEMENT` |
| `ASSIGN` | `MISSING_ASSIGN_STATEMENT` |
| `FUNCTION` | `MISSING_FUNCTION_DEFINITION` |
| `RETURN` | `MISSING_RETURN` |
| `CONST` | `MISSING_CONST_VALUE` |
| `OPERATION` | `MISSING_OPERATION` |
| `ARG` | `MISSING_ARGUMENT` |
| `VAR` | `MISSING_VARIABLE` |

Output: `(tag, insert['new'], context_path)` where `context_path = " > ".join(insert['path'])`.

#### Detector 2 — `detect_unnecessary_deletions` → UNNECESSARY_* tags

**Trigger:** `delete` operation whose node is NOT also being inserted elsewhere (truly redundant, not moved).

| Node type in `delete['current']` | Tag |
|---|---|
| `FOR` | `UNNECESSARY_FOR_LOOP` |
| `WHILE` | `UNNECESSARY_WHILE_LOOP` |
| `FUNCTION` | `UNNECESSARY_FUNCTION` |
| `RETURN` | `UNNECESSARY_RETURN_IN_FUNCTION` |
| `IF` | `UNNECESSARY_CONDITIONAL` |
| `CALL` | `UNNECESSARY_CALL_STATEMENT` |
| `ASSIGN` | `UNNECESSARY_ASSIGN_STATEMENT` |
| `CONST` | `UNNECESSARY_CONST_VALUE` |
| `OPERATION` | `UNNECESSARY_OPERATION` |
| `ARG` | `UNNECESSARY_ARGUMENT` |
| `VAR` | `UNNECESSARY_VAR` |

Output: `(tag, value_after_colon_or_None, context_path)` where `context_path = " > ".join(delete['path'])`.

> **Important:** `delete['path']` INCLUDES the deleted node itself as the last path element. So context_path for an `Operation: +` node will end with `"... > Operation: +[0]"`.

#### Detector 3 — `detect_incorrect_statement_positions` → INCORRECT_STATEMENT_POSITION_* tags

**Trigger:** A node is deleted from location A AND a node of the same kind+label is inserted at location B. The node was moved/misplaced. Context points to the TARGET (insert) location.

| Kind | Tag |
|---|---|
| `FOR` | `INCORRECT_STATEMENT_POSITION_FOR` |
| `WHILE` | `INCORRECT_STATEMENT_POSITION_WHILE` |
| `IF` | `INCORRECT_STATEMENT_POSITION_IF` |
| `CALL` | `INCORRECT_STATEMENT_POSITION_CALL` |
| `ASSIGN` | `INCORRECT_STATEMENT_POSITION_ASSIGN` |
| `FUNCTION` | `INCORRECT_STATEMENT_POSITION_FUNCTION` |
| `RETURN` | `INCORRECT_STATEMENT_POSITION_RETURN` |

Output: `(tag, value_or_None, context_path)`.

#### Detector 4 — `track_all_updates` → UPDATE tags

**Trigger:** `update` operations (node label changed). Categorized by the updated node's type (last element of path):

| Updated node type | Tag | Format |
|---|---|---|
| `CONST` | `CONST_VALUE_MISMATCH` | 4-tuple: `(tag, current, new, context)` |
| `COMPARE` | `INCORRECT_OPERATION_IN_CONDITION` | 4-tuple |
| `OPERATION` | `INCORRECT_OPERATION_IN_ASSIGN` | 4-tuple |
| `ASSIGN` | `NODE_TYPE_MISMATCH` | 4-tuple |
| `VAR` | skipped | — |

Also handles node-TYPE replacements (e.g. `FOR` replaced by `WHILE` in update): emits `UNNECESSARY_<old>` + `MISSING_<new>`.

#### Detector 5 — `detect_variable_mismatches` → VARIABLE_MISMATCH

**Trigger:** A `Var` node is updated to different target names at different locations.

Output: `("VARIABLE_MISMATCH", var_name, context_path)`.

#### High-Level Filtering Rules

Applied after all detectors. Each rule suppresses child-context noise when a higher-level structural error is present:

| Trigger tag | Suppresses |
|---|---|
| `UNNECESSARY_CALL_STATEMENT` at context C | All errors with context starting `C > ` |
| `UNNECESSARY_FOR_LOOP` or `UNNECESSARY_WHILE_LOOP` at context C | All errors with context starting `C > ` |
| `MISSING_CALL_STATEMENT` at context C | All errors with context starting `C > ` |
| `MISSING_FOR_LOOP` at context C | All errors with context starting `C > ` |

---

### Layer 2 — Typology Error Detection (`error_checks.py`)

`get_customized_error_tags(input_list)` → `set` of error tag strings.

Input: list of 3-tuples `(tag, value, context)` or 4-tuples `(tag, current, new, context)`.

#### Pre-processing: Assignment presence/absence

`process_tag_triplets()` checks if all tags in a required set are simultaneously present with the same context segment. Used for:
- `EXP_ERROR_ASSIGNMENT_MISSING`: requires `{MISSING_CONST_VALUE, MISSING_ASSIGN_STATEMENT, MISSING_VARIABLE}` same context
- `EXP_ERROR_ASSIGNMENT_UNNECESSARY`: requires `{UNNECESSARY_CONST_VALUE, UNNECESSARY_ASSIGN_STATEMENT, UNNECESSARY_VAR}` same context

#### Rule: `EXP_ERROR_OPERANDS`
The operation expression **exists** in the student code, but there is a problem with its **operands** (the values or sub-expressions being operated on). Also covers cases where an entire operation is extra or missing, since the net effect is a wrong operand being evaluated. The **operator type** is NOT the issue here.
- **Case 1** (wrong constant operand): `tag == CONST_VALUE_MISMATCH` AND context matches `r"Operation:.*"` → operation present in both trees but a constant operand has the wrong value (e.g. `k+2` vs `k+1`)
- **Case 2** (extra operation): `tag == UNNECESSARY_OPERATION` AND `"Assign"` NOT in context → student wrote an entire operation that should not be there (e.g. `print(k+1)` vs `print(k)`)
- **Case 3** (missing operation): `tag == MISSING_OPERATION` AND `"Assign"` NOT in context → student is missing an entire operation (e.g. `print(k)` vs `print(k+1)`)
- Guard: Cases 2 and 3 inside `"Assign"` context are handled by `VA_EXPRESSION_ASSIGNMENT_TO_VARIABLE_ERROR` instead.

#### Rule: `EXP_ERROR_OPERATOR`
The operation expression **exists** in both student and correct code, but the **operator type** is wrong (e.g. student wrote `k-1` but should have written `k+1`):
- `tag == INCORRECT_OPERATION_IN_ASSIGN` AND `"Assign"` NOT in context → the Operation node label changed between trees (operator type replaced), outside an assignment scope
- Guard: inside `"Assign"` context, `VA_EXPRESSION_ASSIGNMENT_TO_VARIABLE_ERROR` covers operator-type errors at the assignment level.

#### Rule: `EXP_ERROR_OPERATION` (umbrella)
Fires alongside both `EXP_ERROR_OPERANDS` and `EXP_ERROR_OPERATOR` — emitted on **every** case where an existing operation expression does not match what is expected, regardless of whether the problem is with the operands or the operator. Useful when only a coarse-grained signal is needed.

> **Distinction from assignment errors:** `EXP_ERROR_OPERATION`, `EXP_ERROR_OPERANDS`, and `EXP_ERROR_OPERATOR` all imply the operation **expression is structurally present**. The assignment-level errors (`EXP_ERROR_ASSIGNMENT_MISSING`, `EXP_ERROR_ASSIGNMENT_UNNECESSARY`, `EXP_ERROR_ASSIGNMENT_MISPLACED`) are about the **entire assignment expression** being absent, extra, or in the wrong place.

#### Rule: `EXP_ERROR_ASSIGNMENT_MISPLACED`
- `tag == INCORRECT_STATEMENT_POSITION_ASSIGN`

#### Rule: `EXP_ERROR_CONDITIONAL_BRANCH`
- `tag == INCORRECT_OPERATION_IN_CONDITION` AND `"If > Condition"` in context

#### Rule: `VA_DECLARATION_INITIALIZATION_ERROR`
- `tag == CONST_VALUE_MISMATCH` AND context matches `r".*Assign\s>\sConst:\s\d+$"` (variable assigned wrong numeric literal)

#### Rule: `VA_EXPRESSION_ASSIGNMENT_TO_VARIABLE_ERROR`
Right-hand side expression of an assignment is wrong:
- `tag == INCORRECT_OPERATION_IN_ASSIGN` AND `"Assign"` in context
- `tag == MISSING_OPERATION` AND `"Assign"` in context AND `MISSING_ASSIGN_STATEMENT` not in all primary tags
- `tag == UNNECESSARY_OPERATION` AND `"Assign"` in context AND `UNNECESSARY_ASSIGN_STATEMENT` not in all primary tags

#### Rule: `LO_FOR_NUMBER_ITERATION_ERROR` / `LO_FOR_NUMBER_ITERATION_ERROR_UNDER2`
- `tag == CONST_VALUE_MISMATCH` AND `"For > Condition: > Call: range > Const"` in context
- Extract integers from context (student) and context2 (correct); `|diff| > 1` → `LO_FOR_NUMBER_ITERATION_ERROR`, `|diff| == 1` → `UNDER2`

#### Rule: `LO_WHILE_NUMBER_ITERATION_ERROR` / `LO_WHILE_NUMBER_ITERATION_ERROR_UNDER2`
- `tag == CONST_VALUE_MISMATCH` AND `"While > Condition: > Compare"` in context; same diff rule

#### Rule: `LO_FOR_MISSING` / `LO_WHILE_MISSING`
- `tag == MISSING_FOR_LOOP` / `tag == MISSING_WHILE_LOOP`

#### Rule: `LO_FOR_UNNECESSARY` / `LO_WHILE_UNNECESSARY`
- `tag == UNNECESSARY_FOR_LOOP` AND (context matches `r".*For$"` OR context2 ends with `"For"`)
- `tag == UNNECESSARY_WHILE_LOOP` AND (context matches `r".*While$"` OR context2 ends with `"While"`)

#### Rule: `LO_FOR_MISPLACED`
- `tag == INCORRECT_STATEMENT_POSITION_FOR`

#### Rule: `LO_BODY_MISSING_NOT_PRESENT_ANYWHERE`
- Any `MISSING_*` tag AND (`"For > Body"` OR `"While > Body"`) in context

#### Rule: `LO_BODY_MISPLACED`
- Any `INCORRECT_STATEMENT_POSITION` tag AND `"For > Body"` in context

#### Rule: `LO_BODY_ERROR`
Any of these (tag + context) combinations:
- `MISSING_CONST_VALUE` + `"For > Body"`
- `MISSING_CALL_STATEMENT` + `"For > Body"`
- `UNNECESSARY_CALL_STATEMENT` + `"For > Body"`
- `CONST_VALUE_MISMATCH` + `"While > Body"`
- `INCORRECT_STATEMENT_POSITION_ASSIGN` + `"For > Body"`

#### Rule: `LO_CONDITION_ERROR`
- `tag == INCORRECT_OPERATION_IN_CONDITION` AND `"While > Condition"` in context

#### Rule: `F_CALL_MISSING` / `F_CALL_MISSING_<NAME>`
- `tag == MISSING_CALL_STATEMENT`
- Identify function name from context2's last word
- Known names → specific tags: `F_CALL_MISSING_PRINT`, `F_CALL_MISSING_AVANCER`, `F_CALL_MISSING_TOURNER`, `F_CALL_MISSING_COULEUR`, `F_CALL_MISSING_ARC`, `F_CALL_MISSING_GAUCHE`, `F_CALL_MISSING_HAUT`, `F_CALL_MISSING_BAS`, `F_CALL_MISSING_DROITE`, `F_CALL_MISSING_POSER`, `F_CALL_MISSING_LEVER`
- Unknown → `F_CALL_MISSING`

#### Rule: `F_CALL_UNNECESSARY` / `F_CALL_UNNECESSARY_<NAME>`
- `tag == UNNECESSARY_CALL_STATEMENT`
- Identified by context2 last word OR context regex; same known-name list

#### Rule: `F_CALL_PRINT_ERROR_ARG`
Error inside `print`'s argument list:
- `tag != UNNECESSARY_CALL_STATEMENT` AND context matches `r"Call:\s*print > .*"` (wrong/extra element inside print args)
- `tag in {MISSING_CONST_VALUE, MISSING_VARIABLE, MISSING_ARGUMENT, MISSING_OPERATION}` AND context matches `r"Call:\s*print"` (missing element inside print)

#### Rule: `F_CALL_<NAME>_ERROR` (design + robot functions)
- Design (avancer, tourner, couleur, arc): `tag not in [VARIABLE_MISMATCH]` AND context matches `r"Call:\s*<name> > .*"`
- Robot (gauche, haut, bas, droite, lever, poser): same rule with respective names

#### Rule: `F_CALL_INCORRECT_POSITION_<NAME>`
- `tag == INCORRECT_STATEMENT_POSITION_CALL` AND context matches `r"Call:\s*<name>"` for each known function

#### Rule: `F_DEFINITION_MISSING` / `F_DEFINITION_UNNECESSARY`
- `tag == MISSING_FUNCTION_DEFINITION` → `F_DEFINITION_MISSING`
- `tag == UNNECESSARY_FUNCTION` → `F_DEFINITION_UNNECESSARY`

#### Rule: `F_DEFINITION_ERROR_RETURN`
- `tag == MISSING_RETURN`
- `tag == UNNECESSARY_RETURN_IN_FUNCTION`
- `tag == MISSING_VARIABLE` AND `"Function"` in context AND `"Return > Tuple"` in context

#### Rule: `CS_MISSING`
- `tag == MISSING_IF_STATEMENT`

#### Rule: `CS_BODY_ERROR`
- Any `MISSING_*` tag AND `"If > Body"` in context

#### Rule: `CS_BODY_MISPLACED`
- `tag == INCORRECT_STATEMENT_POSITION_IF`

---

### Context Path Format

Context paths are `" > "`-separated strings. The node itself is included as the last element.

```
"Module > For > Body: > Call: print"
"Module > For > Condition: > Call: range > Const: 10"
"Module > For > Body: > Call: print > Operation: +"
"Module > Assign > Const: 5"
```

When the path comes from `detect_unnecessary_deletions` / `detect_specific_missing_constructs`, index suffixes like `[0]` are present. `structural_path_element()` strips them for display.

---

### Exception Tag Lists (constants.py)

```python
EXP_ERROR_OPERATION_EXCEPTION_ANNOTATION_TAGS     = [VARIABLE_MISMATCH]
F_CALL_PRINT_ERROR_ARG_EXCEPTION_ANNOTATION_TAGS  = [VARIABLE_MISMATCH, UNNECESSARY_CALL_STATEMENT]
F_CALL_DESIGN_ERROR_ARG_EXCEPTION_ANNOTATION_TAGS = [VARIABLE_MISMATCH]
F_CALL_ROBOT_ERROR_ARG_EXCEPTION_ANNOTATION_TAGS  = [VARIABLE_MISMATCH]
```

---

### Changelog

#### Fix — `EXP_ERROR_OPERATION` not detected for `print(k+1)` vs `print(k)` (2026-03)
**Root cause:** The original rule only fired for `CONST_VALUE_MISMATCH + "Operation:" in context`, which handles the case where the operator is wrong inside an existing operation (e.g. `k+2` vs `k+1` → Const update). When the operation is entirely extra (`UNNECESSARY_OPERATION`) or entirely missing (`MISSING_OPERATION`), the tag never matched.

**Fix (then refactored into split below):** Added handling for `UNNECESSARY_OPERATION` and `MISSING_OPERATION` tags. The Assign guard prevents double-reporting with `VA_EXPRESSION_ASSIGNMENT_TO_VARIABLE_ERROR`.

#### Refactor — Split `EXP_ERROR_OPERATION` into `EXP_ERROR_OPERANDS` + `EXP_ERROR_OPERATOR` (2026-03)
**Motivation:** `EXP_ERROR_OPERATION` conflated two distinct error kinds — wrong operand values vs wrong operator type. The split makes the distinction precise and actionable.

| Old tag | New tag | When |
|---|---|---|
| `EXP_ERROR_OPERATION` (Case 1) | `EXP_ERROR_OPERANDS` | `CONST_VALUE_MISMATCH` inside an Operation context |
| `EXP_ERROR_OPERATION` (Case 2) | `EXP_ERROR_OPERANDS` | `UNNECESSARY_OPERATION` outside Assign |
| `EXP_ERROR_OPERATION` (Case 3) | `EXP_ERROR_OPERANDS` | `MISSING_OPERATION` outside Assign |
| *(new)* | `EXP_ERROR_OPERATOR` | `INCORRECT_OPERATION_IN_ASSIGN` outside Assign |

`EXP_ERROR_OPERATION` constant is kept in `constants.py` as deprecated. `EXP_ERROR_OPERANDS` and `EXP_ERROR_OPERATOR` are the canonical replacements.

**Semantic contract:**
- All three errors imply the operation expression **structurally exists** in the student code.
- `EXP_ERROR_OPERATION` = umbrella — fires on every operation error (operands OR operator wrong).
- `EXP_ERROR_OPERANDS` = right operator, wrong values/variables being combined.
- `EXP_ERROR_OPERATOR` = right operands, wrong operator type (+ vs -, etc.).
- Assignment-level errors (`EXP_ERROR_ASSIGNMENT_*`) = expression wholly absent / extra / misplaced.
- `EXP_ERROR_OPERATION` always co-fires with whichever specific tag applies.

#### Fix — Spurious `UNNECESSARY_VARIABLE` errors from variable-name differences (2026-03)
**Root cause:** When comparing two programs that use different variable names for the same structural role (e.g. `n` in student code vs `x` in correct code), Zhang-Shasha aligned `Var: n` with `Var: x` and produced one `UNNECESSARY_VARIABLE` update per occurrence of the variable — masking the real errors.

**Fix — Variable anonymization (`node_functions.anonymize_variable_names`):**
Before the Zhang-Shasha distance call, each tree is independently traversed in pre-order and every `Var: <name>` node is renamed to `Var: VAR_k` where `k` is the order of first encounter. Both `Var: name` and `Var: -name` (negated variable) are handled.

```
code1  n=9; for k in range(4): avancer(n) ...
       → after anonymization → VAR_0=9; for VAR_1 in range(4): avancer(VAR_0) ...

code2  x=9; for k in range(5): avancer(x) ...
       → after anonymization → VAR_0=9; for VAR_1 in range(5): avancer(VAR_0) ...
```

The only remaining difference is `Const: 4` vs `Const: 5` → `LO_FOR_NUMBER_ITERATION_ERROR_UNDER2`.

**Why independent anonymization works:** Variables that play the same structural role appear in the same position in both programs, so they receive the same anonymous index. Genuine structural variable mismatches (e.g. a program that uses two variables where only one is expected) still produce differences after anonymization.

**Location:** `node_functions.anonymize_variable_names(root)` called in `error_diagnosis.get_primary_code_errors()` after tree construction, before `distance()`.
