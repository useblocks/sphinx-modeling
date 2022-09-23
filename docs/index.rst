
Modeling for sphinx-needs
=========================

``Sphinx-Modeling`` allows the definition of models and constraints for objects defined with
`Sphinx-Needs <https://github.com/useblocks/sphinx-needs>`_. They can be validated during the Sphinx build.

`pydantic <https://github.com/pydantic/pydantic>`_ is used under the hood to validate all models.

Arbitrary constraints can be enforced such as:

- multiplicity of value fields (need options)
- multiplicity of link fields
- typed fields (string, regex, int, enums)
- no additional fields
- outgoing links must target specific need types or union of types
- need type must be nested within another need type
- need type must be part of a specific document or chapter/section
- custom validators

Motivation
==========

Requirements management with ``Sphinx-Needs`` and docs-as-code traditionally comes at the cost of complete freedom for developers. ``need_types``, ``needs_extra_options`` and ``needs_extra_links`` are global and all ``need_types`` can
use all ``needs_extra_options``/``needs_extra_options``.

This is a problem for organisations that want to enforce standards on objects.
Especially when migrating parts of the requirements management system to ``Sphinx-Needs`` it is crucial to enforce the same
constraints as defined in existing solutions. Doing so enables technological interoperability.

Planned features
================

Generation of the following ``Sphinx-Needs`` configurations from a model configuration:

- ``needs_types``
- ``needs_extra_options``
- ``needs_extra_links``

.. toctree::
   :maxdepth: 2
   :hidden:

   installation
   configuration
   contributing
   support
   changelog
