"""
End-to-End Unit tests for FastAPI REST API endpoints using TestClient.
"""

import io
import cv2
import numpy as np
import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ONLINE"
    assert "disclaimer" in data

def test_model_info():
    response = client.get("/api/model-info")
    assert response.status_code == 200
    data = response.json()
    assert data["number_of_qubits"] == 4
    assert data["latent_dimension"] == 8

def test_dashboard_and_experiments():
    res_dash = client.get("/api/dashboard")
    assert res_dash.status_code == 200
    dash_data = res_dash.json()
    assert "total_images" in dash_data

    res_exp = client.get("/api/experiments")
    assert res_exp.status_code == 200
    exp_data = res_exp.json()
    assert "experiments" in exp_data

def test_upload_and_compression_workflow():
    # 1. Create dummy grayscale image in memory
    dummy_img = np.random.randint(50, 200, (64, 64), dtype=np.uint8)
    success, encoded = cv2.imencode(".png", dummy_img)
    assert success
    
    file_bytes = io.BytesIO(encoded.tobytes())
    
    # Upload
    upload_res = client.post(
        "/api/upload",
        files={"file": ("test_slice.png", file_bytes, "image/png")}
    )
    assert upload_res.status_code == 200
    up_data = upload_res.json()
    assert "image_id" in up_data
    image_id = up_data["image_id"]

    # 2. Compress with Classical Autoencoder
    comp_classical = client.post(
        "/api/compress",
        json={"image_id": image_id, "model_type": "CLASSICAL_AUTOENCODER"}
    )
    assert comp_classical.status_code == 200
    c_data = comp_classical.json()
    assert c_data["psnr"] > 0
    assert c_data["compression_ratio"] > 1.0

    # 3. Compress with Hybrid Quantum Model
    comp_hybrid = client.post(
        "/api/compress",
        json={"image_id": image_id, "model_type": "HYBRID_QUANTUM"}
    )
    assert comp_hybrid.status_code == 200
    h_data = comp_hybrid.json()
    assert h_data["psnr"] > 0
    assert h_data["storage_reduction_percent"] > 50.0

    # 4. Check results endpoint
    results_res = client.get("/api/results")
    assert results_res.status_code == 200
    assert results_res.json()["count"] >= 2
