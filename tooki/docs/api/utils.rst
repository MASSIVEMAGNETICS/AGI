Utilities Module
================

The utilities module provides helper functions for logging, configuration, and state management.

.. automodule:: victor_core.utils
   :members:
   :undoc-members:
   :show-inheritance:

Logging
-------

.. autofunction:: victor_core.utils.setup_logger

Configuration
-------------

.. autoclass:: victor_core.utils.Config
   :members:
   :undoc-members:
   :show-inheritance:

State Management
----------------

.. autoclass:: victor_core.utils.StateManager
   :members:
   :undoc-members:
   :show-inheritance:

File I/O
--------

.. autofunction:: victor_core.utils.ensure_dir
.. autofunction:: victor_core.utils.safe_save_json
.. autofunction:: victor_core.utils.load_json
.. autofunction:: victor_core.utils.save_pickle
.. autofunction:: victor_core.utils.load_pickle

Timing
------

.. autoclass:: victor_core.utils.Timer
   :members:
   :undoc-members:
   :show-inheritance:

Formatting
----------

.. autofunction:: victor_core.utils.format_bytes
.. autofunction:: victor_core.utils.format_number

Deprecation
-----------

.. autofunction:: victor_core.utils.deprecated
