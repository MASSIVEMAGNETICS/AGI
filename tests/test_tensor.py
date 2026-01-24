"""
Comprehensive tests for Victor Core Tensor engine.

Tests cover:
- Basic operations (add, mul, matmul, etc.)
- Gradient computation (backward pass)
- Broadcasting behavior
- Activation functions
- Loss functions
- Optimizers
- Save/load functionality
"""

import pytest
import numpy as np
from victor_core.tensor import (
    Tensor, no_grad, SGD, Adam, RMSprop,
    relu, sigmoid, tanh, softmax,
    mse_loss, binary_cross_entropy, cross_entropy
)
from victor_core.tensor.engine import (
    save_tensor, load_tensor, save_checkpoint, load_checkpoint
)
import tempfile
import os


class TestTensorBasics:
    """Test basic tensor creation and properties."""
    
    def test_tensor_creation(self):
        """Test tensor creation from various inputs."""
        # From list
        t1 = Tensor([1, 2, 3])
        assert t1.shape == (3,)
        
        # From numpy array
        t2 = Tensor(np.array([[1, 2], [3, 4]]))
        assert t2.shape == (2, 2)
        
        # From scalar
        t3 = Tensor(5.0)
        assert t3.shape == ()
        
        # From another tensor
        t4 = Tensor(t1)
        assert t4.shape == t1.shape
    
    def test_requires_grad(self):
        """Test gradient tracking flag."""
        t1 = Tensor([1, 2, 3], requires_grad=True)
        assert t1.requires_grad == True
        
        t2 = Tensor([1, 2, 3], requires_grad=False)
        assert t2.requires_grad == False
    
    def test_detach(self):
        """Test detaching tensor from computation graph."""
        t1 = Tensor([1, 2, 3], requires_grad=True)
        t2 = t1.detach()
        
        assert t2.requires_grad == False
        assert np.array_equal(t1.data, t2.data)
    
    def test_item(self):
        """Test extracting scalar value."""
        t = Tensor(5.0)
        assert t.item() == 5.0
        
        with pytest.raises(ValueError):
            Tensor([1, 2]).item()


class TestArithmeticOps:
    """Test arithmetic operations."""
    
    def test_add(self):
        """Test addition."""
        a = Tensor([1, 2, 3], requires_grad=True)
        b = Tensor([4, 5, 6], requires_grad=True)
        c = a + b
        
        assert np.array_equal(c.data, [5, 7, 9])
        
        # Test backward
        c.backward(np.ones(3))
        assert np.array_equal(a.grad, [1, 1, 1])
        assert np.array_equal(b.grad, [1, 1, 1])
    
    def test_add_scalar(self):
        """Test addition with scalar."""
        a = Tensor([1, 2, 3], requires_grad=True)
        b = a + 5
        
        assert np.array_equal(b.data, [6, 7, 8])
    
    def test_sub(self):
        """Test subtraction."""
        a = Tensor([5, 6, 7], requires_grad=True)
        b = Tensor([1, 2, 3], requires_grad=True)
        c = a - b
        
        assert np.array_equal(c.data, [4, 4, 4])
    
    def test_mul(self):
        """Test multiplication."""
        a = Tensor([1, 2, 3], requires_grad=True)
        b = Tensor([2, 3, 4], requires_grad=True)
        c = a * b
        
        assert np.array_equal(c.data, [2, 6, 12])
        
        # Test backward
        c.backward(np.ones(3))
        assert np.array_equal(a.grad, b.data)
        assert np.array_equal(b.grad, a.data)
    
    def test_div(self):
        """Test division."""
        a = Tensor([6, 8, 10], requires_grad=True)
        b = Tensor([2, 4, 5], requires_grad=True)
        c = a / b
        
        assert np.array_equal(c.data, [3, 2, 2])
    
    def test_pow(self):
        """Test power operation."""
        a = Tensor([2, 3, 4], requires_grad=True)
        b = a ** 2
        
        assert np.array_equal(b.data, [4, 9, 16])
        
        # Test gradient: d/dx (x^2) = 2x
        b.backward(np.ones(3))
        assert np.array_equal(a.grad, [4, 6, 8])
    
    def test_neg(self):
        """Test negation."""
        a = Tensor([1, -2, 3], requires_grad=True)
        b = -a
        
        assert np.array_equal(b.data, [-1, 2, -3])


