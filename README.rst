**Complete documentation**: http://sphinx-modeling.readthedocs.io/en/latest/

Introduction
============

``Sphinx-Modeling`` allows the definition of models and constraints for objects defined with
`Sphinx-Needs <https://github.com/useblocks/sphinx-needs>`_. They can be validated during the Sphinx build.

Under the hood `pydantic <https://github.com/pydantic/pydantic>`_ is used to provide and validate all models.

Arbitrary constraints can be enforced such as:

- multiplicity of value fields (need options)
- multiplicity of link fields
- typed fields (string, regex, int, enums)
- no additional fields
- outgoing links must target specific need types
- need type must be nested within another need type
- need type must be part of a specific document or chapter/section

Additionally this extensions enables the generation of the following ``Sphinx-Needs`` configurations:

- ``needs_types``
- ``needs_extra_options``
- ``needs_extra_links``

Motivation
==========

Requirements management with ``Sphinx-Needs`` and docs-as-code traditionally comes at the cost of complete freedom for developers. ``need_types``, ``needs_extra_options`` and ``needs_extra_links`` are global and all ``need_types`` can
use all ``needs_extra_options``.

This is a problem for organisations that want to enforce standards on the defined objects.
Especially when migrating parts of the requirements management system to ``Sphinx-Needs`` it is crucial to enforce the same
constraints as defined by existing solutions. Doing so enables a technological interoperability between solutions.


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

    extensions = ["sphinx-needs", "sphinx_modeling", ]
