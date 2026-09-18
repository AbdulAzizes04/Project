"""
Unit tests for PennyLane QuantumFeatureLayer.
Validates forward shapes, expectation values, and end-to-end backpropagation gradients.
"""

import torch
import torch.optim as optim
import pytest

from backend.models.quantum_layer import QuantumFeatureLayer
from backend.config import NUM_QUBITS, NUM_QUANTUM_LAYERS, LATENT_DIM

def test_quantum_layer_forward_shape():
    layer = QuantumFeatureLayer(latent_dim=LATENT_DIM, num_qubits=NUM_QUBITS, num_layers=NUM_QUANTUM_LAYERS)
    batch_size = 4
    dummy_input = torch.randn(batch_size, LATENT_DIM)
    
    output = layer(dummy_input)
    assert output.shape == (batch_size, LATENT_DIM)
    assert not torch.isnan(output).any()

def test_quantum_layer_gradients():
    layer = QuantumFeatureLayer(latent_dim=LATENT_DIM, num_qubits=NUM_QUBITS, num_layers=NUM_QUANTUM_LAYERS)
    dummy_input = torch.randn(2, LATENT_DIM, requires_grad=True)
    
    output = layer(dummy_input)
    target = torch.zeros_like(output)
    loss = torch.nn.functional.mse_loss(output, target)
    
    loss.backward()
    
    # Check that input gradients exist
    assert dummy_input.grad is not None
    assert not torch.isnan(dummy_input.grad).any()
    
    # Check that quantum variational weights have non-zero gradients
    q_weights = layer.qnode_layer.weights
    assert q_weights.grad is not None
    assert torch.sum(torch.abs(q_weights.grad)) > 0

def test_quantum_optimizer_step():
    layer = QuantumFeatureLayer(latent_dim=LATENT_DIM, num_qubits=NUM_QUBITS, num_layers=NUM_QUANTUM_LAYERS)
    optimizer = optim.Adam(layer.parameters(), lr=0.01)
    
    initial_weights = layer.qnode_layer.weights.clone()
    
    dummy_input = torch.randn(3, LATENT_DIM)
    output = layer(dummy_input)
    loss = output.sum()
    
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    
    # Weights should change after step
    assert not torch.equal(initial_weights, layer.qnode_layer.weights)
