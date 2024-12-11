import json
import re

from pydantic import BaseModel

from model import StateChange, PreviousRole


def parse_keys(field: str) -> list:
    """Parse a nested field into a list of keys."""
    keys = re.split(r'[.\[\]]', field)
    return [k for k in keys if k]


def traverse_to_target(obj: BaseModel, keys: list) -> tuple:
    """Traverse the object to the target parent and return it with the final key."""
    current_obj = obj
    for attr in keys[:-1]:
        if attr.isdigit():
            current_obj = current_obj[int(attr)]
        elif hasattr(current_obj, attr):
            current_obj = getattr(current_obj, attr)
        else:
            raise AttributeError(f"'{type(current_obj).__name__}' object has no attribute '{attr}'")
    return current_obj, keys[-1]


def parse_value(final_key: str, value: str) -> any:
    """Parse a string value into the appropriate type."""
    if not isinstance(value, str):
        return value
    try:
        parsed_value = json.loads(value)
        if isinstance(parsed_value, list) and final_key == "previous_roles":
            return [PreviousRole(**item) for item in parsed_value]
        elif final_key == "previous_roles":
            return PreviousRole(**parsed_value)
        return parsed_value
    except json.JSONDecodeError:
        return value


def set_nested_value(obj: BaseModel, change: StateChange) -> None:
    """
    Set a nested value in a Pydantic model.

    :param obj: The Pydantic model to modify.
    :param change: The change object containing the field and value.
    :type change.field: str - Field path, e.g., 'field.subfield[0].subsubfield'
    :type change.value: Union[str, int, float, list, dict] - New value to set.
    """
    keys = parse_keys(change.field)
    current_obj, final_key = traverse_to_target(obj, keys)

    # Use the final key to get the target attribute
    if not hasattr(current_obj, final_key):
        raise AttributeError(f"'{type(current_obj).__name__}' object has no attribute '{final_key}'")

    value = parse_value(final_key, change.value)
    target = getattr(current_obj, final_key)

    if isinstance(target, list):
        if isinstance(value, list):
            target.extend(value)
        target.append(value)
    else:
        setattr(current_obj, final_key, value)
