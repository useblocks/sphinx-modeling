{%- macro issue(nr) -%}
`Issue #{{ nr }} <https://github.com/useblocks/sphinx-modeling/issues/{{ nr }}>`_
{%- endmacro -%}
{%- macro pr(nr) -%}
`PR #{{ nr }} <https://github.com/useblocks/sphinx-modeling/pull/{{ nr }}>`_
{%- endmacro -%}

.. _changelog:

Changelog
=========

.. _Unreleased Changes: https://github.com/useblocks/sphinx-modeling/compare/0.2.0...HEAD
.. _0.2.0: http://github.com/useblocks/sphinx-modeling/compare/0.1.1...0.2.0
.. _0.1.1: http://github.com/useblocks/sphinx-modeling/compare/0.1.0...0.1.1
.. _0.1.0: https://github.com/useblocks/sphinx-modeling/tree/0.1.0
.. _Keep a Changelog: https://keepachangelog.com/en/1.0.0/
.. _Semantic Versioning: https://semver.org/spec/v2.0.0.html

All notable *functional* changes to this project will be documented in this file.

The format is based on `Keep a Changelog`_.

Unreleased
------------

Please see all `Unreleased Changes`_ for more information.

`0.2.0`_ - 2022-12-12
---------------------

Added
~~~~~

- Circular link loops ({{ issue(22) }}, {{ pr(25) }})
- Early output of warnings ({{ issue(21) }}, {{ pr(27) }})

Changed
~~~~~~~

- Add new ignore fields ``doctype``, ``arch`` ({{ issue(23) }}, {{ pr(25) }})
- Dict type for ``modeling_models`` ({{ issue(16) }}, {{ pr(26) }})

Fixed
~~~~~

- handle need types with non-identifier characters ({{ issue(16) }}, {{ pr(19) }})

`0.1.1`_ - 2022-09-28
---------------------

Fixed
~~~~~

- correct handling of modeling_remove_backlinks ({{ pr(10) }})

`0.1.0`_ - 2022-09-27
---------------------

Added
~~~~~

- Initial extension version
- Initial start of the changelog
