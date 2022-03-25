from typing import Union

def represents_int(value: Union[str, int]) -> bool:
    """Checks whether or not a string or integer value represents an integer."""

    if not isinstance(value, (str, int)):
        raise ValueError("Value must be int or str.")

    try:
        is_int = value.isdigit()
    except:
        is_int = isinstance(value, int)
    return is_int
