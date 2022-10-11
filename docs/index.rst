
Modeling for sphinx-needs
=========================

``Sphinx-Modeling`` allows the definition of models and constraints for objects defined with
`Sphinx-Needs <https://github.com/useblocks/sphinx-needs>`_. They can be validated during the Sphinx build.

`pydantic <https://github.com/pydantic/pydantic>`_ is used under the hood to validate all models.

Arbitrary constraints can be enforced such as:

- value constraints for need options
- multiplicity of need link options
- typed fields (string, regex, int, enums)
- allow or disallow additional options
- outgoing links must target specific need types or union of types
- need type must be nested within another need type (via ``parent_need``)
- need type must be part of a specific document or chapter/section
- custom validators

.. warning:: This Sphinx extension is in an early stage and subject to breaking changes.

Motivation
==========

Requirements management with ``Sphinx-Needs`` and docs-as-code traditionally comes at the cost of complete freedom for developers. ``need_types``, ``needs_extra_options`` and ``needs_extra_links`` are global and all ``need_types`` can
use all ``needs_extra_options``/``needs_extra_links`` by default.

This is a problem for organizations that want to enforce well defined (UML) standards on objects.
Especially when migrating parts of the requirements management system to ``Sphinx-Needs`` it is crucial to be
consistent with existing solutions. Doing so enables technological interoperability.

More reasons to use sphinx-modeling are:

* defining model constraints (typed links, multiplicity, allowed attributes, allowed values etc) as part of your model
  definition (and not as `need_warnings`). This leaves `need_warnings` with the load of doing only data relevant checks
  later. That is, reduce glue and duplication as much as possible.
* automatic visualization of typed model (planned feature)
* self contained need definitions which does not leave types, options, links and warnings scattered (planned feature)
* user-documentation of meta-model (automatically create readable textual documentation on the types, its allowed
  values etc. Can be combined with additional docstring documentation as part of model definition if needed)
* possibility to use the typed model in external tools (VsCode Extension, Linter etc.)
* possibility to auto-generate
  `needs_ide_directive_snippets <https://sphinxcontrib-needs.readthedocs.io/en/latest/configuration.html#needs-ide-directive-snippets>`_ (planned feature)


Planned features
================

* Generation of the following ``Sphinx-Needs`` configurations from a model configuration:

  * ``needs_types``
  * ``needs_extra_options``
  * ``needs_extra_links``

* Visualization of the model (e.g. with PlantUML)
* Use the model as source for IDE extensions

.. toctree::
   :maxdepth: 2
   :hidden:

   installation
   configuration
   modeling
   contributing
   support
   license
   changelog
