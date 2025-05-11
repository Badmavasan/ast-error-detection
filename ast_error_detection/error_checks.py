
"""from ast_error_detection.constants import FOR_LOOP_INCORRECT_NUMBER_OF_ITERATIONS, FOR_LOOP_MISSING, \
    FOR_LOOP_BODY_MISMATCH, MISSING_STATEMENT, ERROR_VALUE_PARAMETER, ANNOTATION_TAG_CONST_VALUE_MISMATCH, \
    ANNOTATION_TAG_MISSING_FOR_LOOP, ANNOTATION_CONTEXT_FOR_LOOP_BODY, ANNOTATION_TGA_MISSING, \
    ANNOTATION_CONTEXT_FUNCTION_PARAMETER, LO_NUMBER_ITERATION_ERROR, LO_NUMBER_ITERATION_ERROR_UNDER2"""
from ast_error_detection.constants import *

import re


def get_customized_error_tags2(input_list):
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
        if tag == ANNOTATION_TAG_CONST_VALUE_MISMATCH and "For > Condition: > Call: range > Const" in context:
            error_list.append(FOR_LOOP_INCORRECT_NUMBER_OF_ITERATIONS)

        # Rule 2: Tag exactly matches MISSING_FOR_LOOP.
        if tag == ANNOTATION_TAG_MISSING_FOR_LOOP:
            error_list.append(FOR_LOOP_MISSING)

        # Rule 3: Context contains "Module > For > Body".
        if ANNOTATION_CONTEXT_FOR_LOOP_BODY in context:
            error_list.append(FOR_LOOP_BODY_MISMATCH)

        # Rule 4: Tag contains "MISSING".
        if ANNOTATION_TAG_MISSING in tag and tag != ANNOTATION_TAG_MISSING_FOR_LOOP:
            error_list.append(MISSING_STATEMENT)

        # Rule 5: CONST_VALUE_MISMATCH with context ending with the specified pattern.
        if tag == ANNOTATION_TAG_CONST_VALUE_MISMATCH and pattern_value_parameter.search(context):
            error_list.append(ERROR_VALUE_PARAMETER)

    return set(error_list)

def get_customized_error_tags(input_list): # new version
    """
    Analyzes a list of error details for specific tag and context patterns,
    returning a list of error code strings based on the following rules.

    Each element in the input list should be a list of either 3 or 4 elements.
    The first element is treated as the error tag and the last element as the error context.

    Rules:
        1. If the tag is "CONST_VALUE_MISMATCH" and the context contains
           "For > Condition: > Call: rang > Const", or "While > Condition: > Compare" then add:
               "LO_NUMBER_ITERATION_ERROR" OR "LO_NUMBER_ITERATION_ERROR_UNDER2"
           (Indicates a constant value mismatch in a for loop's condition. The difference being either 1 or greater.)

        2. If the tag exactly matches "MISSING_FOR_LOOP" or "MISSING_WHILE_LOOP", then add:
               "LO_FOR_MISSING" "LO_WHILE_MISSING"
           (Indicates that a for loop is missing where expected.)



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
        context2 = error_details[-2]

        # ITERATION ERROR
        if tag == ANNOTATION_TAG_CONST_VALUE_MISMATCH and "For > Condition: > Call: range > Const" in context:
            number1 = int(context.split(" ")[-1])
            number2 = int(context2.split(" ")[-1])
            if abs(number1-number2) > 1 :
                error_list.append(LO_FOR_NUMBER_ITERATION_ERROR)
            else :
                error_list.append(LO_FOR_NUMBER_ITERATION_ERROR_UNDER2)
        if tag == ANNOTATION_TAG_CONST_VALUE_MISMATCH and "While > Condition: > Compare" in context:
            number1 = int(context.split(" ")[-1])
            number2 = int(context2.split(" ")[-1])
            print("coucou", number1, number2)
            if abs(number1-number2) > 1 :
                error_list.append(LO_WHILE_NUMBER_ITERATION_ERROR)
            else :
                error_list.append(LO_WHILE_NUMBER_ITERATION_ERROR_UNDER2)

        # BODY MISSING
        if tag in ANNOTATION_TAG_INCORRECT_POSITION_LOOP :
            error_list.append(LO_BODY_MISPLACED)
        if ANNOTATION_TAG_MISSING in tag and (ANNOTATION_CONTEXT_FOR_LOOP_BODY in context or ANNOTATION_CONTEXT_WHILE_LOOP_BODY in context):
            error_list.append(LO_BODY_MISSING_NOT_PRESENT_ANYWHERE)

        # MISSING LOOP OR CS OR FUNCTION
        if tag == ANNOTATION_TAG_MISSING_FOR_LOOP:
            error_list.append(LO_FOR_MISSING)

        if tag == ANNOTATION_TAG_MISSING_WHILE_LOOP:
            error_list.append(LO_WHILE_MISSING)

        if tag == ANNOTATION_TAG_MISSING_CS:
            error_list.append(CS_MISSING)

        if tag == ANNOTATION_TAG_MISSING_FUNCTION_DEFINITION:
            error_list.append(F_DEFINITION_MISSING)

        # CS : error 2 : body error or body missing
        if ANNOTATION_TAG_MISSING in tag and ANNOTATION_CONTEXT_CS_BODY in context:
            error_list.append(CS_BODY_ERROR)

        # CS : error 3 : body_misplaced
        if tag == ANNOTATION_TAG_INCORRECT_POSITION_CS:
            error_list.append(CS_BODY_MISPLACED)

        # VAR : error 1 : Initialization
        if tag == VAR_CONST_MISMATCH and ANNOTATION_CONTEXT_VAR in context:
            error_list.append(VA_DECLARATION_INITIALIZATION_ERROR)

        # FONCTION : error 1 : definition error arg
        if tag == ANNOTATION_TAG_MISSING_ARGUMENT or tag == ANNOTATION_TAG_UNNECESSARY_ARGUMENT:
            error_list.append(F_DEFINITION_ERROR_ARG)

        # FUNCTION : error 2 : definition error return
        if tag == ANNOTATION_TAG_MISSING_RETURN or tag == ANNOTATION_TAG_UNNECESSARY_RETURN or (tag == ANNOTATION_TAG_MISSING_VARIABLE and ANNOTATION_CONTEXT_RETURN_1 in context and ANNOTATION_CONTEXT_RETURN_2 in context):
            error_list.append(F_DEFINITION_ERROR_RETURN)

        # EXP : error 1 : error conditional branch
        if tag == ANNOTATION_TAG_INCORRECT_OPERATION_IN_CS :
            error_list.append(EXP_ERROR_CONDITIONAL_BRANCH)

        '''
        
        # Rule 4: Tag contains "MISSING".
        if ANNOTATION_TGA_MISSING in tag and tag != ANNOTATION_TAG_MISSING_FOR_LOOP:#not in [ANNOTATION_TAG_MISSING_FOR_LOOP, ANNOTATION_TAG_MISSING_WHILE_LOOP, ANNOTATION_TAG_MISSING_CS, ANNOTATION_CONTEXT_FOR_LOOP_BODY]:
            error_list.append(MISSING_STATEMENT)

        # Rule 5: CONST_VALUE_MISMATCH with context ending with the specified pattern.
        if tag == ANNOTATION_TAG_CONST_VALUE_MISMATCH and pattern_value_parameter.search(context):
            error_list.append(ERROR_VALUE_PARAMETER)
        '''
    return set(error_list)