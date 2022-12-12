.. _modeling_guidelines:

Modeling guidelines
===================

Model definition
----------------

.. admonition:: Handling in versions <= 0.1.1
    :collapsible:

    The validation logic passes each need object to Pydantic. The need type is used to look up the correct model in
    the configuration list :ref:`modeling_models`. sphinx-modeling uses an implicit logic to derive the modeling class
    from the need type. Some examples for how need types are converted to class names::
        
        impl -> Impl
        Swspec -> Swspec
        SwSpec -> SwSpec
        sw-spec -> SwSpec
        sw_spec -> SwSpec
        sw_Spec -> SwSpec
        sw1_Spec -> Sw1Spec
        1sw_spec -> SwSpec
        IPAddress -> IpAddress
        SPEC -> Spec

    The logic splits the need type on non-identifier symbols and underscores and removes leading digits.
    Then it runs `.title() <https://docs.python.org/3/library/stdtypes.html#str.title>`_ on all items and joins them
    together.

    .. note::
        Please make sure the mapping of model names to need types is unambiguous.
        Each model name can only map to exactly one need type.

Each Sphinx-Needs object has a field ``type`` that stores the used RST directive.
Each need ``type`` has exactly one Pydantic model mapped, to configure it use :ref:`modeling_models`.

Base class
----------

Each user provided Pydantic model can inherit from ``BaseModelNeeds``.
When doing so custom validators get access to :ref:`context_vars`.

Need structure
--------------

Each need is represented as a dictionary in Sphinx-Needs that holds

- extra option fields
- link fields
- back link fields
- internal fields

.. admonition:: Need dictionary example
    :collapsible:

    .. code-block:: python

        need = {
            "docname": "index",
            "doctype": "",
            "lineno": 1,
            "target_node": "<target: >",
            "external_url": None,
            "content_node": "<Need: <paragraph...>>",
            "type": "test",
            "type_name": "Test Case",
            "type_prefix": "TC_",
            "type_color": "#DCB239",
            "type_style": "node",
            "status": None,
            "tags": [],
            "constraints": [],
            "constraints_passed": None,
            "constraints_results": {},
            "id": "TC_001",
            "title": "Test test1",
            "full_title": "Test test1",
            "content": "Test case content",
            "collapse": None,
            "diagram": None,
            "style": None,
            "layout": "",
            "template": None,
            "pre_template": None,
            "post_template": None,
            "hide": False,
            "delete": None,
            "jinja_content": None,
            "parts": {},
            "is_part": False,
            "is_need": True,
            "parent_need": {
                "docname": "index",
                "doctype": ".rst",
                "lineno": 25,
                "target_node": "<target: >",
                "more": "fields",
            },
            "is_external": False,
            "external_css": "external_link",
            "is_modified": False,
            "modifications": 0,
            "active": "",
            "impact": "",
            "importance": "",
            "owner": "",
            "priority": "",
            "query": "",
            "specific": "",
            "max_amount": "",
            "max_content_lines": "",
            "id_prefix": "",
            "user": "",
            "created_at": "",
            "updated_at": "",
            "closed_at": "",
            "service": "",
            "url": "",
            "avatar": "",
            "params": "",
            "prefix": "",
            "url_postfix": "",
            "hidden": "",
            "duration": "",
            "completion": "",
            "has_dead_links": "",
            "has_forbidden_dead_links": "",
            "parent_needs": [
                {
                    "docname": "index",
                    "doctype": ".rst",
                    "lineno": 25,
                    "target_node": "<target: >",
                    "more": "fields",
                }
            ],
            "parent_needs_back": [],
            "links": [],
            "links_back": [],
            "sections": ["TEST DOCUMENT MODELING"],
            "section_name": "TEST DOCUMENT MODELING",
            "signature": "",
        }

User provided Pydantic models can basically validate all available fields.

Handled fields
--------------

Internal fields are commonly not of interest for validation and can be removed before passing the dictionary to
Pydantic. The parameter :ref:`modeling_remove_fields` can be used to configure what gets removed.

Fields that hold back links like ``links_back`` are automatically created by Sphinx-Needs.
If validation is not needed, they can be removed by activating :ref:`modeling_remove_backlinks`.

Above settings are particularly helpful if the setting
`Extra.forbid <https://docs.pydantic.dev/usage/model_config/>`_ is used:

.. code-block:: python

    class Story(BaseModelNeeds, extra=Extra.forbid):
        id: str
        type: Literal["story"]

.. _need_link_resolution:

Need link resolution
--------------------

.. admonition:: Handling in versions <= 0.1.1
    :collapsible:

    Up to version ``0.1.1`` Sphinx-Modeling handled ``ModelFields`` that validated linked need objects using
    a ``pre`` root validator in ``BaseModelNeeds``. It resolved target needs and instantiated the model directly.
    This had 3 major downsides:

    - circular need link loops resulted in an error as Pydantic cannot handle those (also not planned for Pydantic v2)
    - hidden and complicated logic

Sphinx-Needs represents link field values as list of need ID strings. The only exception from this is the field
``parent_need`` which holds the nested need parent ID directly (without a list).

When activating the flag :ref:`modeling_resolve_links` all need IDs get replaced with the target need's dicionary.
That makes it possible to write Pydantic models that validate against linked need fields.

