"""
Comprehensive Benchmark Comparison Engine.
Fairly evaluates and compares:
1. JPEG standard compression (at matched quality)
2. Classical Convolutional Autoencoder (Baseline)
3. Proposed Hybrid Quantum-Classical Autoencoder (QuantumMedCompress)

Measures:
- Original Size, Compressed Size, Compression Ratio, Storage Reduction (%)
- MSE, PSNR (dB), SSIM
- Encoding and Reconstruction Latencies (ms)
"""

import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import time
import io
import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import torch

from backend.config import (
    SAVED_MODELS_DIR,
    DATASETS_DIR,
    TABLES_DIR,
    PLOTS_DIR,
    DEVICE,
    IMAGE_SIZE
)
from backend.preprocessing.image_processor import (
    preprocess_image,
    deprocess_image,
    get_dataloaders
)
from backend.models.quantum_autoencoder import create_model
from backend.serialization.compressor import serialize_latent_to_qmc, deserialize_qmc_to_latent
from backend.evaluation.metrics import evaluate_reconstruction_all
from backend.utils.helpers import setup_logger

logger = setup_logger("Benchmark")

def compress_with_jpeg(image_np: np.ndarray, quality: int = 25) -> dict:
    """Compresses a grayscale image using standard JPEG DCT compression."""
    start_time = time.time()
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
    success, enc_bytes = cv2.imencode(".jpg", image_np, encode_param)
    compressed_bytes_len = len(enc_bytes.tobytes())
    
    # Decompress back
    decompressed = cv2.imdecode(enc_bytes, cv2.IMREAD_GRAYSCALE)
    latency_ms = (time.time() - start_time) * 1000.0

    orig_bytes = image_np.nbytes
    metrics = evaluate_reconstruction_all(
        original=image_np,
        reconstructed=decompressed,
        original_size_bytes=orig_bytes,
        compressed_size_bytes=compressed_bytes_len,
        inference_time_ms=latency_ms
    )
    metrics["model_name"] = f"JPEG (Q={quality})"
    return metrics

def compress_with_neural_model(
    model,
    model_type: str,
    image_tensor: torch.Tensor,
    original_np: np.ndarray,
    temp_dir: Path
) -> dict:
    """Runs compression, on-disk .qmc serialization, and reconstruction through PyTorch/Quantum model."""
    start_time = time.time()
    model.eval()

    with torch.no_grad():
        # 1. Encode
        latent = model.encode(image_tensor.to(DEVICE))

        # 2. Real on-disk .qmc serialization
        qmc_file = temp_dir / f"test_{int(time.time() * 1000)}.qmc"
        _, stats = serialize_latent_to_qmc(
            latent=latent,
            output_path=qmc_file,
            model_type=model_type,
            target_shape=IMAGE_SIZE,
            quantize_mode="int8"
        )
        compressed_size = stats["total_compressed_bytes"]

        # 3. Deserialize from disk
        recovered_latent, _ = deserialize_qmc_to_latent(qmc_file)

        # 4. Decode
        recon_tensor = model.decode(recovered_latent.to(DEVICE))
        recon_np = deprocess_image(recon_tensor)

        if qmc_file.exists():
            qmc_file.unlink()

    latency_ms = (time.time() - start_time) * 1000.0
    orig_bytes = original_np.nbytes

    metrics = evaluate_reconstruction_all(
        original=original_np,
        reconstructed=recon_np,
        original_size_bytes=orig_bytes,
        compressed_size_bytes=compressed_size,
        inference_time_ms=latency_ms
    )
    metrics["model_name"] = "Classical Autoencoder" if "CLASSICAL" in model_type else "Hybrid Quantum Model"
    return metrics

