# B.Tech Final-Year Project Comprehensive Academic Deliverables
## Project Title: A Scalable Quantum-Enhanced AI Model for Medical Image Compression and Optimization (QuantumMedCompress)

---

## 1. Project Abstract
Modern diagnostic medicine relies heavily on high-resolution imaging modalities such as Magnetic Resonance Imaging (MRI), Computed Tomography (CT), and Chest Radiography (X-ray). While indispensable for clinical decision-making, the exponential growth of Picture Archiving and Communication Systems (PACS) poses severe transmission bandwidth bottlenecks and long-term cloud storage costs. Conventional lossy compression methods (such as JPEG and JPEG 2000) introduce high-frequency blocking and ringing artifacts that compromise fine anatomical tissue contrast. This project proposes **QuantumMedCompress**, a hybrid quantum-classical deep learning framework designed to investigate whether Parameterized Quantum Circuits (PQC) integrated into the latent space of a classical convolutional autoencoder can provide an effective compression-quality trade-off. 

The system maps standardized 64×64 grayscale medical slices into a compact 8-dimensional continuous latent space via a deep classical CNN encoder. This latent representation is transformed and processed on a 4-qubit quantum simulator using angle state preparation, parameterized single-qubit rotations, and circular ring entanglement before measuring Pauli-Z expectation values. A residual skip mechanism feeds the enhanced representation into a classical transposed convolutional decoder. Crucially, the project introduces a true binary `.qmc` file serialization engine utilizing INT8 quantization and entropy coding to measure real-world on-disk byte footprints rather than theoretical vector lengths. Experimental results demonstrate over 98% storage reduction relative to uncompressed raw bitmaps while maintaining structural integrity (PSNR ~15–16 dB, SSIM ~0.5), providing a realistic, reproducible baseline for quantum-assisted medical data optimization.

---

## 2. Problem Statement
Medical imaging data repositories are expanding at unprecedented rates. Storing and transmitting volumetric DICOM studies over constrained hospital networks introduces significant latency. Although standard lossy compression algorithms achieve reasonable compression ratios, they do not exploit semantic anatomical structure and often degrade subtle pathology boundaries. Conversely, while theoretical Quantum Machine Learning (QML) promises enhanced representational capacity via Hilbert-space entanglement, existing literature frequently suffers from:
1. Impractical NISQ assumptions attempting to encode entire multi-megapixel images directly into thousands of physical qubits.
2. Abstract "latent vector" claims without implementing genuine on-disk bitstream serialization.
3. Lack of direct, reproducible head-to-head benchmarking against standard JPEG baselines.

Therefore, there is an urgent need for a computationally realistic, runnable hybrid quantum-classical architecture that operates on standardized medical images and evaluates true disk storage reduction against reconstruction quality metrics.

---

## 3. Project Objectives
1. **Design a Practical Hybrid Architecture**: Implement a modular hybrid model combining classical CNN spatial encoders/decoders with a 4-qubit Parameterized Quantum Circuit (PQC) running on PennyLane.
2. **Eliminate Barren Plateaus & Gradient Dissipation**: Formulate a residual quantum integration mechanism to preserve continuous backpropagation gradients on standard CPU/GPU development environments.
3. **Build True Binary Bitstream Serialization**: Implement an actual `.qmc` (Quantum Medical Compressed) binary format with quantization and entropy coding to verify true disk storage reduction.
4. **Conduct Rigorous Head-to-Head Benchmarking**: Evaluate and contrast the proposed Hybrid Quantum model against Pure Classical Autoencoders and standard DCT-based JPEG across MSE, PSNR, SSIM, Compression Ratio (CR), and Storage Reduction (%).
5. **Develop a Full-Stack Interactive Demonstrator**: Deliver an end-to-end FastAPI backend and React.js web dashboard featuring real-time image upload, pipeline stage animations, interactive visual distortion heatmaps, and SQLite experiment tracking.

---

## 4. Literature Survey Summary

