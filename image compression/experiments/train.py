"""
Unified Training Script for Classical Autoencoder and Hybrid Quantum-Classical Autoencoder.
Trains models, saves PyTorch checkpoints (.pth), tracks metrics, updates SQLite database,
and exports comparison loss curves to results/plots/.
"""

import sys
from pathlib import Path
# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import argparse
import time
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import torch
import torch.optim as optim

from backend.config import (
    IMAGE_SIZE,
    LATENT_DIM,
    NUM_QUBITS,
    NUM_QUANTUM_LAYERS,
    BATCH_SIZE,
    LEARNING_RATE,
    WEIGHT_DECAY,
    EPOCHS,
    SAVED_MODELS_DIR,
    DATASETS_DIR,
    PLOTS_DIR,
    TABLES_DIR,
    DEVICE
)
from backend.utils.helpers import setup_logger, set_seed
from backend.preprocessing.image_processor import (
    generate_synthetic_medical_dataset,
    get_dataloaders,
    deprocess_image
)
from backend.models.quantum_autoencoder import (
    create_model,
    MedicalReconstructionLoss
)
from backend.evaluation.metrics import (
    calculate_psnr,
    calculate_ssim,
    calculate_mse
)
from backend.database import get_connection

logger = setup_logger("Trainer")

def train_single_model(
    model_type: str,
    train_loader,
    val_loader,
    epochs: int = EPOCHS,
    lr: float = LEARNING_RATE,
    device: str = DEVICE
) -> dict:
    """
    Trains either ClassicalAutoencoder or HybridQuantumAutoencoder.
    Returns full training history dictionary and best checkpoint.
    """
    set_seed(42)
    logger.info(f"=== Starting Training: {model_type} on {device} (Epochs={epochs}, LR={lr}) ===")
    
    model = create_model(model_type, latent_dim=LATENT_DIM, num_qubits=NUM_QUBITS, num_layers=NUM_QUANTUM_LAYERS)
    model.to(device)
    
    loss_fn = MedicalReconstructionLoss().to(device)
    optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=WEIGHT_DECAY)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="min", factor=0.5, patience=3)

    history = {
        "epoch": [],
        "train_loss": [],
        "train_mse": [],
        "val_loss": [],
        "val_psnr": [],
        "val_ssim": [],
        "time_sec": []
    }

    best_val_loss = float("inf")
    model_filename = (
        "classical_autoencoder.pth" if "CLASSICAL" in model_type.upper() 
        else "hybrid_quantum_autoencoder.pth"
    )
    checkpoint_path = SAVED_MODELS_DIR / model_filename

    total_start_time = time.time()

    for epoch in range(1, epochs + 1):
        epoch_start = time.time()
        model.train()
        train_loss_accum = 0.0
        train_mse_accum = 0.0
        num_train_batches = 0

        for batch_x in train_loader:
            batch_x = batch_x.to(device)
            optimizer.zero_grad()
            
            recon, z = model(batch_x)
            loss, details = loss_fn(recon, batch_x)
            
            loss.backward()
            optimizer.step()

            train_loss_accum += details["loss"]
            train_mse_accum += details["mse"]
            num_train_batches += 1

        avg_train_loss = train_loss_accum / max(num_train_batches, 1)
        avg_train_mse = train_mse_accum / max(num_train_batches, 1)

        # Validation phase
        model.eval()
        val_loss_accum = 0.0
        val_psnr_list = []
        val_ssim_list = []
        num_val_batches = 0

        with torch.no_grad():
            for batch_x in val_loader:
                batch_x = batch_x.to(device)
                recon, _ = model(batch_x)
                loss, _ = loss_fn(recon, batch_x)
                val_loss_accum += loss.item()
                num_val_batches += 1

                # Calculate PSNR and SSIM on sample images
                orig_np = deprocess_image(batch_x[0])
                recon_np = deprocess_image(recon[0])
                val_psnr_list.append(calculate_psnr(orig_np, recon_np))
                val_ssim_list.append(calculate_ssim(orig_np, recon_np))

        avg_val_loss = val_loss_accum / max(num_val_batches, 1)
        avg_val_psnr = float(np.mean(val_psnr_list))
        avg_val_ssim = float(np.mean(val_ssim_list))
        epoch_duration = time.time() - epoch_start

        scheduler.step(avg_val_loss)

        history["epoch"].append(epoch)
        history["train_loss"].append(round(avg_train_loss, 5))
        history["train_mse"].append(round(avg_train_mse, 6))
        history["val_loss"].append(round(avg_val_loss, 5))
        history["val_psnr"].append(round(avg_val_psnr, 2))
        history["val_ssim"].append(round(avg_val_ssim, 4))
        history["time_sec"].append(round(epoch_duration, 2))

        logger.info(
            f"Epoch [{epoch:02d}/{epochs:02d}] "
            f"Train Loss: {avg_train_loss:.4f} | "
            f"Val Loss: {avg_val_loss:.4f} | "
            f"Val PSNR: {avg_val_psnr:.2f} dB | "
            f"Val SSIM: {avg_val_ssim:.4f} "
            f"({epoch_duration:.1f}s)"
        )

        # Save best model
        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            torch.save({
                "model_state_dict": model.state_dict(),
                "model_type": model_type,
                "latent_dim": LATENT_DIM,
                "num_qubits": NUM_QUBITS if "HYBRID" in model_type.upper() else 0,
                "num_quantum_layers": NUM_QUANTUM_LAYERS if "HYBRID" in model_type.upper() else 0,
                "best_val_loss": best_val_loss,
                "final_val_psnr": avg_val_psnr,
                "final_val_ssim": avg_val_ssim,
                "epoch": epoch
            }, checkpoint_path)
            logger.info(f"==> Checkpoint saved: {checkpoint_path} (Val Loss: {best_val_loss:.4f})")

    total_time = time.time() - total_start_time
    logger.info(f"Training completed for {model_type} in {total_time:.1f}s. Saved to {checkpoint_path}")

    # Record in SQLite experiments table
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO experiments (
                experiment_name, model_type, dataset, image_size, latent_dim,
                num_qubits, num_quantum_layers, epochs, batch_size, learning_rate,
                avg_mse, avg_psnr, avg_ssim
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            f"Run_{model_type}_{int(time.time())}",
            model_type,
            "Brain MRI / Phantom 64x64",
            "64x64",
            LATENT_DIM,
            NUM_QUBITS if "HYBRID" in model_type.upper() else 0,
            NUM_QUANTUM_LAYERS if "HYBRID" in model_type.upper() else 0,
            epochs,
            BATCH_SIZE,
            lr,
            history["train_mse"][-1],
            history["val_psnr"][-1],
            history["val_ssim"][-1]
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.warning(f"Could not log experiment to database: {e}")

    return {
        "model_type": model_type,
        "checkpoint_path": str(checkpoint_path),
        "history": history,
        "total_time_sec": total_time
    }

def plot_training_histories(histories: list, output_file: Path = PLOTS_DIR / "training_loss_comparison.png") -> None:
    """Generates dual-panel plot comparing Train/Val Loss and PSNR/SSIM."""
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    for h_data in histories:
        name = h_data["model_type"]
        hist = h_data["history"]
        axes[0].plot(hist["epoch"], hist["train_loss"], label=f"{name} (Train Loss)", linestyle="--")
        axes[0].plot(hist["epoch"], hist["val_loss"], label=f"{name} (Val Loss)", linewidth=2)

        axes[1].plot(hist["epoch"], hist["val_psnr"], label=f"{name} (Val PSNR dB)", linewidth=2)

    axes[0].set_title("Reconstruction Loss Convergence", fontsize=12, fontweight="bold")
    axes[0].set_xlabel("Epoch")
    axes[0].set_ylabel("Compound Loss (MSE + 0.15 SSIM)")
    axes[0].legend()
    axes[0].grid(True)

    axes[1].set_title("Reconstruction Quality (PSNR)", fontsize=12, fontweight="bold")
    axes[1].set_xlabel("Epoch")
    axes[1].set_ylabel("PSNR (dB)")
    axes[1].legend()
    axes[1].grid(True)

    plt.tight_layout()
    plt.savefig(output_file, dpi=200)
    plt.close()
    logger.info(f"Loss comparison plot saved to {output_file}")

def main():
    parser = argparse.ArgumentParser(description="QuantumMedCompress Training Pipeline")
    parser.add_argument("--model", type=str, default="all", choices=["classical", "hybrid", "all"],
                        help="Model to train: 'classical', 'hybrid', or 'all'")
    parser.add_argument("--epochs", type=int, default=10, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE, help="Mini-batch size")
    parser.add_argument("--lr", type=float, default=LEARNING_RATE, help="Initial learning rate")
    args = parser.parse_args()

    # 1. Ensure dataset exists
    data_dir = DATASETS_DIR / "synthetic_mri"
    if not data_dir.exists() or len(list(data_dir.glob("*.png"))) < 50:
        logger.info(f"Dataset not detected in {data_dir}. Generating synthetic medical phantom dataset...")
        generate_synthetic_medical_dataset(data_dir, num_samples=160)

    train_loader, val_loader, _ = get_dataloaders(data_dir, batch_size=args.batch_size)

    histories = []
    if args.model in ["classical", "all"]:
        res_classical = train_single_model("CLASSICAL_AUTOENCODER", train_loader, val_loader, epochs=args.epochs, lr=args.lr)
        histories.append(res_classical)

    if args.model in ["hybrid", "all"]:
        res_hybrid = train_single_model("HYBRID_QUANTUM", train_loader, val_loader, epochs=args.epochs, lr=args.lr)
        histories.append(res_hybrid)

    if histories:
        plot_training_histories(histories)

if __name__ == "__main__":
    main()
