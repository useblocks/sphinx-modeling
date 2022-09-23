.. _config:

Configuration
=============

All configurations take place in your project's **conf.py** file.

Activation
----------

Add **sphinx_modeling** to your extensions.

.. code-block:: python

   extensions = ["sphinx_modeling",]

Options
-------

All configuration options starts with the prefix ``modeling_`` for **Sphinx-Modeling**.


modeling_models
~~~~~~~~~~~~~~~
This option defines the list of user provided pydantic models.
Each pydantic model class must inherit from ``BaseModelNeeds``.

Default: ``[]``

.. code-block:: python

   class Story(BaseModelNeeds, extra=Extra.forbid):
      id: str
      type: typing.Literal["story"]
      active: Optional[needs_bool]

   class Spec(BaseModelNeeds, extra=Extra.forbid):
      id: pydantic.constr(regex=r'^SPEC_\w{3,}$')
      type: Literal["spec"]
      links: pydantic.conlist(Story, min_items=1, max_items=1)

   modeling_models = [Story, Spec]

modeling_remove_fields
~~~~~~~~~~~~~~~~~~~~~~

Need dictionary fields that shall be removed before passing each need dictionary to pydantic.
A common modeling approach is not not allow additional need fields using pydantic's ``Extra.forbid``.
In this case a need should not contain unused fields as they would appear as validation violations.

Default:

.. code-block:: python

   MODELING_REMOVE_FIELDS = [
      "docname",
      "external_css",
      "hide",
      "is_modified",
      "layout",
      "style",
      "type_color",
      "type_name",
      "type_prefix",
      "type_style",
   ]

Example:

.. code-block:: python

   modeling_remove_fields = MODELING_REMOVE_FIELDS + [
    "content",
    "full_title",
    "is_external",
    "is_need",
    "is_part",
   ]
