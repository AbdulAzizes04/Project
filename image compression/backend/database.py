"""
SQLite database management module for tracking processed images, compression runs, and experiment benchmarks.
"""

import sqlite3
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from backend.config import DB_PATH
from backend.utils.helpers import setup_logger

logger = setup_logger("Database")

def get_connection() -> sqlite3.Connection:
    """Returns a SQLite connection with dict-like row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db() -> None:
    """Initializes the SQLite database tables if they do not exist."""
    conn = get_connection()
    cursor = conn.cursor()

    # Images table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            original_path TEXT NOT NULL,
            original_size_bytes INTEGER NOT NULL,
            width INTEGER NOT NULL,
            height INTEGER NOT NULL,
            channels INTEGER NOT NULL,
            modality TEXT DEFAULT 'Grayscale Medical',
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Compression Runs / Results table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS compression_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_id INTEGER,
            model_type TEXT NOT NULL,          -- 'JPEG', 'CLASSICAL_AUTOENCODER', 'HYBRID_QUANTUM'
            compressed_file_path TEXT,
            reconstructed_image_path TEXT,
            original_size_bytes INTEGER NOT NULL,
            compressed_size_bytes INTEGER NOT NULL,
            compression_ratio REAL NOT NULL,
            storage_reduction_percent REAL NOT NULL,
            mse REAL NOT NULL,
            psnr REAL NOT NULL,
            ssim REAL NOT NULL,
            inference_time_ms REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (image_id) REFERENCES images(id)
        )
    """)

    # Experiments table (for batch training and comparative study logs)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS experiments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            experiment_name TEXT NOT NULL,
            model_type TEXT NOT NULL,
            dataset TEXT NOT NULL,
            image_size TEXT NOT NULL,
            latent_dim INTEGER NOT NULL,
            num_qubits INTEGER DEFAULT 0,
            num_quantum_layers INTEGER DEFAULT 0,
            epochs INTEGER NOT NULL,
            batch_size INTEGER NOT NULL,
            learning_rate REAL NOT NULL,
            avg_mse REAL,
            avg_psnr REAL,
            avg_ssim REAL,
            avg_compression_ratio REAL,
            avg_storage_reduction REAL,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    logger.info(f"Database initialized successfully at {DB_PATH}")

def save_image_record(filename: str, original_path: str, size_bytes: int, width: int, height: int, channels: int = 1) -> int:
    """Inserts an uploaded image record and returns its ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO images (filename, original_path, original_size_bytes, width, height, channels)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (filename, original_path, size_bytes, width, height, channels))
    image_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return image_id

def save_compression_run(run_data: Dict[str, Any]) -> int:
    """Inserts a compression evaluation run into database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO compression_runs (
            image_id, model_type, compressed_file_path, reconstructed_image_path,
            original_size_bytes, compressed_size_bytes, compression_ratio,
            storage_reduction_percent, mse, psnr, ssim, inference_time_ms
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        run_data.get("image_id"),
        run_data["model_type"],
        run_data.get("compressed_file_path"),
        run_data.get("reconstructed_image_path"),
        run_data["original_size_bytes"],
        run_data["compressed_size_bytes"],
        run_data["compression_ratio"],
        run_data["storage_reduction_percent"],
        run_data["mse"],
        run_data["psnr"],
        run_data["ssim"],
        run_data["inference_time_ms"]
    ))
    run_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return run_id

def get_recent_compression_runs(limit: int = 20) -> List[Dict[str, Any]]:
    """Retrieves recent compression runs."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT cr.*, img.filename 
        FROM compression_runs cr
        LEFT JOIN images img ON cr.image_id = img.id
        ORDER BY cr.created_at DESC
        LIMIT ?
    """, (limit,))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def get_dashboard_summary() -> Dict[str, Any]:
    """Computes aggregate metrics for dashboard."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as total_images FROM images")
    total_images = cursor.fetchone()["total_images"]

    cursor.execute("""
        SELECT 
            COUNT(*) as total_runs,
            AVG(compression_ratio) as avg_cr,
            AVG(psnr) as avg_psnr,
            AVG(ssim) as avg_ssim,
            AVG(storage_reduction_percent) as avg_storage_reduction
        FROM compression_runs
    """)
    stats = dict(cursor.fetchone())
    conn.close()

    return {
        "total_images": total_images,
        "total_runs": stats.get("total_runs") or 0,
        "avg_compression_ratio": round(stats.get("avg_cr") or 0.0, 2),
        "avg_psnr": round(stats.get("avg_psnr") or 0.0, 2),
        "avg_ssim": round(stats.get("avg_ssim") or 0.0, 4),
        "avg_storage_reduction": round(stats.get("avg_storage_reduction") or 0.0, 2)
    }

if __name__ == "__main__":
    init_db()
