**Complete documentation**: http://sphinx-modeling.readthedocs.io/en/latest/

Introduction
============

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

Planned features
================

Generation of the following ``Sphinx-Needs`` configurations from a model configuration:

- ``needs_types``
- ``needs_extra_options``
- ``needs_extra_links``

Installation
============

Using poetry
------------
::

    poetry add sphinx-modeling


Using pip
---------
::

    pip install sphinx-modeling

Using sources
-------------
::

    git clone https://github.com/useblocks/sphinx-modeling
    cd sphinx-modeling
    pip install .

Activation
----------

Add **sphinx_modeling** to your extensions::

    extensions = ["sphinx_needs", "sphinx_modeling", ]
