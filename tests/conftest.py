"""
Pytest configuration and shared fixtures for Victor Core tests.
"""

import pytest
import numpy as np
from victor_core.tensor import Tensor
from victor_core.trust import LegoContext, SAVE3ModuleSpec
from victor_core.tensor.engine import set_grad_enabled


@pytest.fixture
def small_tensor():
    """Create a small tensor for testing."""
    return Tensor([[1.0, 2.0], [3.0, 4.0]], requires_grad=True)


@pytest.fixture
def scalar_tensor():
    """Create a scalar tensor."""
    return Tensor(5.0, requires_grad=True)


@pytest.fixture
def zero_tensor():
    """Create a zero tensor."""
    return Tensor(np.zeros((3, 3)), requires_grad=True)


@pytest.fixture
def lego_context():
    """Create a fresh LegoContext."""
    return LegoContext()


@pytest.fixture
def sample_module_spec():
    """Create a sample module specification."""
    return SAVE3ModuleSpec(
        module_id="test.module",
        name="Test Module",
        version="v1.0.0",
        provides=["test.capability"],
        requires=[],
        description="Test module for unit tests"
    )


@pytest.fixture(autouse=True)
def reset_grad_state():
    """Reset gradient tracking state between tests."""
    # Store and restore original gradient state
    original = set_grad_enabled(True)
    yield
    set_grad_enabled(original)


def approx_equal(a: np.ndarray, b: np.ndarray, rtol: float = 1e-5, atol: float = 1e-7) -> bool:
    """
    Check if two arrays are approximately equal.
    
    Args:
        a: First array
        b: Second array
        rtol: Relative tolerance
        atol: Absolute tolerance
        
    Returns:
        True if arrays are approximately equal
    """
    return np.allclose(a, b, rtol=rtol, atol=atol)


# Make approx_equal available as pytest helper
pytest.approx_equal = approx_equal
