# This file is part of ast_error_detection.
# Copyright (C) 2025 Badmavasan Kirouchenassamy & Eva Chouaki.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or any later version.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
from ast_error_detection.constants import ANNOTATION_TAG_CONST_VALUE_MISMATCH, \
    ANNOTATION_TAG_INCORRECT_OPERATION_IN_COMP, ANNOTATION_TAG_INCORRECT_OPERATION_IN_ASSIGN, \
    ANNOTATION_CONTEXT_RANGE_FUNCTION_CALL, ANNOTATION_TAG_MISSING_CALL_STATEMENT, \
    ANNOTATION_CONTEXT_CALL_NATIVE_FUNCTION_PRINT, ANNOTATION_TAG_UNNECESSARY_CALL_STATEMENT, \
    ANNOTATION_CONTEXT_FUNCTION_CALL_NODE, F_CALL_UNNECESSARY_PRINT, F_CALL_UNNECESSARY_AVANCER, \
    F_CALL_UNNECESSARY_TOURNER, ANNOTATION_CONTEXT_CALL_NATIVE_FUNCTION_PRINT_NODE_NAME, \
    ANNOTATION_CONTEXT_CALL_NATIVE_FUNCTION_AVANCER_NODE_NAME, ANNOTATION_CONTEXT_CALL_NATIVE_FUNCTION_TOURNER_NODE_NAME
import re

### HIGH LEVEL RULES ##

# Rule: If there is a MISSING_CALL_STATEMENT with context containing "Call: range",
# then remove ALL errors whose context also contains "Call: range".
def rule_remove_all_call_range_if_missing_call_present():
    pattern = re.compile(ANNOTATION_CONTEXT_RANGE_FUNCTION_CALL, re.IGNORECASE)

    def rule(errors):
        # Check if the trigger error is present
        trigger_found = any(
            e[0] == ANNOTATION_TAG_MISSING_CALL_STATEMENT and pattern.search(e[-1])
            for e in errors
        )

        # If trigger found, filter out all errors tied to 'Call: range'
        if trigger_found:
            errors = [e for e in errors if not pattern.search(e[-1])]

        return errors

    return rule


# Rule: If there is an UNNECESSARY_CALL_STATEMENT with context containing "Call: print",
# then remove ALL errors whose context also contains "Call: print".
import re

def rule_remove_all_call_print_if_unnecessary_call_present():
    # Match "Call: print" anywhere in the context
    pattern = re.compile(r"Call:\s*print", re.IGNORECASE)

    def rule(errors):

        # Detect trigger: UNNECESSARY_CALL_STATEMENT on a context that ends with "Call: print"
        trigger_present = any(
            e[0] == ANNOTATION_TAG_UNNECESSARY_CALL_STATEMENT
            and pattern.search(e[-1] or "")
            and (e[-1] or "").strip().endswith("Call: print")
            for e in errors
        )
        if not trigger_present:
            return errors

        filtered = []
        for e in errors:
            code, ctx = e[0], e[-1] or ""

            # Always keep the trigger itself
            if code == ANNOTATION_TAG_UNNECESSARY_CALL_STATEMENT and ctx.strip().endswith("Call: print"):
                filtered.append(e)
                continue

            # Remove other errors if their context contains "Call: print" but continues after it
            if pattern.search(ctx) and not ctx.strip().endswith("Call: print"):
                continue

            filtered.append(e)

        return filtered

    return rule


def high_level_filtering():
    """
    Returns a function that applies a pipeline of rules to an error list.
    Default rules include:
        - Removing all 'Call: range' errors if a MISSING_CALL_STATEMENT
          on 'Call: range' is present.
    """
    rules = [
        rule_remove_all_call_range_if_missing_call_present(),
        rule_remove_all_call_print_if_unnecessary_call_present()
    ]

    def apply_rules(errors):
        for rule in rules:
            errors = rule(errors)
        return errors

    return apply_rules