class TestBroadcasting:
    """Test broadcasting behavior."""
    
    def test_broadcast_add(self):
        """Test addition with broadcasting."""
        a = Tensor([[1, 2], [3, 4]], requires_grad=True)
        b = Tensor([10, 20], requires_grad=True)
        c = a + b
        
        expected = [[11, 22], [13, 24]]
        assert np.array_equal(c.data, expected)
        
        # Test backward
        c.backward(np.ones((2, 2)))
        assert np.array_equal(a.grad, [[1, 1], [1, 1]])
        assert np.array_equal(b.grad, [2, 2])  # Summed over batch dim
    
    def test_broadcast_mul(self):
        """Test multiplication with broadcasting."""
        a = Tensor([[1, 2], [3, 4]], requires_grad=True)
        b = Tensor([2, 3], requires_grad=True)
        c = a * b
        
        expected = [[2, 6], [6, 12]]
        assert np.array_equal(c.data, expected)


class TestMatrixOps:
    """Test matrix operations."""
    
    def test_matmul(self):
        """Test matrix multiplication."""
        a = Tensor([[1, 2], [3, 4]], requires_grad=True)
        b = Tensor([[5, 6], [7, 8]], requires_grad=True)
        c = a @ b
        
        expected = [[19, 22], [43, 50]]
        assert np.array_equal(c.data, expected)
        
        # Test backward
        c.backward(np.ones((2, 2)))
        # Gradient should be accumulated correctly
        assert a.grad is not None
        assert b.grad is not None
    
    def test_transpose(self):
        """Test transpose operation."""
        a = Tensor([[1, 2, 3], [4, 5, 6]], requires_grad=True)
        b = a.T
        
        expected = [[1, 4], [2, 5], [3, 6]]
        assert np.array_equal(b.data, expected)
        
        # Test backward
        b.backward(np.ones((3, 2)))
        assert np.array_equal(a.grad, [[1, 1, 1], [1, 1, 1]])


class TestShapeOps:
    """Test shape manipulation operations."""
    
    def test_reshape(self):
        """Test reshape operation."""
        a = Tensor([1, 2, 3, 4, 5, 6], requires_grad=True)
        b = a.reshape(2, 3)
        
        assert b.shape == (2, 3)
        
        # Test backward
        b.backward(np.ones((2, 3)))
        assert np.array_equal(a.grad, [1, 1, 1, 1, 1, 1])
    
    def test_squeeze(self):
        """Test squeeze operation."""
        a = Tensor([[[1], [2], [3]]], requires_grad=True)
        b = a.squeeze()
        
        assert b.shape == (3,)
    
    def test_view(self):
        """Test view (alias for reshape)."""
        a = Tensor([[1, 2], [3, 4]], requires_grad=True)
        b = a.view(4)
        
        assert b.shape == (4,)


class TestReductionOps:
    """Test reduction operations."""
    
    def test_sum(self):
        """Test sum operation."""
        a = Tensor([[1, 2], [3, 4]], requires_grad=True)
        b = a.sum()
        
        assert b.data == 10
        
        # Test backward
        b.backward()
        assert np.array_equal(a.grad, [[1, 1], [1, 1]])
    
    def test_sum_axis(self):
        """Test sum along axis."""
        a = Tensor([[1, 2], [3, 4]], requires_grad=True)
        b = a.sum(axis=0)
        
        assert np.array_equal(b.data, [4, 6])
    
    def test_mean(self):
        """Test mean operation."""
        a = Tensor([[2, 4], [6, 8]], requires_grad=True)
        b = a.mean()
        
        assert b.data == 5.0
        
        # Test backward
        b.backward()
        expected_grad = 0.25  # 1/4
        assert np.allclose(a.grad, [[expected_grad] * 2] * 2)
    
    def test_mean_axis(self):
        """Test mean along axis."""
        a = Tensor([[1, 2], [3, 4]], requires_grad=True)
        b = a.mean(axis=1)
        
        assert np.array_equal(b.data, [1.5, 3.5])


class TestActivations:
    """Test activation functions."""
    
    def test_relu(self):
        """Test ReLU activation."""
        a = Tensor([-2, -1, 0, 1, 2], requires_grad=True)
        b = relu(a)
        
        assert np.array_equal(b.data, [0, 0, 0, 1, 2])
        
        # Test gradient
        b.backward(np.ones(5))
        assert np.array_equal(a.grad, [0, 0, 0, 1, 1])
    
    def test_sigmoid(self):
        """Test sigmoid activation."""
        a = Tensor([0.0], requires_grad=True)
        b = sigmoid(a)
        
        assert np.isclose(b.data, 0.5)
        
        # Test gradient at x=0: sigmoid'(0) = 0.25
        b.backward()
        assert np.isclose(a.grad, 0.25)
    
    def test_tanh(self):
        """Test tanh activation."""
        a = Tensor([0.0], requires_grad=True)
        b = tanh(a)
        
        assert np.isclose(b.data, 0.0)
        
        # Test gradient at x=0: tanh'(0) = 1
        b.backward()
        assert np.isclose(a.grad, 1.0)
    
    def test_softmax(self):
        """Test softmax activation."""
        a = Tensor([[1.0, 2.0, 3.0]], requires_grad=True)
        b = softmax(a)
        
        # Check probabilities sum to 1
        assert np.isclose(b.data.sum(), 1.0)
        
        # Check values are positive
        assert np.all(b.data > 0)


