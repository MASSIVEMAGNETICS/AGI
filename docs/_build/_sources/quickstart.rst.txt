Quickstart Guide
================

This guide will get you up and running with Victor AGI Core in just a few minutes.

Installation
------------

Victor AGI Core has minimal dependencies:

.. code-block:: bash

   # Core functionality (NumPy only)
   pip install numpy
   
   # GPU acceleration (optional)
   pip install cupy-cuda11x  # or cupy-cuda12x for CUDA 12
   
   # Development tools (optional)
   pip install pytest sphinx

Basic Tensor Operations
-----------------------

Creating Tensors
^^^^^^^^^^^^^^^^

.. code-block:: python

   from victor_core.tensor import Tensor
   
   # From lists
   x = Tensor([1, 2, 3], requires_grad=True)
   
   # From NumPy arrays
   import numpy as np
   y = Tensor(np.random.randn(3, 3), requires_grad=True)
   
   # Scalars
   z = Tensor(5.0, requires_grad=True)

Operations
^^^^^^^^^^

.. code-block:: python

   # Arithmetic
   a = Tensor([1, 2, 3], requires_grad=True)
   b = Tensor([4, 5, 6], requires_grad=True)
   
   c = a + b      # Addition
   d = a * b      # Multiplication
   e = a @ b.T    # Matrix multiplication
   f = a ** 2     # Power
   
   # Reductions
   sum_val = a.sum()
   mean_val = a.mean()
   
   # Shape operations
   reshaped = a.reshape(3, 1)
   transposed = reshaped.T

Automatic Differentiation
--------------------------

.. code-block:: python

   from victor_core.tensor import Tensor
   
   # Define computation
   x = Tensor([2.0], requires_grad=True)
   y = x ** 2 + 3 * x + 1
   
   # Compute gradients
   y.backward()
   
   print(f"dy/dx = {x.grad}")  # dy/dx = 2x + 3 = 7

Training a Neural Network
-------------------------

.. code-block:: python

   from victor_core.tensor import Tensor, Adam, relu, binary_cross_entropy
   import numpy as np
   
   # Generate synthetic data
   X_train = np.random.randn(100, 10).astype(np.float32)
   y_train = (X_train.sum(axis=1, keepdims=True) > 0).astype(np.float32)
   
   # Initialize parameters
   W1 = Tensor(np.random.randn(10, 20) * 0.1, requires_grad=True)
   b1 = Tensor(np.zeros(20), requires_grad=True)
   W2 = Tensor(np.random.randn(20, 1) * 0.1, requires_grad=True)
   b2 = Tensor(np.zeros(1), requires_grad=True)
   
   # Optimizer
   optimizer = Adam([W1, b1, W2, b2], lr=0.01)
   
   # Training loop
   for epoch in range(100):
       # Forward pass
       X = Tensor(X_train)
       hidden = relu(X @ W1 + b1)
       logits = hidden @ W2 + b2
       predictions = 1 / (1 + Tensor(np.exp(-logits.data)))
       
       # Loss
       loss = binary_cross_entropy(predictions, Tensor(y_train))
       
       # Backward pass
       optimizer.zero_grad()
       loss.backward()
       optimizer.step()
       
       if epoch % 20 == 0:
           print(f"Epoch {epoch}: Loss = {loss.item():.4f}")

SAVE3 Trust Framework
---------------------

.. code-block:: python

   from victor_core.trust import TrustModelBeta, SAVE3Envelope, lego_build
   
   # Trust scoring with time decay
   trust = TrustModelBeta(decay_halflife=3600.0)
   trust.record_success("service_a", score_gain=10, latency_ms=50)
   trust.record_failure("service_b", score_penalty=15)
   
   print(f"Service A trust: {trust.get_trust('service_a')}")
   
   # Secure envelopes with HMAC signatures
   envelope = SAVE3Envelope(
       module_id="my.module",
       module_name="My Module",
       module_version="v1.0.0",
       payload={"config": {"timeout": 30}}
   )
   envelope.finalize(secret=b"shared_secret")
   envelope.verify(secret=b"shared_secret")
   
   # Module orchestration
   result = lego_build("/path/to/modules")
   print(f"Capabilities: {result['capabilities_published']}")

GPU Acceleration
----------------

.. code-block:: python

   from victor_core.tensor import Tensor
   from victor_core.tensor.gpu import to_gpu, to_cpu
   
   # Move tensors to GPU
   x = Tensor([1, 2, 3], requires_grad=True)
   x_gpu = to_gpu(x)
   
   # Perform GPU operations
   y_gpu = x_gpu ** 2
   
   # Move back to CPU
   y_cpu = to_cpu(y_gpu)

Cognitive Modules
-----------------

.. code-block:: python

   from victor_core.cognitive import ReasoningEngine, MetacognitiveLoop
   
   # Reasoning system
   reasoner = ReasoningEngine()
   result = reasoner.deduce(premises=["All humans are mortal", "Socrates is human"])
   print(result.conclusion)  # "Socrates is mortal"
   
   # Metacognitive monitoring
   metacog = MetacognitiveLoop()
   performance = metacog.monitor(task_results)
   if performance.confidence < 0.7:
       metacog.adjust_strategy()

Next Steps
----------

* Read the :doc:`api/index` for complete API documentation
* Explore :doc:`guides/index` for in-depth tutorials
* Check :doc:`architecture` to understand the system design
