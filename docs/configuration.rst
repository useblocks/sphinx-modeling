.. _config:

Configuration
=============

All configurations take place in your project's **conf.py** file.

Activation
----------

Add **sphinx_modeling** to your extensions:

.. code-block:: python

   extensions = ["sphinx_needs", "sphinx_modeling", ]

Options
-------

All configuration options starts with the prefix ``modeling_`` for Sphinx-Modeling.

.. _modeling_models:

modeling_models
~~~~~~~~~~~~~~~

This option defines the list of user provided pydantic models.
Each pydantic model class must inherit from ``BaseModelNeeds`` which can be imported as follows

.. code-block:: python

   from sphinx_modeling.modeling.main import BaseModelNeeds

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

The repository contains a `full example <https://github.com/useblocks/sphinx-modeling/blob/main/tests/doc_test/doc_modeling/conf.py>`_. More examples and details can be found in the :ref:`modeling_guidelines`.

.. _modeling_remove_fields:

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

   from sphinx_modeling.modeling.defaults import MODELING_REMOVE_FIELDS

   modeling_remove_fields = MODELING_REMOVE_FIELDS + [
      "content",
      "full_title",
      "is_external",
      "is_need",
      "is_part",
   ]

.. _modeling_remove_backlinks:

modeling_remove_backlinks
~~~~~~~~~~~~~~~~~~~~~~~~~

Flag indicating whether to remove back referencing link fields from need dictionaries before passing on to pydantic.
This is an addition to :ref:`modeling_remove_fields` so the backlinks don't have to be listed separately.
Commonly they should also not be part of the validation models.

Default: ``True``

.. _modeling_resolve_links:

modeling_resolve_links
~~~~~~~~~~~~~~~~~~~~~~

Flag to replace linked need IDs with the linked need dictionary itself.

Sphinx-Needs uses list of strings to represent outgoing and incoming need links.
Each string is a need ID which uniquely identifies the linked need.
To validate outgoing or incoming need links, Pydantic models can either validate the need IDs or
the target need dictionary - which also includes the need ID.
Commonly it is preferrable to validate various linked need fields such as:

- must be of type 'story'
- must be in status 'in_progress' or 'done'

Setting this configuration parameter to ``True`` will replace all need ID strings with the corresponding
target need dictionary.

.. admonition:: Circular loops
   :class: warning

   Keep in mind Pydantic does **not** support circular references. Replacing need IDs with the target need
   dictionary might lead to circular references which is perfectly fine in Python but not for Pydantic.
   This happens if e.g. a ``test`` references a ``spec`` which references a ``story`` which then links
   to the same ``test`` again. To avoid this create dedicated models with a reduced field set for linked
   need validation. See the :ref:`modeling_guidelines` for more information.