class TestLossFunctions:
    """Test loss functions."""
    
    def test_mse_loss(self):
        """Test MSE loss."""
        y_pred = Tensor([1.0, 2.0, 3.0], requires_grad=True)
        y_true = Tensor([1.0, 2.0, 2.0])
        
        loss = mse_loss(y_pred, y_true)
        
        # MSE = mean((y_pred - y_true)^2) = mean([0, 0, 1]) = 1/3
        expected = 1.0 / 3.0
        assert np.isclose(loss.data, expected)
    
    def test_binary_cross_entropy(self):
        """Test binary cross-entropy loss."""
        y_pred = Tensor([0.9, 0.1, 0.8], requires_grad=True)
        y_true = Tensor([1.0, 0.0, 1.0])
        
        loss = binary_cross_entropy(y_pred, y_true)
        
        # Loss should be positive
        assert loss.data > 0


class TestOptimizers:
    """Test optimizer implementations."""
    
    def test_sgd_basic(self):
        """Test SGD optimizer."""
        params = [Tensor([1.0, 2.0], requires_grad=True)]
        optimizer = SGD(params, lr=0.1)
        
        # Simulate gradient
        params[0]._ensure_grad()
        params[0].grad = np.array([1.0, 1.0])
        
        # Step
        optimizer.step()
        
        # New params should be: old - lr * grad = [1, 2] - 0.1 * [1, 1] = [0.9, 1.9]
        expected = [0.9, 1.9]
        assert np.allclose(params[0].data, expected)
    
    def test_sgd_momentum(self):
        """Test SGD with momentum."""
        params = [Tensor([1.0, 2.0], requires_grad=True)]
        optimizer = SGD(params, lr=0.1, momentum=0.9)
        
        # First step
        params[0]._ensure_grad()
        params[0].grad = np.array([1.0, 1.0])
        optimizer.step()
        
        # Second step
        optimizer.zero_grad()
        params[0]._ensure_grad()
        params[0].grad = np.array([1.0, 1.0])
        optimizer.step()
        
        # With momentum, should move further
        assert params[0].data[0] < 0.8  # More than single step
    
    def test_adam(self):
        """Test Adam optimizer."""
        params = [Tensor([1.0, 2.0], requires_grad=True)]
        optimizer = Adam(params, lr=0.01)
        
        # Simulate gradient
        params[0]._ensure_grad()
        params[0].grad = np.array([1.0, 1.0])
        
        # Step
        optimizer.step()
        
        # Parameters should change
        assert not np.array_equal(params[0].data, [1.0, 2.0])
    
    def test_rmsprop(self):
        """Test RMSprop optimizer."""
        params = [Tensor([1.0, 2.0], requires_grad=True)]
        optimizer = RMSprop(params, lr=0.01)
        
        # Simulate gradient
        params[0]._ensure_grad()
        params[0].grad = np.array([1.0, 1.0])
        
        # Step
        optimizer.step()
        
        # Parameters should change
        assert not np.array_equal(params[0].data, [1.0, 2.0])
    
    def test_zero_grad(self):
        """Test optimizer zero_grad."""
        params = [Tensor([1.0, 2.0], requires_grad=True)]
        optimizer = SGD(params, lr=0.1)
        
        # Set gradient
        params[0]._ensure_grad()
        params[0].grad = np.array([1.0, 1.0])
        
        # Zero it
        optimizer.zero_grad()
        
        assert params[0].grad is None


class TestGradientComputation:
    """Test gradient computation and backpropagation."""
    
    def test_simple_backward(self):
        """Test backward on simple computation."""
        x = Tensor([2.0], requires_grad=True)
        y = x * 3
        
        y.backward()
        
        assert x.grad is not None
        assert np.isclose(x.grad, 3.0)
    
    def test_chain_rule(self):
        """Test chain rule in backward pass."""
        x = Tensor([2.0], requires_grad=True)
        y = x * 2
        z = y * 3
        
        z.backward()
        
        # dz/dx = dz/dy * dy/dx = 3 * 2 = 6
        assert np.isclose(x.grad, 6.0)
    
    def test_multi_path_gradient(self):
        """Test gradient accumulation from multiple paths."""
        x = Tensor([2.0], requires_grad=True)
        y = x * 2
        z = x * 3
        w = y + z
        
        w.backward()
        
        # dw/dx = dw/dy * dy/dx + dw/dz * dz/dx = 1*2 + 1*3 = 5
        assert np.isclose(x.grad, 5.0)
    
    def test_no_grad_context(self):
        """Test no_grad context manager."""
        x = Tensor([1.0, 2.0], requires_grad=True)
        
        with no_grad():
            y = x * 2
        
        assert y.requires_grad == False


