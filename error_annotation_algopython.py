import json
from collections import Counter
from typing import Iterable, Dict, List

from ast_error_detection.error_diagnosis import get_primary_code_errors, get_typology_based_code_error

def _build_correct_codes_index(meta_file: str) -> Dict[int, List[str]]:
    """
    Load the metadata file and build a map: exerciseId -> correctCodes (list of strings).
    The metadata file is expected to be a JSON array of objects like:
      { "exerciseId": 60, "correctCodes": ["..."], ... }
    """
    with open(meta_file, "r", encoding="utf-8") as f:
        meta = json.load(f)

    index: Dict[int, List[str]] = {}
    for obj in meta:
        try:
            ex_id = int(obj.get("exerciseId"))
        except Exception:
            continue
        cc = obj.get("correctCodes")
        if isinstance(cc, list):
            index[ex_id] = cc
    return index


def annotate_exercises(meta_file: str, exercise_ids: Iterable[int]):
    """
    For each exerciseId in `exercise_ids`, reads:
      - input file:  exercice_{exerciseId}_algopython_data.json
      - output file: annotations_{exerciseId}.json
    Runs get_typology_based_code_error(code, correct_codes) for each submission
    and saves annotations with counts per exercise to the output files.
    """
    correct_index = _build_correct_codes_index(meta_file)

    for ex_id in exercise_ids:
        input_file = f"data/serieB/tentatives_exercise_{ex_id}.json"
        typology_errors_output_file = f"annotations/serieB/typology_annotations_{ex_id}.json"
        primary_errors_output_file = f"annotations/serieB/primary_annotations_{ex_id}.json"

        # Load submissions
        try:
            with open(input_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"Skipping {ex_id}: no input file {input_file}")
            continue

        # Get correct codes
        correct_codes = correct_index.get(ex_id)
        if not correct_codes:
            print(f"Skipping {ex_id}: no correctCodes in metadata")
            continue

        # Aggregate annotations
        typology_counter = Counter()
        primary_counter = Counter()
        processed = 0
        skipped_errors = 0

        for item in data:
            code = item.get("code", "")
            try:
                _, result = get_typology_based_code_error(code, correct_codes)
                result2 = [x[0] for x in get_primary_code_errors(code, correct_codes[0])[-1]]

                if not isinstance(result, (list, set, tuple)):
                    raise TypeError("get_typology_based_code_error: second return value is not iterable")

                typology_counter.update(result)
                primary_counter.update(result2)

                processed += 1

            except Exception as e:
                print(e)
                skipped_errors += 1

        # Convert Counters to dicts
        output = {int(ex_id): dict(typology_counter)}
        output2 = {int(ex_id): dict(primary_counter)}

        # Save to file
        with open(typology_errors_output_file, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        with open(primary_errors_output_file, "w", encoding="utf-8") as f2:
            json.dump(output2, f2, ensure_ascii=False, indent=2)

        print(
            f"Exercise {ex_id}: processed={processed}, skippedErrors={skipped_errors}, "
            f"typologyErrors={len(typology_counter)}, primaryErrors={len(primary_counter)}"
        )


annotate_exercises(
     meta_file="exercises.json",  # the file that has exerciseId + correctCodes
     exercise_ids=[85, 81, 82, 84, 80, 79, 147]
)