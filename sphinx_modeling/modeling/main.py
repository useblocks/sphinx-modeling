"""
Main logic for modeling.

It contains some mypy '# type: ignore' which are used for Sphinx environment fields.
They are unknown to mypy as they are dynamically created.
"""

from contextlib import suppress
import copy
import os
import pickle
from typing import Any, Dict, List, Set

from pydantic import BaseModel, ValidationError, root_validator
from pydantic.fields import ModelField
from sphinx.environment import BuildEnvironment

from sphinx_modeling.logging import get_logger


PYDANTIC_INSTANCES: Dict[str, Any] = {}  # fully created Pydantic instances
log = get_logger(__name__)


class BaseModelNeeds(BaseModel):
    """
    Custom Base class to support custom validation against all needs.

    This approach https://github.com/pydantic/pydantic/issues/1170#issuecomment-575233689
    is used to make all needs available to validators.
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
    # deep copy needs dictionary as it is modified
    needs_copy = copy.deepcopy(needs)

    # resolve all need links
    all_link_types = {"links"}
    all_link_types.update({link_config["option"] for link_config in env.config.needs_extra_links})
    back_types = set()
    for link_type in all_link_types:
        back_types.add(f"{link_type}_back")
    all_link_types.update(back_types)

    if env.config.modeling_resolve_links:
        # user may decide to validate need IDs directly or resolve them in own (root) validators;
        # normally it is more helpful to see resolved needs so far fields can be used for validation
        for need in needs_copy.values():
            _resolve_links(need, needs_copy, all_link_types)

    pydantic_models = env.config.modeling_models

    if not pydantic_models:
        # user did not define any models, skip the check
        return

    sphinx_needs_link_types = [link["option"] for link in env.config.needs_extra_links]
    sphinx_needs_link_types_back = [f"{link}_back" for link in sphinx_needs_link_types]

    for model in pydantic_models.values():
        # invert the order of root validators to have
        # context variables available in user defined root validators
        model.__post_root_validators__.reverse()

    logged_types_without_model = set()  # helper to avoid duplicate log output
    all_successful = True
    all_messages: List[str] = []  # return variable

    for need in needs_copy.values():
        try:
            # expected model name is the need type with first letter capitalized (this is how Python class are named)
            if need["type"] in pydantic_models:
                model = pydantic_models[need["type"]]
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
                PYDANTIC_INSTANCES[need["id"]] = instance
            else:
                if need["type"] not in logged_types_without_model:
                    all_successful = False
                    log.warning(f"Model validation: no model defined for need type '{need['type']}'")
                    logged_types_without_model.add(need["type"])
        except ValidationError as exc:
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
            log.info(msg, color="red")
        log.warning("Validation errors appeared!")
        dir_name = os.path.dirname(os.path.abspath(msg_path))
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        with open(msg_path, "wb") as fp:
            pickle.dump(all_messages, fp)


def _remove_unrequested_fields(
    need: Dict[str, Any],
    model_fields: List[str],
    remove_fields: List[str],
    remove_backlinks: bool,
    sphinx_needs_link_types_back: List[str],
) -> Any:
    """
    Remove unneeded object fields.

    :param model_fields: list of fields that are contained in the user defined model
    :param remove_fields: list of fields to remove from the dict
    :param remove_backlinks: flag indicating whether to remove backlink references
    :param sphinx_needs_link_types_back: list of sphinx-needs link backreference names (e.g. blocks -> blocks_back)
    """
    output_dict = {}
    for key, value in need.items():
        if key in remove_fields:
            continue  # static user configuration
        if value is None:
            continue  # not considered a useful field for modeling (e.g. style)
        keep = False
        if key in model_fields:
            keep = True
        if key == "parent_need":
            keep = True  # special sphinx-needs field that holds the nesting parent
        if not keep:
            if isinstance(value, bool):
                # useful for flags such as is_need
                keep = True
            if isinstance(value, (str, list)):
                # str:  do not return empty values as they cannot be set in RST
                # list: need links, those can be empty by setting in RST or not giving them, cannot distinguish here;
                #       empty lists should be removed unless they are part of model_fields
                keep = bool(value)
            if remove_backlinks and key in sphinx_needs_link_types_back:
                keep = False
        if keep:
            output_dict[key] = value
    return output_dict


def _resolve_links(need: Dict[str, Any], needs: Dict[str, Dict[str, Any]], all_link_types: Set[str]) -> None:
    """Resolve link fields and backlinks for a given need."""
    for field, link_targets in need.items():
        if field in all_link_types and link_targets:
            resolved_link_targets = []
            for link_target in link_targets:
                if link_target in needs:
                    resolved_link_targets.append(needs[link_target])
            need[field] = resolved_link_targets
    if need["parent_need"] and need["parent_need"] in needs:
        need["parent_need"] = needs[need["parent_need"]]
