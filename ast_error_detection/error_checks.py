# This file is part of ast_error_detection.
# Copyright (C) 2025 Badmavasan Kirouchenassamy & Eva Chouaki.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or any later version.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

from ast_error_detection.constants import *
import re


def process_tag_triplets(input_list, required_tags, match_start, match_end):
    """
    Checks if all required_tags are present in the input_list (as first element in sublists).
    If so, extracts those sublists and compares the part of their third element from match_start to match_end.
    If all match, return the dedicated error tag

    Args:
        input_list (list of lists): Each sublist must contain [tag, context1, context2].
        required_tags (set): A set of tags to look for.
        match_start (str): Start delimiter for substring match in context2.
        match_end (str): End delimiter for substring match in context2.

    Returns:
        str: Error Tag
    """
    # Filter entries with tags in required_tags
    filtered = [entry for entry in input_list if entry[0] in required_tags]

    # Check if the same tags are present in both sets
    tags_present = [entry[0] for entry in filtered]

    if not all(elem in tags_present for elem in required_tags):
        return None  # Do nothing if tags don't exactly match

    # Extract the entries matching the tags
    tag_entries = [entry for entry in filtered if entry[0] in required_tags]

    def extract_context_segment(context, start, end):
        try:
            start_index = context.index(start)
            end_index = context.index(end, start_index) + len(end)
            return context[start_index:end_index]
        except ValueError:
            return None

    # Extract segments from context2
    segments = [
        extract_context_segment(entry[2], match_start, match_end)
        for entry in tag_entries
    ]

    if all(seg == segments[0] and seg is not None for seg in segments):
        # If all segments are the same and not None, append EXP_ERR
        if match_start == ANNOTATION_CONTEXT_MODULE and match_end == ANNOTATION_CONTEXT_ASSIGN:
            return VA_DECLARATION_INITIALIZATION_ERROR

    return None


