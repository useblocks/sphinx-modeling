"""
Main logic for modeling.

It contains some mypy '# type: ignore' which are used for Sphinx environment fields.
They are unknown to mypy as they are dynamically created.
"""

import os
import pickle
from contextlib import suppress
from typing import Any, Dict, List

from pydantic import BaseModel, ValidationError, root_validator
from pydantic.fields import ModelField
from sphinx.environment import BuildEnvironment

from sphinx_modeling.logging import get_logger

PYDANTIC_INSTANCES: Dict[str, Any] = {}  # fully created Pydantic instances
PENDING_NEED_IDS: List[str] = []  # Pydantic startet building but not ready (resolving links)
# CICULAR_LOOP_LINKS: List[Tuple[str, str, str]] = []  # Tuple: need id, link field, link target
log = get_logger(__name__)


class BaseModelNeeds(BaseModel):
    """
    Custom Base class to support custom validation against all needs.

    This approach https://github.com/pydantic/pydantic/issues/1170#issuecomment-575233689
    to make all needs available to validators.
    Other approaches are Python ContextVars which also works. ContextVars however are hard to
    expose to the end users that run custom validators.
    """

    all_needs: Any
    env: Any

    @root_validator()
    def remove_context(cls, values: Dict[str, ModelField]) -> Dict[str, ModelField]:  # noqa: N805
        """
        Remove context variables after others validators were executed.

        The values are mainly used in instantiate_links.
        """
        del values["all_needs"]
        del values["env"]
        return values

    @root_validator(pre=True)
    def instantiate_links(cls, values: Dict[str, Any]) -> Dict[str, Any]:  # noqa: N805
        """
        Resolve sphinx-needs link targets.

        The function is called by pydantic when
        1. looping over all needs in check_model
        2. when a link targets gets resolved and instantiated in this very function
        """
        try:
            # str conversion should not go wrong
            need_id = str(values["id"])
        except KeyError:
            log.warning("Error instantiating links: need has no id")
            raise
        if need_id in PYDANTIC_INSTANCES:
            # do nothing as this object is already successfully validated
            # it can happen when a later need links to an already instantiated need
            return values
        if need_id not in PENDING_NEED_IDS:
            # remember the id to detect circular references (recursion depth limitation)
            PENDING_NEED_IDS.append(need_id)

        pydantic_models = values["env"].config.modeling_models
        model_name_2_model = {model.__name__: model for model in pydantic_models}
        sphinx_needs_list_link_types = [link["option"] for link in values["env"].config.needs_extra_links]
        sphinx_needs_list_link_types.append("parent_needs")
        sphinx_needs_list_link_types_back = [f"{link}_back" for link in sphinx_needs_list_link_types]
        sphinx_needs_string_link_types = ["parent_need"]

        for link_type, link_value in values.items():
            if link_type not in sphinx_needs_list_link_types + sphinx_needs_string_link_types:
                continue
            resolved_needs = []
            if link_type in sphinx_needs_string_link_types:
                assert isinstance(link_value, str)
                links = [link_value]
            else:
                assert isinstance(link_value, list)
                links = link_value
            for target in links:
                if target in PENDING_NEED_IDS:
                    # circular link loop detected
                    log.warning(f"{need_id}: unsupported circular loop detected for link '{link_type}: {target}'")
                    log.warning("Ignoring target for validation")
                    continue
                if target in PYDANTIC_INSTANCES:
                    instance = PYDANTIC_INSTANCES[target]
                else:
                    try:
                        resolved_need = values["all_needs"][target]
                    except KeyError:
                        log.warning(f"{need_id}: cannot resolve link '{link_type}: {target}'")
                        log.warning("Ignoring target for validation")
                        continue
                    resolved_need_model = model_name_2_model[resolved_need["type"].title()]
                    resolved_need_model_fields = [
                        name
                        for name, field in resolved_need_model.__fields__.items()
                        if isinstance(field, ModelField) and name not in ["all_needs", "env"]
                    ]
                    need_relevant_fields = _remove_unrequested_fields(
                        resolved_need,
                        resolved_need_model_fields,
                        values["env"].config.modeling_remove_fields,
                        values["env"].config.modeling_remove_backlinks,
                        sphinx_needs_list_link_types_back,
                    )
                    instance = need_relevant_fields
                    instance.update(
                        {
                            "all_needs": values["all_needs"],
                            "env": values["env"],
                        }
                    )
                    # instance = resolved_need_model(
                    #     **need_relevant_fields, all_needs=values["all_needs"], env=values["env"]
                    # )  # run pydantic
                    # PYDANTIC_INSTANCES[resolved_need["id"]] = instance
                resolved_needs.append(instance)

            if link_type in sphinx_needs_string_link_types:
                if resolved_needs:
                    values[link_type] = resolved_needs[0]
            else:
                values[link_type] = resolved_needs
        return values


