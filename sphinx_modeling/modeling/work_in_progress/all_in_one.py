from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Extra, ValidationError, constr, create_model, root_validator, validator
from pydantic.fields import Field, ModelField


# sphinx-needs internals
needs = {
    "STORY_1": {
        "id": "STORY_1",
        "type": "story",
        "status": "open",
        "active": "True",
        "specs": ["SPEC_1"],
        "implspecs": ["IMPL_1"],
    },
    "SPEC_1": {
        "id": "SPEC_1",
        "type": "spec",
        "importance": "HIGH",
        "opt_needs": ["STORY_1"],
        "needs": ["STORY_1"],
        "need": ["STORY_1"],
        "opt_need": ["STORY_1"],
    },
    "IMPL_1": {
        "id": "IMPL_1",
        "type": "impl",
    },
}


link_types = ["specs", "implspecs", "opt_needs", "needs", "need", "opt_need", "parent_need"]

# user provided models
needs_bool = Literal["True", "False"]


def validator_reuse(cls, v):
    # raise ValueError("StatusValidator")
    return v


class Story(BaseModel, extra=Extra.forbid):
    id: constr(regex=r"^STORY_[a-zA-Z0-9_]{1,}$")
    status: Literal["open", "done"]
    specs: Spec | None
    specs: list[Spec]
    implspecs: list[Spec | Impl] | None
    active: needs_bool

    @root_validator(pre=True)
    def test_root_validator_pre(cls, values):
        assert "card_number" not in values, "card_number should not be included"
        return values

    @root_validator()
    def remove_context(cls, values: dict[str, ModelField]) -> dict[str, ModelField]:
        return values

    _valid_status = validator("status", allow_reuse=True)(validator_reuse)

    @validator("active")
    def test_field_validator(cls, v):
        # raise ValueError("activeValidator")
        return v


class Spec(BaseModel, extra=Extra.forbid):
    id: str
    importance: Literal["HIGH"]
    opt_needs: list[Story] | None
    needs: list[Story]
    need: Story
    opt_need: Story | None


class Impl(BaseModel, extra=Extra.forbid):
    id: str


Story.update_forward_refs()
Spec.update_forward_refs()


def model_remove_all_but_type(model):
    fields = model.__fields__
    validators = {"__validators__": model.__validators__}
    no_link_fields = {key: item for key, item in fields.items() if key == "type"}
    new_model = create_model(f"{model.__name__}OnlyType")
    new_model.__fields__ = no_link_fields
    new_model.__validators__ = model.__validators__
    new_model.__pre_root_validators__ = model.__pre_root_validators__
    new_model.__post_root_validators__ = model.__post_root_validators__
    new_model.__config__ = model.__config__
    new_model.__config__.extra = Extra.allow
    return new_model


models = [Story, Spec]
model_name_2_model = {model.__name__: model for model in models}
model_name_2_model_only_type = {key: model_remove_all_but_type(value) for key, value in model_name_2_model.items()}


# validation logic
def remove_fields_need(need):
    out_dict = {}
    ignore_fields = ["type"] + link_types
    for key, value in need.items():
        if key not in ignore_fields:
            out_dict[key] = value
    return out_dict


def copy_model(model):
    new_model = create_model(f"{model.__name__}Copy")
    new_model.__fields__ = {key: value for key, value in model.__fields__.items()}
    new_model.__validators__ = {key: value for key, value in model.__validators__.items()}
    new_model.__pre_root_validators__ = [item for item in model.__pre_root_validators__]
    new_model.__post_root_validators__ = [item for item in model.__post_root_validators__]
    new_model.__config__ = model.__config__
    return new_model


def model_remove_links(model):
    fields = model.__fields__
    validators = {"__validators__": model.__validators__}
    no_link_fields = {key: item for key, item in fields.items() if key not in link_types}
    new_model = create_model(f"{model.__name__}NoLinks")
    new_model.__fields__ = no_link_fields
    new_model.__validators__ = model.__validators__
    new_model.__pre_root_validators__ = model.__pre_root_validators__
    new_model.__post_root_validators__ = model.__post_root_validators__
    new_model.__config__ = model.__config__
    return new_model


def model_modify_links(model):
    for key, value in model.__fields__.items():
        if key in link_types:
            new_fields = []
            for sub_field in value.sub_fields:
                # create field that just checks for type
                foo: int = Field(4, title="Foo is Great")
            value
    return model


def model_add_env(model):
    new_fields = {
        "all_needs": (Dict[str, Any], ...),
        "env": (Dict[str, Any], ...),
    }
    new_model = create_model(f"{model.__name__}WithNeeds", __base__=model, **new_fields)
    return new_model


def function(v, values):
    if v < 0:
        raise ValueError
    return v


def add_links_validator(model):
    validators = {"__validators__": model.__validators__}
    validator_function = validator("specs", allow_reuse=True)(function)
    validators["__validators__"]["validate_specs"] = validator_function
    fields = model.__fields__
    copied_fields = {key: (item.type_, ... if item.required else None) for key, item in fields.items()}
    return create_model(
        f"{model.__name__}NoLinks", **copied_fields, __validators__=validators, __config__=model.__config__
    )


def instantiate_links(cls, values: dict[str, ModelField]) -> dict[str, ModelField]:
    # available link types in sphinx-modeling:
    #  NeedType
    #  List[NeedType]
    #  Union[NeedType1, NeedType2, ...]
    #  List[Union[NeedType1, NeedType2, ...]]
    for name, links in values.items():
        if name in link_types and isinstance(links, list):
            field = cls.__fields__[name]
            type_str = field._type_display()
            resolved_needs = []
            for link in links:
                need = values["all_needs"][link]
            pass

    return values


def add_root_validator(model):
    model.__pre_root_validators__.append(instantiate_links)
    pass


model_orig_fields = {}

for need in needs.values():
    model = model_name_2_model[need["type"].title()]

    reduced_need = remove_fields_need(need)

    reduced_model = model_remove_links(model)
    # modified_links_model = model_modify_links(model)
    reduced_model_with_env = model_add_env(reduced_model)
    try:
        # reduced_model(**reduced_need, all_needs=needs)
        reduced_model_with_env(**reduced_need, all_needs=needs, env={})
    except ValidationError as exc:
        print(exc)

    model_duplicate = copy_model(model)
    add_root_validator(model_duplicate)
    try:
        # reduced_model(**reduced_need, all_needs=needs)
        model_duplicate(**need, all_needs=needs, env={})
    except ValidationError as exc:
        print(exc)

    # link_validated_model = add_links_validator(model)
    # try:
    #     link_validated_model(**reduced_need)
    # except ValidationError as exc:
    #     print("#### Error in link_validated_model(**reduced_need)")
    #     print(exc)

    # try:
    #     model(**need)
    # except ValidationError as exc:
    #     print("#### Error in model(**need)")
    #     print(exc)
