Installation
============

Using poetry
------------

.. code-block:: bash

    poetry add sphinx-needs-modeling

Using pip
---------

.. code-block:: bash

    pip install sphinx-needs-modeling

Using sources
-------------

.. code-block:: bash

    git clone https://github.com/useblocks/sphinx-needs-modeling
    cd sphinx-needs-modeling
    pip install .
    # or
    poetry install


Activation
----------

For final activation, please add `sphinx_needs_modeling` to the project's extension list of your **conf.py** file.

.. code-block:: python

   extensions = ["sphinx_needs_modeling",]

For the full configuration, please read :ref:`config`.

.. _install_plantuml:

PlantUML support
----------------

The model export uses `PlantUML <http://plantuml.com>`_ and the
Sphinx-extension `sphinxcontrib-plantuml <https://pypi.org/project/sphinxcontrib-plantuml/>`_ for generating the
diagrams.

Both must be available and correctly configured to work.


Install PlantUML
~~~~~~~~~~~~~~~~

1. Download the latest version of the plantuml.jar file:
   http://sourceforge.net/projects/plantuml/files/plantuml.jar/download
2. Make a new folder called ``utils`` inside your docs folder. Copy the ``plantuml.jar`` file into the ``utils`` folder.
3. Install the plantuml sphinx extension: ``pip install sphinxcontrib-plantuml``.
4. Add ``sphinxcontrib.plantuml`` to the sphinx extension list in ``conf.py``

.. code-block:: python

      extensions = ['sphinxcontrib.plantuml',
                    'sphinx_needs_modeling']


5. Configure plantuml in ``conf.py``

.. code-block:: python

  on_rtd = os.environ.get('READTHEDOCS') == 'True'
  if on_rtd:
      plantuml = 'java -Djava.awt.headless=true -jar /usr/share/plantuml/plantuml.jar'
  else:
      plantuml = 'java -jar %s' % os.path.join(os.path.dirname(__file__), "utils", "plantuml.jar"))

      plantuml_output_format = 'png'

The final configuration contains already a setup for building and deploying the documentation on
`ReadTheDocs <https://readthedocs.org/>`_.

ReadTheDocs provides ``plantuml.jar`` already on their system, so do not store it inside your source version control system.