class ErrorAnnotation:

    def concatenate_all_errors(self, patterns):
        """
        Collect errors from all detection functions and concatenate them into a single list.

        Args:
            patterns (list): A list of dictionaries containing the type of operation,
                             path, current value, and new value for transformations.

        Returns:
            list: A combined list of tuples from all error detection functions.
        """



        # Call individual detection functions
        missing_statements = self.detect_specific_missing_constructs(patterns)
        unnecessary_deletions = self.detect_unnecessary_deletions(patterns)
        incorrect_positions = self.detect_incorrect_statement_positions(patterns)
        updates = self.track_all_updates(patterns)
        variable_mismatches = self.detect_variable_mismatches(patterns)

        # Combine all errors into one list
        all_errors = []
        all_errors.extend(missing_statements)
        all_errors.extend(unnecessary_deletions)
        all_errors.extend(incorrect_positions)
        all_errors.extend(updates)
        all_errors.extend(variable_mismatches)
        # High Level filtering
        error_filter = high_level_filtering()
        filtered = error_filter(all_errors)

        return filtered

    def detect_specific_missing_constructs(self, patterns):
        """
        Detect specific missing constructs in the code based on the nodes that need to be inserted,
        ensuring the node is not marked for removal elsewhere in the patterns.

        The detection focuses on node types like "Assign", "For", "While", "Call", "If", "Function",
        and "Return". Each result includes:
        - The missing construct type.
        - The value (if present) extracted from the node type after a ":".
        - The context (path) where the missing construct occurs.

        Args:
            patterns (list): A list of dictionaries containing the type of operation,
                             path, current value, and new value for transformations.

        Returns:
            list: A list of tuples in the format:
                  (missing_construct, value (or None), context_path)
        """
        missing_errors = []


        # Helper function to remove indices from path elements
        def structural_path_element(element):
            return element.split("[")[0]

        # Extract all delete nodes for comparison
        deleted_nodes = {d['current'] for d in patterns if d['type'] == 'delete'}
        updated_nodes = {u['current'] for u in patterns if u['type'] == 'update'}

        # Analyze insert operations
        for insert in patterns:
            if insert['type'] == 'insert':
                node_type_with_value = structural_path_element(insert['new']).upper()
                context_path = " > ".join(structural_path_element(p) for p in insert['path'])

                # Handle cases where ":" is present
                if ":" in node_type_with_value:
                    node_type, value = node_type_with_value.split(":", 1)
                    node_type = node_type.strip().upper()
                    value = value.strip()
                else:
                    node_type = node_type_with_value
                    value = None

                # Check if the node is also being removed elsewhere
                if insert['new'] not in deleted_nodes and insert['new'] not in updated_nodes:
                    # Determine the missing construct
                    if node_type == "FOR":
                        missing_errors.append(("MISSING_FOR_LOOP", value, context_path))
                    elif node_type == "WHILE":
                        missing_errors.append(("MISSING_WHILE_LOOP", value, context_path))
                    elif node_type == "CALL":
                        missing_errors.append(("MISSING_CALL_STATEMENT", value, context_path))
                    elif node_type == "IF":
                        missing_errors.append(("MISSING_IF_STATEMENT", value, context_path))
                    elif node_type == "ASSIGN":
                        missing_errors.append(("MISSING_ASSIGN_STATEMENT", value, context_path))
                    elif node_type == "FUNCTION":
                        missing_errors.append(("MISSING_FUNCTION_DEFINITION", value, context_path))
                    elif node_type == "RETURN":
                        missing_errors.append(("MISSING_RETURN", value, context_path))
                    elif node_type == "CONST":
                        missing_errors.append(("MISSING_CONST_VALUE", value, context_path))
                    elif node_type == "OPERATION":
                        missing_errors.append(("MISSING_OPERATION", value, context_path))
                    elif node_type == "ARG":
                        missing_errors.append(("MISSING_ARGUMENT", value, context_path))
                    elif node_type == "VAR":
                        missing_errors.append(("MISSING_VARIABLE", value, context_path))

        return list(set(missing_errors))  # Remove duplicates

    def detect_unnecessary_deletions(self, patterns):
        """
        Detect unnecessary deletions in the code based on the nodes that are marked for deletion
        but have no corresponding insert operations for the same type and value.

        The detection groups nodes into broader categories:
        - FOR_LOOP
        - WHILE_LOOP
        - FUNCTION
        - STATEMENT (covers general statements like Assign, Return, Call)
        - CONDITIONAL (covers If statements)

        Each result includes:
        - The unnecessary construct type.
        - The value (if present) extracted from the node type after a ":".
        - The context (path) where the unnecessary deletion occurs.

        Args:
            patterns (list): A list of dictionaries containing the type of operation,
                             path, current value, and new value for transformations.

        Returns:
            list: A list of tuples in the format:
                  (unnecessary_statement, value (or None), context_path)
        """
        unnecessary_errors = []

        # Helper function to remove indices from path elements
        def structural_path_element(element):
            return element.split("[")[0]

        # Extract all insert nodes for comparison
        inserted_nodes = {i['new'] for i in patterns if i['type'] == 'insert'}

        # Analyze delete operations
        for delete in patterns:
            if delete['type'] == 'delete':
                node_type_with_value = structural_path_element(delete['current']).upper()
                context_path = " > ".join(structural_path_element(p) for p in delete['path'])

                # Handle cases where ":" is present
                if ":" in node_type_with_value:
                    node_type, value = node_type_with_value.split(":", 1)
                    node_type = node_type.strip().upper()
                    value = value.strip()
                else:
                    node_type = node_type_with_value
                    value = None

                # Check if the node is also being inserted elsewhere
                if delete['current'] not in inserted_nodes:
                    # Group broader categories
                    if node_type == "FOR":
                        unnecessary_errors.append(("UNNECESSARY_FOR_LOOP", value, context_path))
                    elif node_type == "WHILE":
                        unnecessary_errors.append(("UNNECESSARY_WHILE_LOOP", value, context_path))
                    elif node_type == "FUNCTION":  # Group Function and Return
                        unnecessary_errors.append(("UNNECESSARY_FUNCTION", value, context_path))
                    elif node_type == "RETURN":
                        unnecessary_errors.append(("UNNECESSARY_RETURN_IN_FUNCTION", value, context_path))
                    elif node_type == "IF":  # Group If into Conditional
                        unnecessary_errors.append(("UNNECESSARY_CONDITIONAL", value, context_path))
                    elif node_type == "CALL":
                        unnecessary_errors.append(("UNNECESSARY_CALL_STATEMENT", value, context_path))
                    elif node_type == "ASSIGN":
                        unnecessary_errors.append(("UNNECESSARY_ASSIGN_STATEMENT", value, context_path))
                    elif node_type == "CONST":
                        unnecessary_errors.append(("UNNECESSARY_CONST_VALUE", value, context_path))
                    elif node_type == "OPERATION":
                        unnecessary_errors.append(("UNNECESSARY_OPERATION", value, context_path))
                    elif node_type == "ARG":
                        unnecessary_errors.append(("UNNECESSARY_ARGUMENT", value, context_path))
                    elif node_type == "VAR":
                        unnecessary_errors.append(("UNNECESSARY_VAR", value, context_path))

        return list(set(unnecessary_errors))  # Remove duplicates

    def detect_incorrect_statement_positions(self, patterns):
        """
        Detect nodes that are both deleted and inserted elsewhere, indicating incorrect statement positioning.

        The detection focuses on node types like "Assign", "For", "While", "Call", "If", "Function",
        and "Return". Each result includes:
        - The incorrect statement position type.
        - The value (if present) extracted from the node type after a ":".
        - The context (path) where the incorrect positioning occurs.

        Args:
            patterns (list): A list of dictionaries containing the type of operation,
                             path, current value, and new value for transformations.

        Returns:
            list: A list of tuples in the format:
                  (incorrect_statement_position, value (or None), context_path)
        """

        # Helper function to remove indices from path elements
        def structural_path_element(element):
            return element.split("[")[0]

        # Extract delete and insert nodes
        deleted_nodes = {(structural_path_element(d['current']).upper(), d['current'].upper(), tuple(d['path']))
                         for d in patterns if d['type'] == 'delete'}
        inserted_nodes = {(structural_path_element(i['new']).upper(), i['new'].upper(), tuple(i['path']))
                          for i in patterns if i['type'] == 'insert'}

        incorrect_positions = []
        kind_to_code = {
            "FOR": "INCORRECT_STATEMENT_POSITION_FOR",
            "WHILE": "INCORRECT_STATEMENT_POSITION_WHILE",
            "IF": "INCORRECT_STATEMENT_POSITION_IF",
            "CALL": "INCORRECT_STATEMENT_POSITION_CALL",
            "ASSIGN": "INCORRECT_STATEMENT_POSITION_ASSIGN",
            "FUNCTION": "INCORRECT_STATEMENT_POSITION_FUNCTION",
            "RETURN": "INCORRECT_STATEMENT_POSITION_RETURN",
        }

        for del_type, del_value, del_path in deleted_nodes:
            for ins_type, ins_value, ins_path in inserted_nodes:
                # Compare like with like
                if del_type == ins_type and del_value == ins_value:
                    # Build context from the *deleted* path (as you had)
                    context_path = " > ".join(structural_path_element(p) for p in del_path)

                    # Extract base kind (e.g., "CALL" from "CALL: PRINT")
                    base_kind = del_type.split(":", 1)[0].strip().upper()

                    # Extract human-readable value if present (e.g., "PRINT" or "'Finished ...'")
                    value = None
                    if ":" in del_value:
                        value = del_value.split(":", 1)[1].strip()

                    code = kind_to_code.get(base_kind)
                    if code:
                        incorrect_positions.append((code, value, " > ".join(structural_path_element(p) for p in ins_path)))

        # Remove duplicates
        return list(set(incorrect_positions))

    def track_all_updates(self, patterns):
        """
        Track all updates in the code and categorize them based on the node type and context.

        The detection focuses on:
        - "Call" nodes → Constant Value Mismatch
        - Comparison operations → Incorrect Operation in Condition
        - Assignment operations → Incorrect Operation in Assign
        - Loop conditions (For/While) → Incorrect Number of Iterations
        - Variable updates → Ignored for now

        Args:
            patterns (list): A list of dictionaries containing the type of operation,
                             path, current value, and new value for transformations.

        Returns:
            list: A list of tuples in the format:
                  (update_category, current_value, new_value, context_path)
        """
        updates = []

        def _node_kind(label):
            base = (label or "").split("[")[0]
            return base.split(":", 1)[0].strip().upper()

        # Helper function to remove indices from path elements
        def structural_path_element(element):
            return element.split("[")[0]

        call_token = re.compile(ANNOTATION_CONTEXT_FUNCTION_CALL_NODE, re.IGNORECASE)

        _unnecessary_map = {
            "FOR": "UNNECESSARY_FOR_LOOP",
            "WHILE": "UNNECESSARY_WHILE_LOOP",
            "IF": "UNNECESSARY_IF_STATEMENT",
            "CALL": ANNOTATION_TAG_UNNECESSARY_CALL_STATEMENT,  # keep your existing constant
            "ASSIGN": "UNNECESSARY_ASSIGN_STATEMENT",
            "FUNCTIONDEF": "UNNECESSARY_FUNCTION_DEFINITION",
            "RETURN": "UNNECESSARY_RETURN",
            "CONST": "UNNECESSARY_CONST_VALUE",
            "OPERATION": "UNNECESSARY_OPERATION",
            "ARGUMENT": "UNNECESSARY_ARGUMENT",
            "VAR": "UNNECESSARY_VARIABLE",
        }


        # Analyze update operations
        for update in patterns:
            if update['type'] == 'update':
                path = update['path']
                node_type = structural_path_element(path[-1]).upper()
                context_path = " > ".join(structural_path_element(p) for p in path)
                current_value = update['current']
                new_value = update['new']

                # Extract callee names if both sides are calls
                m_current = call_token.search(current_value)


                cur_kind = _node_kind(current_value)
                new_kind = _node_kind(new_value)

                if cur_kind in _unnecessary_map and new_kind and new_kind != cur_kind:
                    # Avoid double-adding for CALL when we already handled above.
                    if not (cur_kind == "CALL" and (m_current is not None)):
                        updates.append((_unnecessary_map[cur_kind], current_value, new_value, context_path))

                # Handle "missing construct" cases based on the new node type
                if new_value in (
                "For", "While", "If", "Call", "Assign", "FunctionDef", "Return", "Const", "Operation", "Argument",
                "Var"):
                    missing_map = {
                        "For": "MISSING_FOR_LOOP",
                        "While": "MISSING_WHILE_LOOP",
                        "If": "MISSING_IF_STATEMENT",
                        "Call": "MISSING_CALL_STATEMENT",
                        "Assign": "MISSING_ASSIGN_STATEMENT",
                        "Const": "MISSING_CONST_VALUE",
                        "Operation": "MISSING_OPERATION",
                        "Var": "MISSING_VARIABLE",
                    }
                    updates.append((missing_map[new_value], current_value, new_value, context_path))


                if "COMPARE" in node_type:
                    updates.append((ANNOTATION_TAG_INCORRECT_OPERATION_IN_COMP, current_value, new_value, context_path))
                elif "OPERATION" in node_type:
                    updates.append((ANNOTATION_TAG_INCORRECT_OPERATION_IN_ASSIGN, current_value, new_value, context_path))
                elif "CONST" in node_type:
                    updates.append((ANNOTATION_TAG_CONST_VALUE_MISMATCH, current_value, new_value, context_path))
                elif "ASSIGN" in node_type:
                    updates.append(("NODE_TYPE_MISMATCH", current_value, new_value, context_path))
                elif "VAR" in node_type:
                    continue  # Skip variable changes for now

        return updates

    def detect_variable_mismatches(self, patterns):
        """
        Detect updates involving variables (Var) and check for consistency in their values.

        If the value of a variable changes in any of the update operations, it is flagged as a mismatch.

        Args:
            patterns (list): A list of dictionaries containing the type of operation,
                             path, current value, and new value for transformations.

        Returns:
            list: A list of tuples in the format:
                  ("VARIABLE_MISMATCH", variable_name, context_path)
        """
        variable_updates = {}

        # Helper function to remove indices from path elements
        def structural_path_element(element):
            return element.split("[")[0]

        # Collect all updates involving variables
        for pattern in patterns:
            if pattern['type'] == 'update':

                # Handle cases where ":" is present
                if ": " in pattern['current']:
                    # The space is important here as in the label of the Var node its 'Var: i'
                    cur_node_type, cur_var_value = pattern['current'].split(": ", 1)

                    if ": " in pattern['new']:
                        new_node_type, new_var_value = pattern['new'].split(": ", 1)

                        # Check if the last element is a Var node
                        if cur_node_type.upper() == "VAR" and new_node_type.upper() == "VAR":
                            context_path = " > ".join(structural_path_element(p) for p in pattern['path'])

                            # Track the variable updates
                            if cur_var_value not in variable_updates:
                                variable_updates[cur_var_value] = {'values': set(), 'context_paths': set()}

                            variable_updates[cur_var_value]['values'].add(new_var_value)
                            variable_updates[cur_var_value]['context_paths'].add(context_path)

        # Check for inconsistencies
        mismatches = []
        for var_name, details in variable_updates.items():
            if len(details['values']) > 1:  # Inconsistent updates
                for context_path in details['context_paths']:
                    mismatches.append(("VARIABLE_MISMATCH", var_name, context_path))

        return mismatches