def check_model(env: BuildEnvironment, msg_path: str) -> None:
    """
    Check all needs against a user defined pydantic model.

    :param env: Sphinx environment, source of all needs to be made available for validation
    """
    # Only perform calculation if not already done yet
    if env.needs_modeling_workflow["models_checked"]:  # type: ignore
        return

    # remove outdated messages file
    with suppress(OSError):
        os.remove(msg_path)

    needs = env.needs_all_needs  # type: ignore
    # all_needs.set(needs)
    pydantic_models = env.config.modeling_models

    if not pydantic_models:
        # user did not define any models, skip the check
        return

    sphinx_needs_link_types = [link["option"] for link in env.config.needs_extra_links]
    sphinx_needs_link_types_back = [f"{link}_back" for link in sphinx_needs_link_types]

    # build a dictionay to look up user model names
    model_name_2_model = {model.__name__: model for model in pydantic_models}

    for model in pydantic_models:
        # invert the order of root validators to have
        # context variables available in user defined root validators
        model.__post_root_validators__.reverse()
        # # later needed for circular model handling
        # model.update_forward_refs()

    logged_types_without_model = set()  # helper to avoid duplicate log output
    all_successful = True
    all_messages: List[str] = []  # return variable
    global PENDING_NEED_IDS
    for need in needs.values():
        if need["id"] in PYDANTIC_INSTANCES:
            # this id was handled during links resolution
            continue
        last_idx_pending_need_ids = len(PENDING_NEED_IDS) - 1
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
                    env.config.modeling_remove_fields,
                    env.config.modeling_remove_backlinks,
                    sphinx_needs_link_types_back,
                )
                instance = model(**need_relevant_fields, all_needs=needs, env=env)  # run pydantic
                PENDING_NEED_IDS.remove(need["id"])
                PYDANTIC_INSTANCES[need["id"]] = instance
            else:
                if need["type"] not in logged_types_without_model:
                    log.warning(f"Model validation: no model defined for need type '{need['type']}'")
                    logged_types_without_model.add(need["type"])
        except ValidationError as exc:
            # remove all pending IDs that were about to be instantiated
            PENDING_NEED_IDS = PENDING_NEED_IDS[: last_idx_pending_need_ids + 1]
            all_successful = False
            all_messages.append(f"Model validation: failed for need {need['id']}")
            all_messages.append(str(exc))
            # get field values as pydantic does not publish that in ValidationError
            # in all cases, like for regex checks
            # see https://github.com/pydantic/pydantic/issues/784
            # TODO: the following code breaks in case a nested model is showing the errors;
            #       the loc is then a tuple
            # error_fields = set()
            # for error in exc.errors():
            #     for field in error["loc"]:
            #         if "regex" in error["type"]:
            #             if field not in error_fields:
            #                 messages.append(f"Actual value: {need[field]}")
            #                 error_fields.add(field)
            # all_messages.extend(messages)
        except Exception as exc:  # pylint: disable=broad-except # user validators might throw anything
            all_successful = False
            all_messages.append(f"Model validation: failed for need {need['id']}")
            all_messages.append(repr(exc))
    if all_successful:
        log.info("Validation was successful!")

    # Finally set a flag so that this function gets not executed several times
    env.needs_modeling_workflow["models_checked"] = True  # type: ignore

    if all_messages:
        for msg in all_messages:
            log.warning(msg)
        dir_name = os.path.dirname(os.path.abspath(msg_path))
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        with open(msg_path, "wb") as fp:
            pickle.dump(all_messages, fp)


def _value_allowed(value: Any) -> bool:
    """Check whether a given need field is allowed for validation."""
    if value is None:
        return False
    if isinstance(value, bool):
        # useful for flags such as is_need
        return True
    elif isinstance(value, (str, list)):
        # do not return empty strings or lists - they are never user defined as RST does not support empty options
        return bool(value)
    else:
        # don't return all other types (such as class instances like content_node)
        return False


def _remove_unrequested_fields(
    need: Dict[str, Any],
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
    for key, value in need.items():
        if not _value_allowed(value):
            # type check and empty check
            continue
        if key not in model_fields:
            if key in remove_fields:
                continue
            if isinstance(value, list) and remove_backlinks and key in sphinx_needs_link_types_back:
                # checking for list type is a safety measure
                continue
        output_dict[key] = value
    return output_dict