| Paper / Author | Methodology | Strengths | Limitations / Gaps |
|---|---|---|---|
| **Kerenidis et al. (2019)**, *Quantum Autoencoders for Data Compression* | Theoretical unitary quantum autoencoder with trash and reference state measurement. | Strong mathematical proof of quantum information compression. | Requires coherent quantum RAM (QRAM) and fault-tolerant hardware; inapplicable to standard PACS images today. |
| **Sureshbabu et al. (2021)**, *Parameterized Quantum Circuits for Machine Learning* | Variational PQC with single-qubit rotations and entangling CNOT gates. | Demonstrated gradient-based parameter learning on NISQ simulators. | Evaluated primarily on synthetic toy datasets (Iris, MNIST) rather than volumetric medical imaging. |
| **Balle et al. (2018)**, *Variational Image Compression with a Scale Hyperprior* | Classical deep convolutional autoencoder with end-to-end rate-distortion optimization. | Superior rate-distortion performance over JPEG 2000. | Computationally heavy classical network; does not investigate quantum representational properties. |
| **Proposed Work (QuantumMedCompress)** | Hybrid CNN-PQC framework with residual skip, true `.qmc` serialization, and multi-metric benchmarking. | Computationally realistic on normal PCs, zero QRAM reliance, real disk measurement, full web UI. | Current quantum simulation is restricted to 4 qubits to maintain sub-second CPU backpropagation. |

---

## 5. Existing System vs. Proposed System

| Parameter | Existing System (JPEG / Classical CAE) | Proposed System (QuantumMedCompress) |
|---|---|---|
| **Representation Mechanism** | Fixed 8×8 block DCT or pure classical dense bottleneck. | Deep spatial CNN encoder + 4-Qubit Variational Hilbert-space entanglement. |
| **Compression Definition** | Fixed quantization matrices or unmeasured continuous float vectors. | Full binary `.qmc` serializer with INT8 quantization and zlib entropy coding. |
| **Feature Correlation** | Linear localized transform or classical weight matrices. | Multi-qubit non-local superposition and quantum expectation values $\langle Z_i \rangle$. |
| **Quality vs. Size Tradeoff** | Blocking artifacts at high compression ratios ($> 50\times$). | Smooth structural degradation without grid-boundary tiling artifacts. |
| **Experiment Management** | Static command-line execution or disparate scripts. | Centralized SQLite database, automated chart generation, and full web application. |

---

## 6. System Architecture & Data Flow

```
[Medical Image (64x64 Grayscale)]
              │
              ▼
[Image Preprocessing Module] ──► Normalization to [0, 1], Validation & Ingestion
              │
              ▼
[Classical CNN Encoder] ───────► 4 Conv2D + BatchNorm + LeakyReLU + AdaptivePool
              │
              ▼
[Latent Bottleneck Vector z] ──► 8 Continuous Latent Features in [-1, 1]
              │
              ▼
[PennyLane Quantum Layer] ────► 4 Qubits: AngleEmbedding(RY, RZ) -> Ring CNOT -> ⟨Z_i⟩
              │
              ▼
[Residual Integration] ────────► z_enhanced = z_classical + alpha * Linear(⟨Z⟩)
              │
              ├──────────────────────────────────┐
              ▼                                  ▼
[Binary .qmc File Serializer]         [Classical CNN Decoder]
(INT8 Quantization + Entropy Bitstream) (Transposed Conv2D + Sigmoid)
              │                                  │
              ▼                                  ▼
[Disk Storage: Real Bytes]            [Reconstructed Medical Image (64x64)]
              │                                  │
              └──────────────────┬───────────────┘
                                 ▼
                     [Evaluation Metrics Engine]
                     (MSE, PSNR, SSIM, CR, Storage Reduction %)
```

---

## 7. Mathematical Formulations

### 1. Quantum State Preparation (Angle Embedding)
Given normalized latent angles $\theta = \pi \cdot \tanh(W_{pre} z + b_{pre}) \in [-\pi, \pi]^4$:
$$|\psi_0\rangle = \bigotimes_{i=0}^3 R_y(\theta_i) |0\rangle = \bigotimes_{i=0}^3 \left( \cos\frac{\theta_i}{2}|0\rangle + \sin\frac{\theta_i}{2}|1\rangle \right)$$

### 2. Parameterized Variational Ansatz
For layer $l \in \{1, \dots, L\}$ and qubit $i$:
$$U_l(\omega) = \left( \prod_{i=0}^3 R_z(\omega_{l,i,2}) R_y(\omega_{l,i,1}) R_x(\omega_{l,i,0}) \right) \cdot U_{\text{entangle}}$$
where circular ring entanglement is defined by:
$$U_{\text{entangle}} = \text{CNOT}_{3,0} \cdot \text{CNOT}_{2,3} \cdot \text{CNOT}_{1,2} \cdot \text{CNOT}_{0,1}$$

### 3. Readout & Residual Integration
The expectation value for each qubit observable $\sigma_z$ is:
$$\langle Z_i \rangle = \langle \psi | \sigma_z^{(i)} | \psi \rangle \in [-1.0, 1.0]$$
The enhanced latent vector is obtained via a learnable skip connection:
$$z_{\text{enhanced}} = z_{\text{classical}} + \alpha \cdot (W_{\text{post}} \langle Z \rangle + b_{\text{post}})$$

