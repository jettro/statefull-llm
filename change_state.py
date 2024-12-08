import json
import re

from pydantic import BaseModel

from model import StateChange, PreviousRole


def set_nested_value(obj: BaseModel, change: StateChange) -> None:
    """
    Set a nested value in a Pydantic model.

    TODO: Use the `change.change` attribute to determine whether to set, append or remove a value.

    :param obj: Object to apply the change to
    :param change: The change to apply
    :return:
    """
    keys = re.split(r'[.\[\]]', change.field)  # Split on dots and brackets
    keys = [k for k in keys if k]  # Remove empty strings
    current_obj = obj

    # Traverse to the last object before the target attribute
    for attr in keys[:-1]:
        if attr.isdigit():  # Handle list indexing
            current_obj = current_obj[int(attr)]
        elif hasattr(current_obj, attr):
            current_obj = getattr(current_obj, attr)
        else:
            raise AttributeError(f"'{type(current_obj).__name__}' object has no attribute '{attr}'")

    # Use the final key to get the target attribute
    final_key = keys[-1]
    if not hasattr(current_obj, final_key):
        raise AttributeError(f"'{type(current_obj).__name__}' object has no attribute '{final_key}'")

    # Set the value using the type of the target attribute and the provided value
    target = getattr(current_obj, final_key)
    value = change.value
    # Try to parse the value as JSON if it's a string and can be parsed
    if isinstance(change.value, str):
        try:
            parsed_value = json.loads(value)
            if isinstance(parsed_value,list) and final_key == "previous_roles":
                value = [PreviousRole(**item) for item in parsed_value]
            elif final_key == "previous_roles":
                value = PreviousRole(**parsed_value)
            else:
                value = parsed_value
        except json.JSONDecodeError:
            pass  # Treat as plain string if JSON parsing fails

    if isinstance(target, list):
        if isinstance(value, list):
            target.extend(value)
        target.append(value)
    else:
        setattr(current_obj, final_key, value)
