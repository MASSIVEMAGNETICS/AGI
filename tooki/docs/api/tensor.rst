Tensor Module
=============

The tensor module provides automatic differentiation capabilities with a NumPy backend
and optional GPU acceleration.

.. automodule:: victor_core.tensor
   :members:
   :undoc-members:
   :show-inheritance:

Tensor Class
------------

.. autoclass:: victor_core.tensor.Tensor
   :members:
   :special-members: __init__, __add__, __mul__, __matmul__, __pow__
   :undoc-members:
   :show-inheritance:

Activation Functions
--------------------

.. autofunction:: victor_core.tensor.relu
.. autofunction:: victor_core.tensor.sigmoid  
.. autofunction:: victor_core.tensor.tanh
.. autofunction:: victor_core.tensor.softmax

Loss Functions
--------------

.. autofunction:: victor_core.tensor.mse_loss
.. autofunction:: victor_core.tensor.binary_cross_entropy
.. autofunction:: victor_core.tensor.cross_entropy

Optimizers
----------

.. autoclass:: victor_core.tensor.Optimizer
   :members:
   :undoc-members:

.. autoclass:: victor_core.tensor.SGD
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: victor_core.tensor.Adam
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: victor_core.tensor.RMSprop
   :members:
   :undoc-members:
   :show-inheritance:

Context Managers
----------------

.. autofunction:: victor_core.tensor.no_grad
.. autofunction:: victor_core.tensor.set_grad_enabled
.. autofunction:: victor_core.tensor.grad_enabled
