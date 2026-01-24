Victor AGI Core Documentation
================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   quickstart
   api/index
   guides/index
   architecture

Welcome to Victor AGI Core
---------------------------

Victor AGI Core is a production-grade foundation for artificial general intelligence systems,
featuring a unified tensor/autograd engine, secure module orchestration (SAVE3), and advanced
cognitive architectures.

Key Features
------------

* **Tensor Engine**: Complete automatic differentiation with NumPy and GPU support
* **SAVE3 Framework**: Secure, trust-weighted module orchestration
* **Cognitive Modules**: Reasoning, metacognition, and emergence systems
* **Zero Dependencies**: Only NumPy required for core functionality
* **Production Ready**: Comprehensive tests, security scans, type hints

Quick Links
-----------

* :doc:`quickstart` - Get started in 5 minutes
* :doc:`api/index` - Complete API reference
* :doc:`guides/index` - Tutorials and guides
* :doc:`architecture` - System architecture

Installation
------------

.. code-block:: bash

   pip install numpy
   
   # Optional: GPU acceleration
   pip install cupy-cuda11x
   
   # Optional: Development tools
   pip install pytest sphinx

Quick Example
-------------

.. code-block:: python

   from victor_core.tensor import Tensor, Adam, relu
   
   # Create tensors with autograd
   x = Tensor([[1.0, 2.0]], requires_grad=True)
   weights = Tensor([[0.5], [0.5]], requires_grad=True)
   
   # Forward pass
   y = relu(x @ weights)
   loss = y.mean()
   
   # Backward pass - automatic differentiation
   loss.backward()
   
   # Optimization
   optimizer = Adam([weights], lr=0.01)
   optimizer.step()

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
