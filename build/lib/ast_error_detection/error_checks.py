from ast_error_detection.constants import FOR_LOOP_INCORRECT_NUMBER_OF_ITERATIONS, FOR_LOOP_MISSING, \
    FOR_LOOP_BODY_MISMATCH, MISSING_STATEMENT, ERROR_VALUE_PARAMETER, ANNOTATION_TAG_CONST_VALUE_MISMATCH, \
    ANNOTATION_TAG_MISSING_FOR_LOOP, ANNOTATION_CONTEXT_FOR_LOOP_BODY, ANNOTATION_TGA_MISSING, \
    ANNOTATION_CONTEXT_FUNCTION_PARAMETER

import re


def get_customized_error_tags(input_list):
    """
    Analyzes a list of error details for specific tag and context patterns,
    returning a list of error code strings based on the following rules.

    Each element in the input list should be a list of either 3 or 4 elements.
    The first element is treated as the error tag and the last element as the error context.

    Rules:
        1. If the tag is "CONST_VALUE_MISMATCH" and the context contains
           "For > Condition: > Call: rang > Const", then add:
               "FOR_LOOP_INCORRECT_NUMBER_OF_ITERATIONS"
           (Indicates a constant value mismatch in a for loop's condition.)

        2. If the tag exactly matches "MISSING_FOR_LOOP", then add:
               "MISSING_FOR_LOOP"
           (Indicates that a for loop is missing where expected.)

        3. If the context contains "Module > For > Body" (anywhere in the context),
           then add:
               "FOR_LOOP_BODY_MISMATCH"
           (Indicates that the body of a for loop does not match the expected structure.)

        4. If the tag contains the substring "MISSING", then add:
               "MISSING_STATEMENT"
           (Indicates that a required statement is missing.)

        5. If the tag is "CONST_VALUE_MISMATCH" and the context ends with a pattern matching
           "Call: <any_text> > Const: <any_text>", then add:
               "ERROR_VALUE_PARAMETER"
           (Indicates that there is an error in the value parameter of a call.)

    Note: The context matching does not require an exact match; it is sufficient for the
    context string to contain the specified substrings or patterns.

    Args:
        input_list (list): A list of error detail lists. Each error detail list must contain
                           3 or 4 elements. The first element is the error tag and the last
                           element is the context.

    Returns:
        list: A list of error code strings that match the conditions. If no conditions match,
              an empty list is returned.
    """
    error_list = []
    pattern_value_parameter = re.compile(ANNOTATION_CONTEXT_FUNCTION_PARAMETER)

    for error_details in input_list:
        # Ensure the error detail has the expected number of elements; if not, skip it.
        if len(error_details) not in (3, 4):
            continue

        tag = error_details[0]
        context = error_details[-1]

        # Rule 1: CONST_VALUE_MISMATCH with specific context substring.
        if tag == ANNOTATION_TAG_CONST_VALUE_MISMATCH and "For > Condition: > Call: rang > Const" in context:
            error_list.append(FOR_LOOP_INCORRECT_NUMBER_OF_ITERATIONS)

        # Rule 2: Tag exactly matches MISSING_FOR_LOOP.
        if tag == ANNOTATION_TAG_MISSING_FOR_LOOP:
            error_list.append(FOR_LOOP_MISSING)

        # Rule 3: Context contains "Module > For > Body".
        if ANNOTATION_CONTEXT_FOR_LOOP_BODY in context:
            error_list.append(FOR_LOOP_BODY_MISMATCH)

        # Rule 4: Tag contains "MISSING".
        if ANNOTATION_TGA_MISSING in tag and tag != ANNOTATION_TAG_MISSING_FOR_LOOP:
            error_list.append(MISSING_STATEMENT)

        # Rule 5: CONST_VALUE_MISMATCH with context ending with the specified pattern.
        if tag == ANNOTATION_TAG_CONST_VALUE_MISMATCH and pattern_value_parameter.search(context):
            error_list.append(ERROR_VALUE_PARAMETER)

    return set(error_list)
