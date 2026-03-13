"""
Example: Basic Tensor Operations
=================================

Demonstrates basic tensor creation, operations, and gradient computation.
"""

import numpy as np
from victor_core.tensor import Tensor, relu, sigmoid

print("=" * 60)
print("Victor Core Tensor Engine - Basic Operations")
print("=" * 60)

# 1. Tensor Creation
print("\n1. Creating Tensors")
print("-" * 40)

x = Tensor([1.0, 2.0, 3.0], requires_grad=True)
y = Tensor([[1, 2], [3, 4]], requires_grad=True)
z = Tensor(5.0, requires_grad=True)

print(f"Vector: {x}")
print(f"Matrix: {y}")
print(f"Scalar: {z}")

# 2. Basic Operations
print("\n2. Basic Operations")
print("-" * 40)

a = Tensor([1.0, 2.0, 3.0], requires_grad=True)
b = Tensor([4.0, 5.0, 6.0], requires_grad=True)

c = a + b
print(f"Addition: {a.data} + {b.data} = {c.data}")

d = a * b
print(f"Multiplication: {a.data} * {b.data} = {d.data}")

e = a ** 2
print(f"Power: {a.data} ** 2 = {e.data}")

# 3. Matrix Operations
print("\n3. Matrix Operations")
print("-" * 40)

m1 = Tensor([[1, 2], [3, 4]], requires_grad=True)
m2 = Tensor([[5, 6], [7, 8]], requires_grad=True)

m3 = m1 @ m2
print(f"Matrix multiplication:\n{m1.data}\n@\n{m2.data}\n=\n{m3.data}")

m4 = m1.T
print(f"Transpose:\n{m1.data}\n=>\n{m4.data}")

# 4. Reduction Operations
print("\n4. Reduction Operations")
print("-" * 40)

t = Tensor([[1, 2, 3], [4, 5, 6]], requires_grad=True)
print(f"Original: {t.data}")
print(f"Sum: {t.sum().data}")
print(f"Mean: {t.mean().data}")
print(f"Sum axis=0: {t.sum(axis=0).data}")
print(f"Mean axis=1: {t.mean(axis=1).data}")

# 5. Shape Operations
print("\n5. Shape Operations")
print("-" * 40)

t1 = Tensor([1, 2, 3, 4, 5, 6], requires_grad=True)
print(f"Original shape: {t1.shape}")

t2 = t1.reshape(2, 3)
print(f"Reshaped to (2, 3): {t2.data}")

t3 = t2.reshape(3, 2)
print(f"Reshaped to (3, 2): {t3.data}")

# 6. Activations
print("\n6. Activation Functions")
print("-" * 40)

x = Tensor([-2, -1, 0, 1, 2], requires_grad=True)
print(f"Input: {x.data}")
print(f"ReLU: {relu(x).data}")
print(f"Sigmoid: {sigmoid(x).data}")

# 7. Gradient Computation
print("\n7. Gradient Computation")
print("-" * 40)

# Simple example: f(x) = x^2
x = Tensor([2.0], requires_grad=True)
y = x ** 2
print(f"Function: f(x) = x^2")
print(f"x = {x.data}")
print(f"y = f(x) = {y.data}")

y.backward()
print(f"Gradient df/dx = 2x = {x.grad}")

# More complex: f(x) = (x * 3 + 2)^2
x = Tensor([1.0], requires_grad=True)
y = ((x * 3) + 2) ** 2
print(f"\nFunction: f(x) = (3x + 2)^2")
print(f"x = {x.data}")
print(f"y = f(x) = {y.data}")

y.backward()
print(f"Gradient df/dx = 2(3x+2)*3 = {x.grad}")
print(f"Expected at x=1: 2(3*1+2)*3 = 30")

# 8. Broadcasting
print("\n8. Broadcasting")
print("-" * 40)

a = Tensor([[1, 2, 3]], requires_grad=True)  # Shape: (1, 3)
b = Tensor([[1], [2], [3]], requires_grad=True)  # Shape: (3, 1)
c = a + b  # Broadcasting to (3, 3)

print(f"a shape: {a.shape}, values:\n{a.data}")
print(f"b shape: {b.shape}, values:\n{b.data}")
print(f"a + b shape: {c.shape}, values:\n{c.data}")

c.backward(np.ones((3, 3)))
print(f"Gradient of a: {a.grad}")  # Summed over broadcast dimensions
print(f"Gradient of b: {b.grad}")

print("\n" + "=" * 60)
print("All examples completed successfully!")
print("=" * 60)