.. warning::
    Keep in mind that Pydantic does not support circular references. The linked needs can form circular
    link reference chains, which is not a problem in Python dictionaries. Pydantic models
    that validate against nested dictionaries can however lead to max recursion depth errors.

Here are some examples how a link validation can look like.

Link validation examples
------------------------

Multiplicity 1..1
~~~~~~~~~~~~~~~~~

.. code-block:: python

    class Story(BaseModelNeeds):
        id: str
        type: Literal["story"]

    class Spec(BaseModelNeeds):
        id: str
        type: Literal["spec"]
        links: conlist(Story, min_items=1, max_items=1)

In above example each ``Spec`` must link to exactly 1 ``Story``.

Multiplicity 0..1
~~~~~~~~~~~~~~~~~

.. code-block:: python

    class Story(BaseModelNeeds):
        id: str
        type: Literal["story"]

    class Spec(BaseModelNeeds):
        id: str
        type: Literal["spec"]
        links: conlist(Story, min_items=0, max_items=1)

In above example each ``Spec`` can optionally link to exactly 1 ``Story``.

Multiplicity 0..*
~~~~~~~~~~~~~~~~~

.. code-block:: python

    class Story(BaseModelNeeds):
        id: str
        type: Literal["story"]

    class Spec(BaseModelNeeds):
        id: str
        type: Literal["spec"]
        links: List[Story]

In above example each ``Spec`` can link to 0 or more need type ``Story``.

Multiplicity 1..*
~~~~~~~~~~~~~~~~~

.. code-block:: python

    class Story(BaseModelNeeds):
        id: str
        type: Literal["story"]

    class Spec(BaseModelNeeds):
        id: str
        type: Literal["spec"]
        links: conlist(Story, min_items=1)

In above example each ``Spec`` can link to 1 or more ``Story`` need types.

Union
~~~~~

.. code-block:: python

    class Story(BaseModelNeeds):
        id: str
        type: Literal["story"]

    class Spec(BaseModelNeeds):
        id: str
        type: Literal["spec"]

    class Impl(BaseModelNeeds):
        id: str
        type: Literal["impl"]
        links: List[Union[Story, Spec]]

In above example each ``Impl`` must link to 0 or more need types ``Story`` or ``Spec``.

Union with multiplicity
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    class Story(BaseModelNeeds):
        id: str
        type: Literal["story"]

    class Spec(BaseModelNeeds):
        id: str
        type: Literal["spec"]

    class Impl(BaseModelNeeds):
        id: str
        type: Literal["impl"]
        links: Union[conlist(Story, min_items=1, max_items=1), conlist(Spec, min_items=2)]

In above example each ``Impl`` must either link to exactly 1 ``Story`` or to 2 or more ``Spec`` need items.

.. _linked_need_validation:

Linked need validation
----------------------

In above examples, the linked need types are directly used as Pydantic nested models.
That means a linked need is only valid if all linked need fields can be validated.
It also implies validation errors gets duplicated because the linked need is validated multiple times.

To avoid the validation error duplication and also to avoid circular link loops, additional Pydantic models can be
defined just for the links. Imaging the following cicular link situation: 

.. code-block:: python

    class Story(BaseModelNeeds):
        id: str
        type: Literal["story"]
        impls: List[Impl]

    class Spec(BaseModelNeeds):
        id: str
        type: Literal["spec"]
        story: List[Story]

    class Impl(BaseModelNeeds):
        id: str
        type: Literal["impl"]
        links: List[Spec]

It can be resolved like this:

.. code-block:: python

    class LinkedStory(BaseModel):
        type: Literal["story"]

    class LinkedSpec(BaseModel):
        type: Literal["spec"]

    class LinkedImpl(BaseModel):
        type: Literal["impl"]

    class Story(BaseModelNeeds):
        id: str
        type: Literal["story"]
        impls: List[LinkedImpl]

    class Spec(BaseModelNeeds):
        id: str
        type: Literal["spec"]
        story: List[LinkedStory]

    class Impl(BaseModelNeeds):
        id: str
        type: Literal["impl"]
        links: List[LinkedSpec]

The solution will just check whether the linked type is correct.
The example can also be used to validate more fields of linked needs by adding more fields to the ``Linked*`` classes.

Custom validators
-----------------

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

.. warning::
    The currently used Pydantic version may raise an exception for custom validators:

    .. code-block:: text

          File "pydantic/class_validators.py", line 145, in pydantic.class_validators._prepare_validator
        TypeError: unsupported operand type(s) for +: 'NoneType' and 'str'

    The affected code uses ``__func__.__module__``. The ``__module__`` class variable is not guaranteed to be defined.
    A workaround is to set the `allow_reuse <https://pydantic-docs.helpmanual.io/usage/validators/#reuse-validators>`_ 
    flag to ``True`` like shown in the examples below.


.. _context_vars:

Context variables
-----------------

User defined `root validators <https://pydantic-docs.helpmanual.io/usage/validators/#root-validators>`_ have access to the following variables in ``values``:

- ``all_needs`` the needs dictionary
- ``env`` the Sphinx environment

Pydantic v1 does not yet offer context variables, so
`this workaround <https://github.com/pydantic/pydantic/issues/1170#issuecomment-575233689>`_ is used.
The feature is however planned for Pydantic v2 (see `here <https://github.com/pydantic/pydantic/issues/1549>`__ and
`here <https://pydantic-docs.helpmanual.io/blog/pydantic-v2/#validation-context>`__).
