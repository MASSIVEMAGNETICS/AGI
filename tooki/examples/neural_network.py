"""
Example: Training a Neural Network
===================================

Demonstrates training a simple neural network for binary classification
using the Victor Core tensor engine.
"""

import numpy as np
from victor_core.tensor import Tensor, Adam, relu, sigmoid, binary_cross_entropy, no_grad

print("=" * 60)
print("Victor Core - Neural Network Training Example")
print("=" * 60)

# Set random seed for reproducibility
np.random.seed(42)

# 1. Generate synthetic data
print("\n1. Generating Synthetic Data")
print("-" * 40)

# Create linearly separable data
n_samples = 200
n_features = 2

# Class 0: centered at (-2, -2)
X_class0 = np.random.randn(n_samples // 2, n_features) + np.array([-2, -2])

# Class 1: centered at (2, 2)
X_class1 = np.random.randn(n_samples // 2, n_features) + np.array([2, 2])

# Combine data
X = np.vstack([X_class0, X_class1]).astype(np.float32)
y = np.vstack([np.zeros((n_samples // 2, 1)), 
                np.ones((n_samples // 2, 1))]).astype(np.float32)

# Shuffle
indices = np.random.permutation(n_samples)
X = X[indices]
y = y[indices]

print(f"Dataset size: {n_samples} samples")
print(f"Features: {n_features}")
print(f"Class distribution: {(y == 0).sum()} negative, {(y == 1).sum()} positive")

# 2. Define network architecture
print("\n2. Defining Network Architecture")
print("-" * 40)

# Simple 2-layer network: 2 -> 8 -> 1
hidden_size = 8

# Initialize parameters
W1 = Tensor(np.random.randn(n_features, hidden_size).astype(np.float32) * 0.1, 
            requires_grad=True)
b1 = Tensor(np.zeros((hidden_size,), dtype=np.float32), requires_grad=True)

W2 = Tensor(np.random.randn(hidden_size, 1).astype(np.float32) * 0.1, 
            requires_grad=True)
b2 = Tensor(np.zeros((1,), dtype=np.float32), requires_grad=True)

parameters = [W1, b1, W2, b2]

print(f"Layer 1: {n_features} -> {hidden_size} (with ReLU)")
print(f"Layer 2: {hidden_size} -> 1 (with Sigmoid)")
print(f"Total parameters: {sum(p.data.size for p in parameters)}")

# 3. Training
print("\n3. Training Network")
print("-" * 40)

# Hyperparameters
n_epochs = 100
learning_rate = 0.01
batch_size = 32

# Optimizer
optimizer = Adam(parameters, lr=learning_rate)

# Training loop
print(f"Training for {n_epochs} epochs...")

for epoch in range(n_epochs):
    epoch_loss = 0.0
    n_batches = 0
    
    # Mini-batch training
    for i in range(0, n_samples, batch_size):
        batch_X = X[i:i+batch_size]
        batch_y = y[i:i+batch_size]
        
        # Zero gradients
        optimizer.zero_grad()
        
        # Forward pass
        X_tensor = Tensor(batch_X)
        
        # Layer 1
        hidden = relu(X_tensor @ W1 + b1)
        
        # Layer 2
        logits = hidden @ W2 + b2
        predictions = sigmoid(logits)
        
        # Compute loss
        y_tensor = Tensor(batch_y)
        loss = binary_cross_entropy(predictions, y_tensor)
        
        # Backward pass
        loss.backward()
        
        # Update parameters
        optimizer.step()
        
        epoch_loss += loss.data.item()
        n_batches += 1
    
    # Print progress
    avg_loss = epoch_loss / n_batches
    if (epoch + 1) % 10 == 0:
        print(f"Epoch {epoch+1:3d}/{n_epochs}: Loss = {avg_loss:.4f}")

# 4. Evaluation
print("\n4. Evaluating Model")
print("-" * 40)

with no_grad():
    # Forward pass on entire dataset
    X_tensor = Tensor(X)
    
    # Layer 1
    hidden = relu(X_tensor @ W1 + b1)
    
    # Layer 2
    logits = hidden @ W2 + b2
    predictions = sigmoid(logits)
    
    # Convert to class predictions
    y_pred = (predictions.data > 0.5).astype(float)
    
    # Compute accuracy
    accuracy = (y_pred == y).mean()
    
    print(f"Test Accuracy: {accuracy * 100:.2f}%")
    
    # Confusion matrix
    true_positives = ((y_pred == 1) & (y == 1)).sum()
    true_negatives = ((y_pred == 0) & (y == 0)).sum()
    false_positives = ((y_pred == 1) & (y == 0)).sum()
    false_negatives = ((y_pred == 0) & (y == 1)).sum()
    
    print("\nConfusion Matrix:")
    print(f"  True Positives:  {int(true_positives)}")
    print(f"  True Negatives:  {int(true_negatives)}")
    print(f"  False Positives: {int(false_positives)}")
    print(f"  False Negatives: {int(false_negatives)}")

# 5. Save model
print("\n5. Saving Model")
print("-" * 40)

from victor_core.tensor.engine import save_checkpoint

checkpoint_path = "/tmp/neural_net_model.pt"
save_checkpoint(parameters, optimizer, checkpoint_path, 
                metadata={'epochs': n_epochs, 'accuracy': float(accuracy)})

print(f"Model saved to: {checkpoint_path}")

print("\n" + "=" * 60)
print("Training completed successfully!")
print("=" * 60)
