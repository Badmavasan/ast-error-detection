# This file is part of ast_error_detection.
# Copyright (C) 2025 Badmavasan.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or any later version.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

import ast
from .convert_ast_to_custom_node import ast_to_custom_node
from .error_checks import get_customized_error_tags
from .zang_shasha_distance import distance
from .node import Node
from .error_annotation import ErrorAnnotation


def get_code_errors(code1: str, code2: str):
    """
    Given two Python code snippets, compute their differences as error annotations.

    Args:
        code1 (str): The first (incorrect) code snippet.
        code2 (str): The second (correct) code snippet.

    Returns:
        list: A list of error annotations describing the differences.
    """
    # Parse the AST for both code snippets
    symbolic_code1 = ast.parse(code1)
    symbolic_code2 = ast.parse(code2)

    # Convert AST to custom Node structure
    tree1 = ast_to_custom_node(symbolic_code1)
    tree2 = ast_to_custom_node(symbolic_code2)

    # Ensure both trees have valid roots
    if not tree1 or not tree2:
        raise ValueError("Failed to parse one or both code snippets.")

    # Zhang-Shasha Tree Edit Distance computation
    dist , ops = distance(
        tree1[0],
        tree2[0],
        get_children=Node.get_children,
    )

    # Generate error annotations
    error_annotation = ErrorAnnotation()
    errors = error_annotation.concatenate_all_errors(ops)

    return dist, errors

def get_customized_code_error(code1: str, code2: str):
    dist , errors = get_code_errors(code1, code2)
    customized_error_tags = get_customized_error_tags(errors)
    return dist, customized_error_tags