### 4. Compound Reconstruction Loss
$$\mathcal{L}_{\text{total}} = \frac{1}{M \times N}\sum_{i,j}(x_{i,j} - \hat{x}_{i,j})^2 + \lambda \cdot (1 - \text{SSIM}(x, \hat{x}))$$
where $\lambda = 0.15$ enforces edge and tissue boundary retention.

---

## 8. Algorithms Pseudocode

### Algorithm 1: Quantum-Enhanced Medical Compression
```text
Input: Medical image I of size (H, W), Model weights Theta, Quantization mode Q_mode
Output: Serialized .qmc file, Reconstructed image I_hat, Evaluation metrics dict

1.  gray <- ConvertToGrayscale(I)
2.  resized <- BicubicResize(gray, target=(64, 64))
3.  x <- Normalize(resized) in [0.0, 1.0]
4.  z_classical <- CNN_Encoder(x; Theta_enc)              # Latent vector (Dim=8)
5.  angles <- pi * Tanh(Linear_pre(z_classical))           # Map to [-pi, pi]
6.  |psi> <- AngleEmbedding(angles) on 4 qubits
7.  For layer = 1 to L:
        Apply SingleQubitRotations(RX, RY, RZ; Theta_q)
        Apply RingCNOTEntanglement()
8.  exp_z <- MeasureExpectationValues(PauliZ) on all 4 qubits
9.  z_enhanced <- z_classical + alpha * Linear_post(exp_z) # Residual skip
10. qmc_bytes <- SerializeAndQuantize(z_enhanced, Q_mode="int8")
11. WriteToDisk(qmc_bytes, path="output.qmc")
12. z_recovered <- DeserializeFromDisk("output.qmc")
13. I_hat <- CNN_Decoder(z_recovered; Theta_dec)          # Reconstruct (64x64)
14. metrics <- ComputeMetrics(x, I_hat, Size(I), Size("output.qmc"))
15. Return "output.qmc", I_hat, metrics
```

---

## 9. Comprehensive Viva Questions and Answers

### Q1: Why did you not encode the entire 64×64 image directly into the quantum circuit?
**Answer**: Encoding a 64×64 image directly into a quantum state requires either 4,096 qubits for spatial basis encoding or 12 qubits for dense amplitude encoding ($2^{12} = 4096$). However, amplitude encoding requires arbitrary quantum state preparation circuits of exponential depth $\mathcal{O}(2^n)$, which is completely intractable on NISQ devices and introduces severe decoherence and exponential simulation latency. Our hybrid architecture delegates spatial dimensionality reduction to classical CNNs and uses the quantum circuit for non-linear latent feature enhancement where it is computationally realistic and effective.

### Q2: What is the purpose of the residual skip connection around the quantum circuit?
**Answer**: Parameterized quantum circuits frequently suffer from the *Barren Plateau phenomenon*, where gradients vanish exponentially in the number of qubits and circuit depth ($\text{Var}[\partial_{\theta} \langle O \rangle] \in \mathcal{O}(2^{-n})$). By implementing $z_{\text{hybrid}} = z_{\text{classical}} + \alpha \cdot \text{Linear}(\langle Z \rangle)$ with $\alpha$ initialized to $0.1$, classical gradients flow unimpeded from decoder to encoder at epoch 0, allowing the quantum circuit to learn incremental feature refinements without stalling model convergence.

### Q3: How do you prove that your compression ratio is real and not just theoretical?
**Answer**: We wrote a custom binary serializer (`backend/serialization/compressor.py`). Instead of merely dividing float count by pixel count, our system writes an actual binary `.qmc` file containing a 23-byte header, INT8-quantized latent parameters, and zlib entropy bitstreams. We measure the exact byte count on the Windows NTFS filesystem via `os.path.getsize()`, proving an authentic $> 98\%$ storage reduction against raw bitmaps.

### Q4: Why did you use PennyLane instead of pure Qiskit?
**Answer**: PennyLane provides native, first-class PyTorch automatic differentiation integration through its `default.qubit` device and `diff_method="backprop"`. It converts the quantum circuit into a differentiable computation graph, allowing classical and quantum parameters to be optimized jointly using standard PyTorch optimizers (`AdamW`) in milliseconds per batch without numerical finite-difference approximations.

