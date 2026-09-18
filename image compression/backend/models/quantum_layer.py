"""
PennyLane Parameterized Quantum Circuit (PQC) Layer for Feature Enhancement.
Includes angle state encoding, variational rotational gates (RY, RZ, RX),
entanglement (ring CNOT), and Pauli-Z expectation measurements.
"""

import math
from typing import Tuple
import torch
import torch.nn as nn
import pennylane as qml

from backend.config import NUM_QUBITS, NUM_QUANTUM_LAYERS, QUANTUM_DEVICE, LATENT_DIM
from backend.utils.helpers import setup_logger

logger = setup_logger("QuantumLayer")

# Initialize PennyLane statevector device
dev = qml.device(QUANTUM_DEVICE, wires=NUM_QUBITS)

@qml.qnode(dev, interface="torch", diff_method="backprop")
def _variational_quantum_circuit(inputs: torch.Tensor, weights: torch.Tensor):
    """
    Quantum Circuit:
    inputs: tensor of shape (Batch, NUM_QUBITS) or (NUM_QUBITS,) in [-pi, pi]
    weights: tensor of shape (NUM_QUANTUM_LAYERS, NUM_QUBITS, 3) representing (RX, RY, RZ) angles
    
    Returns:
    List of expectation values [ <Z_0>, <Z_1>, ..., <Z_{N-1}> ]
    """
    # 1. Quantum State Preparation (Native Batched Angle Embedding)
    qml.AngleEmbedding(inputs, wires=range(NUM_QUBITS), rotation="Y")

    # 2. Variational Entangling Layers
    for layer in range(NUM_QUANTUM_LAYERS):
        # Parameterized Single-Qubit Rotations
        for i in range(NUM_QUBITS):
            qml.RX(weights[layer, i, 0], wires=i)
            qml.RY(weights[layer, i, 1], wires=i)
            qml.RZ(weights[layer, i, 2], wires=i)
        
        # Entanglement (Ring / Circular CNOT Topology)
        for i in range(NUM_QUBITS):
            qml.CNOT(wires=[i, (i + 1) % NUM_QUBITS])

    # 3. Measurement: Pauli-Z expectation values on all qubits
    return [qml.expval(qml.PauliZ(i)) for i in range(NUM_QUBITS)]


class QuantumFeatureLayer(nn.Module):
    """
    Differentiable PyTorch Quantum Module wrapping the PennyLane variational circuit.
    Features:
    - Linear projection from classical latent vector (e.g. 8) to 4 qubit angles
    - PennyLane variational quantum circuit with ring CNOT entanglement
    - Post-measurement projection back to latent dimension
    - Learnable residual skip connection to ensure stable training and avoid barren plateaus
    """
    def __init__(
        self,
        latent_dim: int = LATENT_DIM,
        num_qubits: int = NUM_QUBITS,
        num_layers: int = NUM_QUANTUM_LAYERS
    ):
        super().__init__()
        self.latent_dim = latent_dim
        self.num_qubits = num_qubits
        self.num_layers = num_layers

        # Map classical latent variables into angle space [-pi, pi]
        self.pre_linear = nn.Linear(latent_dim, num_qubits)

        # Variational parameters: (num_layers, num_qubits, 3)
        weight_shapes = {"weights": (num_layers, num_qubits, 3)}
        # PennyLane TorchLayer handles vectorized batch evaluation
        self.qnode_layer = qml.qnn.TorchLayer(_variational_quantum_circuit, weight_shapes)

        # Map quantum expectation values back to latent space
        self.post_linear = nn.Linear(num_qubits, latent_dim)

        # Learnable residual scale parameter (initialized to 0.1 for smooth start)
        self.alpha = nn.Parameter(torch.tensor(0.1, dtype=torch.float32))

    def forward(self, z_classical: torch.Tensor) -> torch.Tensor:
        """
        Forward Pass:
        z_classical: (Batch, latent_dim)
        Returns: z_enhanced: (Batch, latent_dim)
        """
        # 1. Project to qubit dimension and scale to [-pi, pi]
        angles = torch.pi * torch.tanh(self.pre_linear(z_classical))

        # 2. Quantum Circuit evaluation: yields (Batch, num_qubits) in [-1.0, 1.0]
        q_expvals = self.qnode_layer(angles)

        # 3. Post-measurement projection
        q_features = self.post_linear(q_expvals)

        # 4. Residual Integration: keeps primary latent representation stable
        z_enhanced = z_classical + self.alpha * q_features
        return z_enhanced
