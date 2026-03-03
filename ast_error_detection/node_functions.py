# This file is part of ast_error_detection.
# Copyright (C) 2025 Badmavasan Kirouchenassamy & Eva Chouaki.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or any later version.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

def anonymize_variable_names(root):
    """
    Rename every ``Var: <name>`` node in the tree to ``Var: VAR_0``,
    ``Var: VAR_1``, etc., based on the order in which each distinct variable
    name is first encountered during a pre-order traversal.

    This is applied **independently** to the student tree and the correct tree
    before the Zhang-Shasha comparison so that two programs that use different
    variable names for the same structural role (e.g. ``n`` vs ``x``) are not
    penalised for a pure naming difference.  Only genuine structural or value
    differences remain visible to the distance algorithm.

    Handles:
    - ``Var: name``  →  ``Var: VAR_k``
    - ``Var: -name`` →  ``Var: -VAR_k``  (negated variable from UnaryOp)

    Args:
        root (Node): Root of the custom Node tree to anonymize in-place.

    Returns:
        dict: The ``{original_name: anonymous_name}`` mapping that was applied,
              useful for debugging.
    """
    name_map = {}
    counter = [0]

    def traverse(node):
        if node is None:
            return
        if node.label and node.label.startswith("Var: "):
            rest = node.label[5:]                      # everything after "Var: "
            negated = rest.startswith("-")
            var_name = rest[1:] if negated else rest   # strip leading '-' if present
            if var_name not in name_map:
                name_map[var_name] = f"VAR_{counter[0]}"
                counter[0] += 1
            prefix = "-" if negated else ""
            node.label = f"Var: {prefix}{name_map[var_name]}"
        for child in node.children:
            traverse(child)

    traverse(root)
    return name_map


def print_ast_nodes(nodes, indent=0):
    """
    Recursively print the labels of an AST's nodes with indentation.

    This function takes a list of nodes and prints their labels,
    indenting child nodes to visually represent the tree structure.

    Args:
        nodes (list[Node]): A list of nodes (e.g., the root node and its descendants).
        indent (int, optional): The current level of indentation.
                                Each level increases the indentation by four spaces.
                                Defaults to 0.

    Example of output of for i in range(5):\n\tprint("hello") :
    Module
        For
            Condition:
                Var: i
                Call: range
                    Const: 5
            Body:
                Call: print
                    Const: 'hello'
    """
    for node in nodes:
        print('    ' * indent + node.label)
        if node.children:
            print_ast_nodes(node.children, indent + 1)