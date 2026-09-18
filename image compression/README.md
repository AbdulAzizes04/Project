# QuantumMedCompress
### A Scalable Quantum-Enhanced AI Model for Medical Image Compression and Optimization

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3114/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.1.1-red.svg)](https://pytorch.org/)
[![PennyLane](https://img.shields.io/badge/PennyLane-0.44.1-purple.svg)](https://pennylane.ai/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-cyan.svg)](https://react.dev/)
[![Tests](https://img.shields.io/badge/pytest-21%20passed-brightgreen.svg)]()

> **Medical Safety & Academic Disclaimer**: This software prototype is developed strictly for 4th-Year B.Tech engineering research and educational purposes. It has not been clinically certified by regulatory authorities (FDA/CE) and must never be utilized for patient diagnosis or medical treatment decisions.

---

## 📌 Project Overview

**QuantumMedCompress** is an end-to-end hybrid quantum-classical deep learning framework for medical image compression, optimization, and evaluation. It investigates whether integrating a Parameterized Quantum Circuit (PQC) into the bottleneck of a classical convolutional autoencoder can provide an effective compression-quality trade-off for medical images (Brain MRI, Chest X-Ray, CT scans).

### Key Highlights
- **Hybrid Quantum-Classical Autoencoder (HQCA)**: 4-layer CNN Encoder + 4-Qubit Variational Quantum Layer (PennyLane) + 4-layer Transposed CNN Decoder.
- **Real Binary `.qmc` Bitstream Compression**: Eliminates theoretical "floating-point vector" claims by performing true INT8 quantization, header encapsulation, and entropy coding to measure exact on-disk byte footprints.
- **Fair Baseline Comparison**: Evaluates head-to-head against Standard DCT-based JPEG (at matched bitrate) and Pure Classical Convolutional Autoencoders.
- **Full-Stack Demonstrable Application**: FastAPI backend with SQLite experiment logging paired with a modern React.js + Tailwind CSS UI for interactive before/after image inspection, distortion heatmaps, and comparative analytics.

---

## 🏛 Architecture Pipeline

```
Medical Image (64×64 Grayscale uint8)
      │
      ▼
Preprocessing & Normalization [0.0, 1.0]
      │
      ▼
Classical CNN Encoder (Conv2D blocks + LeakyReLU + AdaptivePool)
      │
      ▼
Classical Latent Bottleneck Vector z (Dim = 8)
      │
      ├──► [Baseline 1: Pure Classical Autoencoder] ──► Direct to Decoder
      │
      └──► [Proposed: Quantum-Enhanced Layer]
              │ (Linear projection to 4 rotation angles in [-pi, pi])
              ▼
           PennyLane 4-Qubit Variational Circuit
              • State Preparation: AngleEmbedding(RY, RZ) on 4 wires
              • Variational Rotations: 2 layers of RX(w0), RY(w1), RZ(w2)
              • Entanglement: Circular Ring CNOT Gates [0->1, 1->2, 2->3, 3->0]
              • Measurement: Pauli-Z Expectation Values ⟨Z_i⟩ in [-1.0, 1.0]
              • Residual Integration: z_enhanced = z_classical + alpha * Linear(⟨Z⟩)
              │
              ▼
Learned Binary Serializer (.qmc bitstream)
(Quantization to INT8 + Zlib Entropy Coding to Disk)
      │
      ▼
Classical CNN Decoder (Transposed Conv2D blocks + Sigmoid)
      │
      ▼
Reconstructed Medical Image (64×64 Grayscale uint8)
      │
      ▼
Evaluation Metrics Engine (MSE, PSNR dB, SSIM, CR, Storage Reduction %)
```

---

## 📂 Project Structure

```
QuantumMedCompress/
│
├── backend/
│   ├── main.py                     # FastAPI server entry point, static mounts & CORS
│   ├── config.py                   # Centralized configuration (seeds, paths, hyperparams)
│   ├── database.py                 # SQLite database schema, image records & run tracking
│   ├── api/
│   │   ├── upload.py               # Medical image upload & validation (/api/upload)
│   │   ├── compression.py          # Classical, Quantum, & JPEG compression (/api/compress)
│   │   └── evaluation.py           # Dashboard stats, model specs & experiment history
│   ├── models/
│   │   ├── encoder.py              # Classical CNN Encoder PyTorch Module
│   │   ├── decoder.py              # Classical CNN Decoder PyTorch Module
│   │   ├── quantum_layer.py        # PennyLane Parameterized Quantum Circuit Layer
│   │   └── quantum_autoencoder.py  # Classical & Hybrid Autoencoders + Compound SSIM Loss
│   ├── preprocessing/
│   │   └── image_processor.py      # Resizing, Grayscale conversion, Synthetic Phantom Gen
│   ├── serialization/
│   │   └── compressor.py           # True binary .qmc bitstream serializer & decompressor
│   ├── evaluation/
│   │   ├── metrics.py              # MSE, PSNR, SSIM, CR, Storage Reduction calculations
│   │   └── benchmark.py            # Automated multi-model comparative benchmarking
│   └── utils/
│       └── helpers.py              # Random seeding, standardized logging & file helpers
│
├── frontend/                       # Modern React.js + Tailwind CSS UI (Vite)
│   ├── src/
│   │   ├── components/             # Navbar, StatCard, ImageCompare, DifferenceMap
│   │   ├── pages/                  # Dashboard, Compress, Compare, Experiments, Architecture
│   │   ├── services/api.js         # API client communicating with FastAPI
│   │   ├── App.jsx
│   │   └── index.css
│   └── package.json
│
├── datasets/                       # Medical images & synthetic MRI phantom slices
├── saved_models/                   # Trained model weights (.pth)
├── experiments/
│   └── train.py                    # Unified training script with loss curve visualization
├── results/
│   ├── plots/                      # Generated loss curves & model comparison charts
│   ├── tables/                     # Benchmark comparison CSV exports
│   ├── compressed/                 # Serialized .qmc and .jpg binary payloads
│   ├── reconstructed/              # Output medical images
│   └── heatmaps/                   # Jet colormap distortion difference heatmaps
├── tests/                          # 21 Automated Pytest Unit & Integration tests
├── requirements.txt                # Pinned dependencies
├── FINAL_YEAR_PROJECT_REPORT_GUIDE.md # B.Tech Report, Viva Q&A, Algorithms & PPT Guide
└── README.md
```

---

## 🚀 Quickstart & Reproduction Guide

### 1. Environment Setup
```bash
# Clone or navigate to the directory
cd "d:/projects/image compression"

# Install Python requirements
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### 2. Run Automated Test Suite
Ensure all 21 unit tests pass across preprocessing, models, quantum circuits, metrics, serialization, and API routes:
```bash
pytest tests/ -v
```

### 3. Train Models
To train both Classical and Hybrid Quantum-Classical Autoencoders from scratch:
```bash
python experiments/train.py --model all --epochs 5 --batch-size 16
```
This automatically generates 160 synthetic brain phantom slices if not present, trains both models, saves `.pth` checkpoints to `saved_models/`, and creates `results/plots/training_loss_comparison.png`.

### 4. Run Benchmark Comparison
To evaluate Classical Autoencoder vs Hybrid Quantum Model vs JPEG on the test set:
```bash
python backend/evaluation/benchmark.py
```
Outputs `results/tables/benchmark_comparison.csv` and `results/plots/model_comparison_metrics.png`.

### 5. Launch Full-Stack Web Application
Run the backend and frontend servers in separate terminals:

**Terminal 1 (Backend API):**
```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
API Documentation available at: `http://127.0.0.1:8000/docs`

**Terminal 2 (Frontend UI):**
```bash
cd frontend
npm run dev
```
Open your browser at: `http://localhost:5173/`

---

## 📊 Evaluation Metrics Formulas

1. **Mean Squared Error (MSE)**:
   $$\text{MSE} = \frac{1}{M \times N} \sum_{i=1}^M \sum_{j=1}^N (I(i,j) - \hat{I}(i,j))^2$$

2. **Peak Signal-to-Noise Ratio (PSNR)**:
   $$\text{PSNR} = 10 \cdot \log_{10}\left(\frac{\text{MAX}_I^2}{\text{MSE}}\right)$$

3. **Structural Similarity Index (SSIM)**:
   $$\text{SSIM}(x, y) = \frac{(2\mu_x\mu_y + c_1)(2\sigma_{xy} + c_2)}{(\mu_x^2 + \mu_y^2 + c_1)(\sigma_x^2 + \sigma_y^2 + c_2)}$$

4. **True Compression Ratio (CR)**:
   $$\text{Compression Ratio} = \frac{\text{Original File Size (Bytes)}}{\text{Compressed File Size on Disk (Bytes)}}$$

5. **Storage Reduction Percentage**:
   $$\text{Storage Reduction (\%)} = \left(\frac{\text{Original Size} - \text{Compressed Size}}{\text{Original Size}}\right) \times 100$$

---

## ⚛️ Quantum Circuit Parameters
- **Simulator**: PennyLane `default.qubit` (analytic statevector simulation)
- **Number of Qubits**: 4 Qubits ($2^4 = 16$ state vector dimension)
- **Gate Topology**:
  - $R_y(\theta_i)$ Angle Preparation
  - Variational $R_x(\omega_0) R_y(\omega_1) R_z(\omega_2)$ Rotations (2 layers)
  - Circular Ring CNOT Entanglement
  - Pauli-Z Expectation Value $\langle Z_i \rangle \in [-1.0, 1.0]$ Readout
- **Residual Formulation**: $z_{\text{hybrid}} = z_{\text{classical}} + \alpha \cdot \text{Linear}(\langle Z \rangle)$
