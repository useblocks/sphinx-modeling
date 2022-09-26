.. _modeling_guidelines:

Modeling guidelines
===================

Validators
----------

.. warning::
    The currently used Pydantic version may raise an exception when custom validators:

    .. code-block:: text

          File "pydantic/class_validators.py", line 145, in pydantic.class_validators._prepare_validator
        TypeError: unsupported operand type(s) for +: 'NoneType' and 'str'

    The affected code uses ``__func__.__module__``. The ``__module__`` class variable is not guaranteed to be defined.
    A workaround is to set the `allow_reuse <https://pydantic-docs.helpmanual.io/usage/validators/#reuse-validators>`_ flag to ``True`` like shown in the examples below.

Context variables
-----------------

User defined `root validators <https://pydantic-docs.helpmanual.io/usage/validators/#root-validators>`_ have access to the following variables in ``values``:

- ``all_needs`` the needs dictionary
- ``env`` the Sphinx environment

Pydantic v1 does not offer context variables, so
`this workaround <https://github.com/pydantic/pydantic/issues/1170#issuecomment-575233689>`_ is used.
The feature is however planned for pydantic v2 (see `here <https://github.com/pydantic/pydantic/issues/1549>`__ and
`here <https://pydantic-docs.helpmanual.io/blog/pydantic-v2/#validation-context>`__).

Validate linked need
--------------------

This model checks whether linked stories have the right value in their ``active`` field:

.. code-block:: python

    class Story(BaseModelNeeds, extra=Extra.forbid):
        id: str
        type: Literal["story"]
        active: Literal["True", "False"]


    class Spec(BaseModelNeeds, extra=Extra.forbid):
        id: str
        type: Literal["spec"]
        links: conlist(Story, min_items=1, max_items=1)

        @validator("links", allow_reuse=True)
        def linked_story_active(value):
            if value[0].active == "False":
                raise ValueError("Can only link active stories")
            return value

This RST

.. code-block:: rst

    .. story:: Test story 1
       :id: US_001
       :active: False

    .. spec:: Test spec1
       :id: SP_001
       :links: US_001

leads to the warnings:

.. code-block:: text

    WARNING: Model validation: failed for need SP_001
    WARNING: 1 validation error for Spec
    links
      Can only link active stories (type=value_error)    

