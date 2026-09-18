"""
Binary Serialization and Deserialization Engine for QuantumMedCompress (.qmc format).
Implements learned latent quantization, entropy encoding, and true disk-level bitstream measurement.
"""

import struct
import zlib
from pathlib import Path
from typing import Tuple, Dict, Any, Union
import numpy as np
import torch

# Magic identifier for QuantumMedCompress binary bitstreams
MAGIC_HEADER = b"QMC\x01"

MODEL_TYPE_MAP = {
    "CLASSICAL_AUTOENCODER": 1,
    "HYBRID_QUANTUM": 2,
    "UNKNOWN": 0
}
REVERSE_MODEL_TYPE_MAP = {v: k for k, v in MODEL_TYPE_MAP.items()}

class CorruptedQMCFileError(ValueError):
    """Raised when reading an invalid or corrupted .qmc binary file."""
    pass

def serialize_latent_to_qmc(
    latent: Union[torch.Tensor, np.ndarray],
    output_path: Union[Path, str],
    model_type: str = "HYBRID_QUANTUM",
    target_shape: Tuple[int, int] = (64, 64),
    quantize_mode: str = "int8"
) -> Tuple[Path, Dict[str, Any]]:
    """
    Serializes a continuous latent representation into a real on-disk .qmc binary file.
    
    Binary Layout:
    [4 bytes]  Magic: 'QMC\x01'
    [1 byte]   Model Type (1=Classical, 2=Quantum)
    [2 bytes]  Target Height (uint16)
    [2 bytes]  Target Width (uint16)
    [1 byte]   Latent Dim N (uint8)
    [1 byte]   Quantize Mode (1=int8, 2=float16)
    [4 bytes]  Min latent value (float32)
    [4 bytes]  Max latent value (float32)
    [4 bytes]  Compressed payload byte length (uint32)
    [N bytes]  Zlib compressed quantized bitstream
    """
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    if isinstance(latent, torch.Tensor):
        z = latent.detach().cpu().flatten().numpy().astype(np.float32)
    else:
        z = np.asarray(latent, dtype=np.float32).flatten()

    latent_dim = len(z)
    min_val = float(z.min())
    max_val = float(z.max())

    # Quantization
    if quantize_mode == "int8":
        quant_mode_byte = 1
        # Map [min_val, max_val] linearly to int8 [-128, 127]
        if abs(max_val - min_val) < 1e-7:
            quantized = np.zeros(latent_dim, dtype=np.int8)
        else:
            normalized = (z - min_val) / (max_val - min_val)  # [0, 1]
            quantized = (normalized * 255.0 - 128.0).round().astype(np.int8)
        raw_bytes = quantized.tobytes()
    else:
        quant_mode_byte = 2
        raw_bytes = z.astype(np.float16).tobytes()

    # Entropy encoding via zlib level 9
    compressed_payload = zlib.compress(raw_bytes, level=9)
    payload_len = len(compressed_payload)

    type_code = MODEL_TYPE_MAP.get(model_type.upper(), 0)

    # Pack binary header (23 bytes fixed)
    header = struct.pack(
        ">4sBHHBBffI",
        MAGIC_HEADER,
        type_code,
        target_shape[0],
        target_shape[1],
        latent_dim,
        quant_mode_byte,
        min_val,
        max_val,
        payload_len
    )

    with open(out_file, "wb") as f:
        f.write(header)
        f.write(compressed_payload)

    total_bytes = out_file.stat().st_size

    stats = {
        "output_path": str(out_file),
        "total_compressed_bytes": total_bytes,
        "header_bytes": len(header),
        "payload_bytes": payload_len,
        "latent_dim": latent_dim,
        "quantize_mode": quantize_mode,
        "model_type": model_type
    }

    return out_file, stats

def deserialize_qmc_to_latent(file_path: Union[Path, str]) -> Tuple[torch.Tensor, Dict[str, Any]]:
    """
    Reads an on-disk .qmc file, extracts header metadata, decompresses entropy stream,
    and dequantizes back to a PyTorch float32 latent tensor (1, latent_dim).
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f".qmc file not found: {path}")

    with open(path, "rb") as f:
        data = f.read()

    header_size = struct.calcsize(">4sBHHBBffI")
    if len(data) < header_size:
        raise CorruptedQMCFileError("File too small to contain valid QMC header.")

    header = data[:header_size]
    magic, type_code, h, w, latent_dim, quant_mode_byte, min_val, max_val, payload_len = struct.unpack(
        ">4sBHHBBffI", header
    )

    if magic != MAGIC_HEADER:
        raise CorruptedQMCFileError(f"Invalid magic header {magic!r}. Expected {MAGIC_HEADER!r}.")

    payload_data = data[header_size:header_size + payload_len]
    if len(payload_data) != payload_len:
        raise CorruptedQMCFileError("Payload length does not match header declaration.")

    raw_bytes = zlib.decompress(payload_data)

    if quant_mode_byte == 1:
        # int8 dequantization
        quantized = np.frombuffer(raw_bytes, dtype=np.int8)
        if len(quantized) != latent_dim:
            raise CorruptedQMCFileError(f"Expected {latent_dim} int8 elements, got {len(quantized)}.")
        normalized = (quantized.astype(np.float32) + 128.0) / 255.0
        z = normalized * (max_val - min_val) + min_val
    else:
        # float16
        z = np.frombuffer(raw_bytes, dtype=np.float16).astype(np.float32)

    latent_tensor = torch.from_numpy(z).unsqueeze(0).float()

    metadata = {
        "model_type": REVERSE_MODEL_TYPE_MAP.get(type_code, "UNKNOWN"),
        "target_shape": (h, w),
        "latent_dim": latent_dim,
        "file_size_bytes": len(data),
        "min_val": min_val,
        "max_val": max_val
    }

    return latent_tensor, metadata
