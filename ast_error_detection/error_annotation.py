# This file is part of ast_error_detection.
# Copyright (C) 2025 Badmavasan.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or any later version.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

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

        return all_errors

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
        deleted_nodes = {(structural_path_element(d['current']).upper(), d['current'])
                         for d in patterns if d['type'] == 'delete'}

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
                if (node_type, insert['new']) not in deleted_nodes:
                    # Determine the missing construct
                    if node_type == "FOR":
                        missing_errors.append(("MISSING_FOR_LOOP", value, context_path))
                    elif node_type == "WHILE":
                        missing_errors.append(("MISSING_WHILE_LOOP", value, context_path))
                    elif node_type == "CALL":
                        missing_errors.append(("MISSING_CALL_INSTRUCTION", value, context_path))
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
        inserted_nodes = {(structural_path_element(i['new']).upper(), i['new'])
                          for i in patterns if i['type'] == 'insert'}

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
                if (node_type, delete['current']) not in inserted_nodes:
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
        incorrect_positions = []

        # Helper function to remove indices from path elements
        def structural_path_element(element):
            return element.split("[")[0]

        # Extract delete and insert nodes
        deleted_nodes = {(structural_path_element(d['current']).upper(), d['current'].upper(), tuple(d['path']))
                         for d in patterns if d['type'] == 'delete'}
        inserted_nodes = {(structural_path_element(i['new']).upper(), i['new'].upper(), tuple(i['path']))
                          for i in patterns if i['type'] == 'insert'}

        # Find overlapping nodes
        for node_type, node_value, delete_path in deleted_nodes:
            for insert_type, insert_value, insert_path in inserted_nodes:
                if node_type == insert_value and node_value == insert_type:
                    # Node exists in both delete and insert, indicating incorrect positioning
                    context_path = " > ".join(structural_path_element(p) for p in delete_path)

                    # Handle cases where ":" is present
                    if ":" in node_value:
                        _, value = node_value.split(":", 1)
                        value = value.strip()
                    else:
                        value = None

                    # Determine the type of incorrect statement positioning
                    if node_type == "FOR":
                        incorrect_positions.append(("INCORRECT_STATEMENT_POSITION_FOR", value, context_path))
                    elif node_type == "WHILE":
                        incorrect_positions.append(("INCORRECT_STATEMENT_POSITION_WHILE", value, context_path))
                    elif node_type == "IF":
                        incorrect_positions.append(("INCORRECT_STATEMENT_POSITION_IF", value, context_path))
                    elif node_type == "CALL":
                        incorrect_positions.append(("INCORRECT_STATEMENT_POSITION_CALL", value, context_path))
                    elif node_type == "ASSIGN":
                        incorrect_positions.append(("INCORRECT_STATEMENT_POSITION_ASSIGN", value, context_path))
                    elif node_type == "FUNCTION":
                        incorrect_positions.append(("INCORRECT_STATEMENT_POSITION_FUNCTION", value, context_path))
                    elif node_type == "RETURN":
                        incorrect_positions.append(("INCORRECT_STATEMENT_POSITION_RETURN", value, context_path))

        return list(set(incorrect_positions))  # Remove duplicates

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

        # Helper function to remove indices from path elements
        def structural_path_element(element):
            return element.split("[")[0]

        # Analyze update operations
        for update in patterns:
            if update['type'] == 'update':
                node_type = structural_path_element(update['path'][-1]).upper()  # Last element of the path
                context_path = " > ".join(structural_path_element(p) for p in update['path'])  # Full path
                current_value = update['current']
                new_value = update['new']

                # Categorize updates
                if "CALL" in node_type:
                    updates.append(("CONSTANT_VALUE_MISMATCH", current_value, new_value, context_path))
                elif "COMPARE" in node_type:  # For conditions
                    updates.append(("INCORRECT_OPERATION_IN_CONDITION", current_value, new_value, context_path))
                elif "OPERATION" in node_type:  # For assignments
                    updates.append(("INCORRECT_OPERATION_IN_ASSIGN", current_value, new_value, context_path))
                elif "CONST" in node_type:
                    updates.append(("CONST_VALUE_MISMATCH", current_value, new_value, context_path))
                elif "ASSIGN" in node_type:
                    updates.append(("NODE_TYPE_MISMATCH", current_value, new_value, context_path))
                elif "VAR" in node_type:
                    # Skip variable updates for now
                    continue

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
                if ":" in pattern['current']:
                    # The space is important here as in the label of the Var node its 'Var: i'
                    cur_node_type, cur_var_value = pattern['current'].split(": ", 1)

                    if ":" in pattern['new']:
                        new_node_type , new_var_value = pattern['new'].split(": ", 1)

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














