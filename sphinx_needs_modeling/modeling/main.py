import os
import pickle
import re
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, ValidationError, root_validator
from pydantic.fields import Field, ModelField
from sphinx.environment import BuildEnvironment
from sphinx_needs_modeling.logging import get_logger


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
) -> None:
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
        raise ValueError(f"Field type is neither str nor List[str]")
    for link in links:
        if link not in values["all_needs"]:
            raise ValueError(f"Cannot find '{link}' in needs dictionary")


def check_model(env: BuildEnvironment, msg_path: str) -> None:
    """
    Check all needs against a user defined pydantic model.

    :param env: Sphinx environment, source of all needs to be made available for validation
    """
    log = get_logger(__name__)
    # Only perform calculation if not already done yet
    if env.needs_modeling_workflow["models_checked"]:
        return

    # remove outdated messages file
    try:
        os.remove(msg_path)
    except OSError:
        pass

    needs = env.needs_all_needs
    # all_needs.set(needs)
    pydantic_models = env.config.needs_modeling_pydantic_models

    if not pydantic_models:
        # user did not define any models, skip the check
        return

    sphinx_needs_link_types = [link["option"] for link in env.config.needs_extra_links]
    sphinx_needs_link_types_back = [f"{link}_back" for link in sphinx_needs_link_types]

    # build a dictionay to look up user model names
    model_name_2_model = {model.__name__: model for model in pydantic_models}

    logged_types_without_model = set()  # helper to avoid duplicate log output
    all_successful = True
    all_messages = []  # return variable
    for need in needs.values():
        try:
            # expected model name is the need type with first letter capitalized (this is how Python class are named)
            expected_pydantic_model_name = need["type"].title()
            if expected_pydantic_model_name in model_name_2_model:
                model = model_name_2_model[expected_pydantic_model_name]
                # get all fields that exist as per the model
                model_fields = [name for name, field in model.__fields__.items() if isinstance(field, ModelField)]
                need_relevant_fields = _remove_unrequested_fields(
                    need,
                    model_fields,
                    env.config.needs_modeling_remove_fields,
                    env.config.needs_modeling_remove_backlinks,
                    sphinx_needs_link_types_back,
                )
                model(**need_relevant_fields, all_needs=needs)  # run pydantic
            else:
                if need["type"] not in logged_types_without_model:
                    log.warn(f"Model validation: no model defined for need type '{need['type']}'")
                    logged_types_without_model.add(need["type"])
        except ValidationError as exc:
            all_successful = False
            messages = []
            messages.append(f"Model validation: failed for need {need['id']}")
            messages.append(str(exc))
            # get field values as pydantic does not publish that in ValidationError
            # in all cases, like for regex checks
            # see https://github.com/pydantic/pydantic/issues/784
            error_fields = set()
            for error in exc.errors():
                for field in error["loc"]:
                    if "regex" in error["type"]:
                        if field not in error_fields:
                            messages.append(f"Actual value: {need[field]}")
                            error_fields.add(field)
            all_messages.extend(messages)
            for msg in messages:
                log.warn(msg)
    if all_successful:
        log.info("Validation was successful!")

    # Finally set a flag so that this function gets not executed several times
    env.needs_modeling_workflow["models_checked"] = True

    if all_messages:
        dir_name = os.path.dirname(os.path.abspath(msg_path))
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        with open(msg_path, "wb") as fp:
            pickle.dump(all_messages, fp)


def _value_allowed(v: Any) -> bool:
    """Check whether a given need field is allowed for validation."""
    if v is None:
        return False
    if isinstance(v, bool):
        # useful for flags such as is_need
        return True
    elif isinstance(v, (str, list)):
        # do not return empty strings or lists - they are never user defined as RST does not support empty options
        return bool(v)
    else:
        # don't return all other types (such as class instances like content_node)
        return False


def _remove_unrequested_fields(
    d: Any,
    model_fields: List[str],
    remove_fields: List[str],
    remove_backlinks: bool,
    sphinx_needs_link_types_back: List[str],
) -> Any:
    """
    Remove need object fields that

    1. are of wrong type (allowed ar str and List[str] and bool)
    1. are empty (those are not relevant anyway as RST does not support empty options)
    2. are in contained in remove_fields (even if not empty like lineno) but not in model_fields

    :param model_fields: list of fields that are contained in the user defined model
    :param remove_fields: list of fields to remove from the dict
    :param remove_backlinks: flag indicating whether to remove backlink references
    :param sphinx_needs_link_types_back: list of sphinx-needs link backreference names (e.g. blocks -> blocks_back)
    """
    output_dict = {}
    for key, value in d.items():
        if not _value_allowed(value):
            # type check and empty check
            continue
        if key not in model_fields:
            if key in remove_fields:
                continue
            if isinstance(value, list) and key in sphinx_needs_link_types_back:
                # checking for list type is a safety measure
                continue
        output_dict[key] = value
    return output_dict
