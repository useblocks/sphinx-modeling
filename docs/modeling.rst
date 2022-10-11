.. _modeling_guidelines:

Modeling guidelines
===================

Model names
-----------

The validation logic passes each need object to Pydantic. The need type is used to look up the correct model in
the configuration list :ref:`modeling_models`. sphinx-modeling uses an implicit logic to derive the modeling class
from the need type. Some examples for how need types are converted to class names::
    
    test -> Test
    SwReq -> Swreq
    sw-req -> Swreq
    1sw-req -> Swreq
    sw_req -> Sw_Req

The logic removes all non-identifier symbols (allowed are a-zA-Z) and leading digits, then runs
`.title() <https://docs.python.org/3/library/stdtypes.html#str.title>`_ on the string.

Base class
----------

Each user provided Pydantic model must inherit from ``BaseModelNeeds``.

Need link resolution
--------------------

The base class ``BaseModelNeeds`` features a root validator of type ``pre`` that runs before any other validators.
It ensures that linked needs will be provided as nested models, so a user model can directly define need links:

.. code-block:: python

    class Story(BaseModelNeeds):
        id: str
        type: Literal["story"]

    class Spec(BaseModelNeeds):
        id: str
        type: Literal["spec"]

    class Impl(BaseModelNeeds):
        id: str
        type: Literal["spec"]
        links: conlist(Union[Story, Spec] , min_items=1, max_items=1)

In above example each ``Impl`` must link to exactly one ``Story`` or ``Spec``.

Custom validators
-----------------

.. warning::
    The currently used Pydantic version may raise an exception for custom validators:

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

Pydantic v1 does not yet offer context variables, so
`this workaround <https://github.com/pydantic/pydantic/issues/1170#issuecomment-575233689>`_ is used.
The feature is however planned for Pydantic v2 (see `here <https://github.com/pydantic/pydantic/issues/1549>`__ and
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

