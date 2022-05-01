from typing import Any, Tuple


def eliminate_bool(value: Any):
    """
        If input value is a boolean, replaces it with "true" or "false" string, respectively. 
        Needed due to the fact that JUCE has no Osc boolean.
    """
    if value is True:
        return "true"
    elif value is False:
        return "false"
    else:
        return value


def convertTuple(tup: Tuple):
    """
        Changes a tuple value to a concatinated string
    """
    return ''.join(map(str, tup))
