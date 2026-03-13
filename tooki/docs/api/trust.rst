Trust Module
============

The trust module implements the SAVE3 framework for secure module orchestration.

.. automodule:: victor_core.trust
   :members:
   :undoc-members:
   :show-inheritance:

Trust Model
-----------

.. autoclass:: victor_core.trust.TrustModelBeta
   :members:
   :undoc-members:
   :show-inheritance:

SAVE3 Envelope
--------------

.. autoclass:: victor_core.trust.SAVE3Envelope
   :members:
   :undoc-members:
   :show-inheritance:

Module Specification
--------------------

.. autoclass:: victor_core.trust.SAVE3ModuleSpec
   :members:
   :undoc-members:
   :show-inheritance:

Service Registry
----------------

.. autoclass:: victor_core.trust.LegoContext
   :members:
   :undoc-members:
   :show-inheritance:

Functions
---------

.. autofunction:: victor_core.trust.discover_specs
.. autofunction:: victor_core.trust.resolve_init_order
.. autofunction:: victor_core.trust.lego_build
.. autofunction:: victor_core.trust.wrap_spec

Exceptions
----------

.. autoexception:: victor_core.trust.Save3Error
.. autoexception:: victor_core.trust.SpecError
.. autoexception:: victor_core.trust.SignatureError
.. autoexception:: victor_core.trust.DependencyError
.. autoexception:: victor_core.trust.TrustError