def get_customized_error_tags(input_list):  # new version
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


    for tag_list in [
        ANNOTATION_TAG_LIST_VARIABLE_DECLARATION_MISSING,
        ANNOTATION_TAG_LIST_VARIABLE_DECLARATION_UNNECESSARY
    ]:
        result = process_tag_triplets(input_list, tag_list, ANNOTATION_CONTEXT_MODULE, ANNOTATION_CONTEXT_ASSIGN)
        if result is not None:
            error_list.append(result)

    for error_details in input_list:
        # Ensure the error detail has the expected number of elements; if not, skip it.
        if len(error_details) not in (3, 4):
            continue

        if len(error_details) == 3:
            tag = error_details[0]
            context = error_details[-1]
            context2 = error_details[-2]
        else:
            tag = error_details[0]
            context = error_details[-1]
            context2 = error_details[-3]

        # ITERATION ERROR
        if tag == ANNOTATION_TAG_CONST_VALUE_MISMATCH and "For > Condition: > Call: range > Const" in context:
            number1 = int(context.split(" ")[-1])
            number2 = int(context2.split(" ")[-1])
            if abs(number1 - number2) > 1:
                error_list.append(LO_FOR_NUMBER_ITERATION_ERROR)
            else:
                error_list.append(LO_FOR_NUMBER_ITERATION_ERROR_UNDER2)
        if tag == ANNOTATION_TAG_CONST_VALUE_MISMATCH and "While > Condition: > Compare" in context:
            number1 = int(context.split(" ")[-1])
            number2 = int(context2.split(" ")[-1])
            if abs(number1 - number2) > 1:
                error_list.append(LO_WHILE_NUMBER_ITERATION_ERROR)
            else:
                error_list.append(LO_WHILE_NUMBER_ITERATION_ERROR_UNDER2)

        if ANNOTATION_TAG_INCORRECT_POSITION in tag and ANNOTATION_CONTEXT_FOR_LOOP_BODY in context:
            error_list.append(LO_BODY_MISPLACED)

        # BODY MISSING
        if tag in ANNOTATION_TAG_INCORRECT_POSITION_LOOP:
            error_list.append(LO_BODY_MISPLACED)
        if ANNOTATION_TAG_MISSING in tag and (
                ANNOTATION_CONTEXT_FOR_LOOP_BODY in context or ANNOTATION_CONTEXT_WHILE_LOOP_BODY in context):
            error_list.append(LO_BODY_MISSING_NOT_PRESENT_ANYWHERE)

        # WHILE (a retirer par la suite)
        if tag == ANNOTATION_TAG_INCORRECT_OPERATION_IN_COMP and ANNOTATION_CONTEXT_WHILE_LOOP_CONDITION in context:
            error_list.append(LO_CONDITION_ERROR)

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
        if tag == ANNOTATION_TAG_MISSING_RETURN or tag == ANNOTATION_TAG_UNNECESSARY_RETURN or (
                tag == ANNOTATION_TAG_MISSING_VARIABLE and ANNOTATION_CONTEXT_RETURN_1 in context and ANNOTATION_CONTEXT_RETURN_2 in context):
            error_list.append(F_DEFINITION_ERROR_RETURN)

        # EXP : error 1 : error conditional branch
        if tag == ANNOTATION_TAG_INCORRECT_OPERATION_IN_COMP and ANNOTATION_CONTEXT_CS_CONDITION in context:
            error_list.append(EXP_ERROR_CONDITIONAL_BRANCH)

        if tag == ANNOTATION_TAG_CONST_VALUE_MISMATCH and re.search(ANNOTATION_CONTEXT_FUNCTION_PARAMETER, context):
            error_list.append(F_DEFINITION_ERROR_ARG)

        if tag == ANNOTATION_TAG_MISSING_CALL_INSTRUCTION:
            error_list.append(F_CALL_MISSING)

        if tag == ANNOTATION_TAG_CONST_VALUE_MISMATCH and re.search(ANNOTATION_CONTEXT_FUNCTION_CALL_UPDATE, context):
            error_list.append(F_CALL_MISSING)

        """
            SPECIFIC CODE SECTION
        """

        rules = [
            (ANNOTATION_TAG_MISSING_CONST_VALUE, ANNOTATION_CONTEXT_FOR_LOOP_BODY),
            (ANNOTATION_TAG_MISSING_CALL_STATEMENT, ANNOTATION_CONTEXT_FOR_LOOP_BODY ),
            (ANNOTATION_TAG_UNNECESSARY_CALL_STATEMENT, ANNOTATION_CONTEXT_FOR_LOOP_BODY),
            (ANNOTATION_TAG_CONST_VALUE_MISMATCH, ANNOTATION_CONTEXT_WHILE_LOOP_BODY),
            (ANNOTATION_TAG_INCORRECT_POSITION_ASSIGN, ANNOTATION_CONTEXT_FOR_LOOP_BODY),
        ]

        for rule_tag, rule_context in rules:
            if tag == rule_tag and rule_context in context:
                error_list.append(LO_BODY_ERROR)


        FUNC_CALL_RX = re.compile(ANNOTATION_CONTEXT_FUNCTION_CALL)
        INCORRECT_RX = re.compile(ANNOTATION_TAG_INCORRECT_POSITION_REGEX)
        UNNECESSARY_RX = re.compile(ANNOTATION_TAG_UNNECESSARY_REGEX)
        MISSING_RX = re.compile(ANNOTATION_TAG_MISSING_REGEX)

        # Option A: explicit, very readable
        if FUNC_CALL_RX.match(context) and all(
                rx.match(tag) is None for rx in (INCORRECT_RX, UNNECESSARY_RX, MISSING_RX)
        ):
            error_list.append(F_CALL_ERROR)

        if tag == ANNOTATION_TAG_UNNECESSARY_CALL_STATEMENT and ANNOTATION_CONTEXT_UNNECESSARY_FUNCTION_CALL in context:
            error_list.append(F_UNNECESSARY_FUNCTION_CALL)

        """
            TRANSLATION OF ABOVE CODE
    
            if tag == ANNOTATION_TAG_UNNECESSARY_CALL_STATEMENT and ANNOTATION_CONTEXT_FOR_LOOP_BODY in context:
                error_list.append(LO_BODY_ERROR)
    
            if tag == ANNOTATION_TAG_CONST_VALUE_MISMATCH and ANNOTATION_CONTEXT_WHILE_LOOP_BODY in context:
                error_list.append(LO_BODY_ERROR)
    
            if tag == ANNOTATION_TAG_INCORRECT_POSITION_ASSIGN and ANNOTATION_CONTEXT_FOR_LOOP_BODY in context :
                error_list.append(LO_BODY_ERROR)
        """

        '''
        # Rule 4: Tag contains "MISSING".
        if ANNOTATION_TGA_MISSING in tag and tag != ANNOTATION_TAG_MISSING_FOR_LOOP:#not in [ANNOTATION_TAG_MISSING_FOR_LOOP, ANNOTATION_TAG_MISSING_WHILE_LOOP, ANNOTATION_TAG_MISSING_CS, ANNOTATION_CONTEXT_FOR_LOOP_BODY]:
            error_list.append(MISSING_STATEMENT)

        # Rule 5: CONST_VALUE_MISMATCH with context ending with the specified pattern.
        if tag == ANNOTATION_TAG_CONST_VALUE_MISMATCH and pattern_value_parameter.search(context):
            error_list.append(ERROR_VALUE_PARAMETER)
        '''
    return set(error_list)