### Q5: What is the clinical safety stance of this project?
**Answer**: This system is strictly an academic engineering prototype. High-ratio lossy compression introduces subtle alterations in image pixels. In clinical environments, lossy compression on primary diagnostic scans could obscure microcalcifications or small lesions. Therefore, this tool is positioned strictly for PACS archival optimization, medical education, and research simulations, guarded by prominent UI banners and API disclaimer headers.

---

## 10. Demonstration Script for Final-Year Viva / Review Panel

1. **Introduction (1 min)**:
   - "Good morning respected examiners. Today we present *QuantumMedCompress*, a scalable hybrid quantum-classical framework for medical image compression."
   - Explain the core motivation: PACS volumetric data expansion vs. network bandwidth constraints.
2. **Architecture Walkthrough (2 mins)**:
   - Open the **Quantum Design** tab on the web application (`http://localhost:5173`).
   - Point out the 4-qubit circuit topology: RY/RZ angle preparation, 2 variational layers, and circular CNOT ring entanglement.
3. **Live Image Compression Demo (3 mins)**:
   - Navigate to **Compress & Enhance**.
   - Click *Load Brain MRI Phantom* (or upload a local medical scan).
   - Select **Hybrid Quantum (Proposed)** and click *Execute Quantum Compression*.
   - Watch the animated 7-stage pipeline execute in real time.
   - Inspect the **Visual Reconstruction Inspector**: toggle between the reconstructed image and the **Difference Heatmap** to show localized error distribution.
   - Highlight the metrics: Storage Reduction (>98%), Compression Ratio (>60x), PSNR (~15–16 dB), and exact file size on disk (32 bytes).
   - Click *Download Bitstream (.qmc)* to prove the file physically exists on the disk.
4. **Benchmark Showdown (2 mins)**:
   - Navigate to **Model Showdown**.
   - Show the 3-way comparative matrix: Standard JPEG vs. Classical Autoencoder vs. Proposed Quantum-Enhanced Model.
   - Display the real-time Chart.js bar graphs comparing PSNR, SSIM, and Compression Ratio.
5. **Experiment History & Verification (2 mins)**:
   - Navigate to **Experiments**.
   - Show the automated training loss and PSNR convergence graphs generated by Matplotlib and logged into the SQLite database.
   - Show the test suite running in terminal (`pytest tests/ -v`, 21 passed).
6. **Conclusion & Q&A (2 mins)**:
   - Summarize findings and invite questions from the panel.

---

## 11. Presentation (PPT) Slide-by-Slide Outline

- **Slide 1**: Title Slide — Project Title, Student Names, Register Numbers, Supervisor/Guide Name, Department of AI & Data Science.
- **Slide 2**: Problem Statement & Clinical Motivation — PACS bandwidth challenges, limitations of JPEG DCT blocking artifacts.
- **Slide 3**: Project Objectives — Hybrid architecture, 4-qubit circuit, true binary serialization, head-to-head benchmarking.
- **Slide 4**: Literature Survey & Research Gaps — Limitations of existing QML papers (unrealistic QRAM, toy datasets).
- **Slide 5**: Overall System Architecture — High-level block diagram from raw image to reconstructed slice.
- **Slide 6**: Classical CNN Backbone — Encoder layers (Conv2D, LeakyReLU, AdaptivePool) and Decoder layers (ConvTranspose2D, Sigmoid).
- **Slide 7**: Parameterized Quantum Circuit (PQC) Design — 4 qubits, AngleEmbedding, circular CNOT entanglement, Pauli-Z measurement.
- **Slide 8**: Mathematical Formulations — Quantum state evolution, residual skip formula, compound reconstruction loss (MSE + SSIM).
- **Slide 9**: True Binary Serialization (.qmc) — Bitstream layout, quantization to INT8, entropy coding, real disk measurement.
- **Slide 10**: Experimental Setup & Dataset — MedMNIST & Synthetic brain MRI phantom generation, hyperparameters, PyTorch + PennyLane config.
- **Slide 11**: Comparative Results & Visualizations — Loss curves, PSNR/SSIM charts, Difference Heatmaps.
- **Slide 12**: Head-to-Head Comparison Table — JPEG vs. Classical Autoencoder vs. Hybrid Quantum Model.
- **Slide 13**: Software Engineering & Web Architecture — FastAPI backend, SQLite database, React 19 + Tailwind CSS UI.
- **Slide 14**: Limitations & Ethical Considerations — 4-qubit simulator bound, lossy compression medical safety disclaimers.
- **Slide 15**: Conclusion & Future Scope — QPU hardware execution (IBM Quantum / IonQ), 3D volumetric DICOM slices.
- **Slide 16**: References & Acknowledgments — Key academic papers and institutional mentors.
