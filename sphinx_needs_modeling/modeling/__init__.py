from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, ValidationError, root_validator
from pydantic.fields import Field, ModelField


class BaseModelNeeds(BaseModel):
    """
    Custom Base class to support custom validation against all needs.

    Uses this approach https://github.com/pydantic/pydantic/issues/1170#issuecomment-575233689
    Other approaches are Python ContextVars which also works. ContextVars however are hard to
    expose to the end users that run custom validators.
    """

    all_needs: Any

    @root_validator()
    def remove_context(cls, values: Dict[str, ModelField]) -> Dict[str, ModelField]:
        """Remove all_needs before others validators run."""
        del values["all_needs"]
        return values


def validator_links(
    value: Union[str, List[str]],
    values: Dict[str, Any],
):
    """
    Check whether a link target
    - is of the right type (str, List[str])
    - has no duplicates
    - exists in the needs dictionary

    The needs dictionary is available as all_needs values as set in BaseModelNeeds.
    """
    if isinstance(value, str):
        # invoked with each_item=true
        links = [value]
    elif isinstance(value, list) and all(isinstance(elem, str) for elem in value):
        # is list of strings
        links = value
        duplicates = [v for v in links if links.count(v) > 1]
        unique_duplicates = list(set(duplicates))
        if unique_duplicates:
            raise ValueError(f"Duplicate link targets '{', '.join(unique_duplicates)}'")
    else:
        raise ValueError("Field type is neither str nor List[str]")
    for link in links:
        if link not in values["all_needs"]:
            raise ValueError(f"Cannot find '{link}' in needs dictionary")