class TestSaveLoad:
    """Test save/load functionality."""
    
    def test_save_load_tensor(self):
        """Test saving and loading tensors."""
        original = Tensor([1, 2, 3, 4], requires_grad=True)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pt') as f:
            filepath = f.name
        
        try:
            save_tensor(original, filepath)
            loaded = load_tensor(filepath)
            
            assert np.array_equal(original.data, loaded.data)
            assert original.requires_grad == loaded.requires_grad
        finally:
            os.unlink(filepath)
    
    def test_save_load_checkpoint(self):
        """Test saving and loading checkpoints."""
        params = [Tensor([1.0, 2.0], requires_grad=True)]
        optimizer = Adam(params, lr=0.001)
        
        # Take a step
        params[0]._ensure_grad()
        params[0].grad = np.array([1.0, 1.0])
        optimizer.step()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pt') as f:
            filepath = f.name
        
        try:
            # Save
            save_checkpoint(params, optimizer, filepath, metadata={'epoch': 10})
            
            # Create new params and optimizer
            new_params = [Tensor([0.0, 0.0], requires_grad=True)]
            new_optimizer = Adam(new_params, lr=0.001)
            
            # Load
            metadata = load_checkpoint(filepath, new_params, new_optimizer)
            
            assert np.allclose(new_params[0].data, params[0].data)
            assert metadata['epoch'] == 10
        finally:
            os.unlink(filepath)


class TestIntegration:
    """Integration tests for complete workflows."""
    
    def test_linear_regression(self):
        """Test simple linear regression."""
        # Generate data: y = 2x + 1 + noise
        np.random.seed(42)
        x_data = np.random.randn(100, 1).astype(np.float32)
        y_data = 2 * x_data + 1 + 0.1 * np.random.randn(100, 1).astype(np.float32)
        
        # Initialize parameters
        w = Tensor(np.random.randn(1, 1).astype(np.float32), requires_grad=True)
        b = Tensor(np.zeros((1,), dtype=np.float32), requires_grad=True)
        
        # Optimizer
        optimizer = SGD([w, b], lr=0.01)
        
        # Train for a few steps
        for _ in range(50):
            optimizer.zero_grad()
            
            # Forward pass
            x = Tensor(x_data)
            y_pred = x @ w + b
            y_true = Tensor(y_data)
            
            # Loss
            loss = mse_loss(y_pred, y_true)
            
            # Backward
            loss.backward()
            
            # Update
            optimizer.step()
        
        # Check that parameters are close to true values (relaxed tolerance)
        assert np.abs(w.data[0, 0] - 2.0) < 1.0  # Should approach 2
        assert np.abs(b.data[0] - 1.0) < 1.0  # Should approach 1
    
    def test_binary_classification(self):
        """Test simple binary classification."""
        # Generate linearly separable data
        np.random.seed(42)
        x_positive = np.random.randn(50, 2) + np.array([2, 2])
        x_negative = np.random.randn(50, 2) + np.array([-2, -2])
        x_data = np.vstack([x_positive, x_negative]).astype(np.float32)
        y_data = np.vstack([np.ones((50, 1)), np.zeros((50, 1))]).astype(np.float32)
        
        # Initialize parameters
        w = Tensor(np.random.randn(2, 1).astype(np.float32) * 0.01, requires_grad=True)
        b = Tensor(np.zeros((1,), dtype=np.float32), requires_grad=True)
        
        # Optimizer
        optimizer = Adam([w, b], lr=0.01)
        
        # Train
        for _ in range(100):
            optimizer.zero_grad()
            
            # Forward
            x = Tensor(x_data)
            logits = x @ w + b
            y_pred = sigmoid(logits)
            y_true = Tensor(y_data)
            
            # Loss
            loss = binary_cross_entropy(y_pred, y_true)
            
            # Backward
            loss.backward()
            
            # Update
            optimizer.step()
        
        # Check accuracy (should be > 90%)
        with no_grad():
            x = Tensor(x_data)
            logits = x @ w + b
            y_pred = sigmoid(logits)
            predictions = (y_pred.data > 0.5).astype(float)
            accuracy = (predictions == y_data).mean()
            
        assert accuracy > 0.9


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