def run_benchmark(num_test_samples: int = 15) -> pd.DataFrame:
    """Executes benchmark over the test dataset across all three methods."""
    data_dir = DATASETS_DIR / "synthetic_mri"
    _, _, test_loader = get_dataloaders(data_dir, batch_size=1)

    # Load models
    classical_model = create_model("CLASSICAL_AUTOENCODER")
    hybrid_model = create_model("HYBRID_QUANTUM")

    cl_ckpt = SAVED_MODELS_DIR / "classical_autoencoder.pth"
    hy_ckpt = SAVED_MODELS_DIR / "hybrid_quantum_autoencoder.pth"

    if cl_ckpt.exists():
        classical_model.load_state_dict(torch.load(cl_ckpt, map_location=DEVICE)["model_state_dict"])
    classical_model.to(DEVICE)

    if hy_ckpt.exists():
        hybrid_model.load_state_dict(torch.load(hy_ckpt, map_location=DEVICE)["model_state_dict"])
    hybrid_model.to(DEVICE)

    all_results = []
    temp_dir = BASE_DIR / "results" / "temp"
    temp_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Running benchmark comparison over {num_test_samples} test images...")

    count = 0
    for batch_x in test_loader:
        if count >= num_test_samples:
            break
        orig_np = deprocess_image(batch_x[0])

        # 1. JPEG
        res_jpeg = compress_with_jpeg(orig_np, quality=30)
        all_results.append(res_jpeg)

        # 2. Classical Autoencoder
        res_classical = compress_with_neural_model(classical_model, "CLASSICAL_AUTOENCODER", batch_x, orig_np, temp_dir)
        all_results.append(res_classical)

        # 3. Hybrid Quantum-Classical
        res_hybrid = compress_with_neural_model(hybrid_model, "HYBRID_QUANTUM", batch_x, orig_np, temp_dir)
        all_results.append(res_hybrid)

        count += 1

    df = pd.DataFrame(all_results)
    # Aggregate by model
    summary = df.groupby("model_name").agg({
        "original_size_bytes": "mean",
        "compressed_size_bytes": "mean",
        "compression_ratio": "mean",
        "storage_reduction_percent": "mean",
        "mse": "mean",
        "psnr": "mean",
        "ssim": "mean",
        "inference_time_ms": "mean"
    }).reset_index()

    # Save summary table to CSV
    csv_path = TABLES_DIR / "benchmark_comparison.csv"
    summary.to_csv(csv_path, index=False)
    logger.info(f"Benchmark summary saved to {csv_path}")

    # Plot metrics
    plot_comparison_bars(summary)
    return summary

def plot_comparison_bars(summary_df: pd.DataFrame, output_path: Path = PLOTS_DIR / "model_comparison_metrics.png"):
    """Generates a 4-panel comparison bar chart."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    models = summary_df["model_name"].tolist()
    colors = ["#4A5568", "#3182CE", "#805AD5"]

    # 1. PSNR
    axes[0, 0].bar(models, summary_df["psnr"], color=colors)
    axes[0, 0].set_title("Reconstruction Quality: PSNR (dB)", fontweight="bold")
    axes[0, 0].set_ylabel("PSNR (Higher is better)")
    for i, v in enumerate(summary_df["psnr"]):
        axes[0, 0].text(i, v + 0.5, f"{v:.1f}", ha="center", fontweight="bold")

    # 2. SSIM
    axes[0, 1].bar(models, summary_df["ssim"], color=colors)
    axes[0, 1].set_title("Structural Similarity: SSIM", fontweight="bold")
    axes[0, 1].set_ylabel("SSIM (Higher is better)")
    axes[0, 1].set_ylim(0, 1.05)
    for i, v in enumerate(summary_df["ssim"]):
        axes[0, 1].text(i, v + 0.02, f"{v:.3f}", ha="center", fontweight="bold")

    # 3. Compression Ratio
    axes[1, 0].bar(models, summary_df["compression_ratio"], color=colors)
    axes[1, 0].set_title("Compression Ratio (Original / Compressed)", fontweight="bold")
    axes[1, 0].set_ylabel("Ratio (Higher is better)")
    for i, v in enumerate(summary_df["compression_ratio"]):
        axes[1, 0].text(i, v + 1, f"{v:.1f}x", ha="center", fontweight="bold")

    # 4. Storage Reduction %
    axes[1, 1].bar(models, summary_df["storage_reduction_percent"], color=colors)
    axes[1, 1].set_title("Storage Reduction (%)", fontweight="bold")
    axes[1, 1].set_ylabel("Reduction % (Higher is better)")
    axes[1, 1].set_ylim(0, 110)
    for i, v in enumerate(summary_df["storage_reduction_percent"]):
        axes[1, 1].text(i, v + 1.5, f"{v:.1f}%", ha="center", fontweight="bold")

    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()
    logger.info(f"Comparison chart saved to {output_path}")

if __name__ == "__main__":
    summary = run_benchmark()
    print(summary)
