Installation
============

Using poetry
------------

.. code-block:: bash

    poetry add sphinx-modeling

Using pip
---------

.. code-block:: bash

    pip install sphinx-modeling

Using sources
-------------

.. code-block:: bash

    git clone https://github.com/useblocks/sphinx-modeling
    cd sphinx-modeling
    pip install .
    # or
    poetry install


Activation
----------

For final activation, please add `sphinx_modeling` to the project's extension list of your **conf.py** file.

.. code-block:: python

   extensions = ["sphinx_modeling",]

For the full configuration, please read :ref:`config`.

.. _install_plantuml:

PlantUML support
----------------

A feature is planned for Sphinx-Modeling to export the defined user models into a diagram.
For this `PlantUML <http://plantuml.com>`_ will be used and the
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

      extensions = ['sphinx_needs', 'sphinx_modeling', 'sphinxcontrib.plantuml', ]


5. Configure plantuml in ``conf.py``

.. code-block:: python

    plantuml = f'java -jar {os.path.join(os.path.dirname(__file__), "utils", "plantuml.jar")}'
    plantuml_output_format = 'png'
