"""
CLI Batch & Single Pair Inference Tool for EARTH VISION-X.
Usage: python infer.py --t1 path/to/t1.png --t2 path/to/t2.png --model "ViT-Base Siamese"
"""

import sys
import argparse
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from earth_vision_x.app.config.logging_config import logger
from earth_vision_x.app.config.constants import SupportedModels
from earth_vision_x.app.database.db import init_db
from earth_vision_x.app.datasets.sample_downloader import SampleDatasetGenerator
from earth_vision_x.app.services.inference_service import InferenceService

def main():
    parser = argparse.ArgumentParser(description="EARTH VISION-X Inference CLI")
    parser.add_argument("--t1", type=str, default=None, help="Path to Time-1 image")
    parser.add_argument("--t2", type=str, default=None, help="Path to Time-2 image")
    parser.add_argument("--model", type=str, default=SupportedModels.VIT_BASE.value, help="Model architecture")
    parser.add_argument("--tta", action="store_true", help="Enable Test-Time Augmentation")

    args = parser.parse_args()

    init_db()

    if args.t1 is None or args.t2 is None:
        logger.info("No input image pair specified. Generating synthetic benchmark sample...")
        samples = SampleDatasetGenerator.generate_synthetic_benchmark(num_samples=1)
        t1, t2 = samples["t1_paths"][0], samples["t2_paths"][0]
    else:
        t1, t2 = args.t1, args.t2

    logger.info(f"Running inference on pair: {t1} vs {t2}")

    service = InferenceService(model_name=args.model)
    res = service.run_full_pipeline(t1, t2, use_tta=args.tta, generate_pdf=True)

    print("\n====================================================")
    print("EARTH VISION-X INFERENCE RESULTS")
    print("====================================================")
    print(f"Primary Change Detected: {res['primary_change']}")
    print(f"Confidence Score:        {res['confidence_score']*100:.2f}%")
    print(f"Affected Area:           {res['affected_area_sqkm']:.2f} sq km ({res['affected_percentage']:.2f}%)")
    print(f"Inference Time:          {res['inference_time_sec']:.3f} seconds")
    print(f"PDF Report Saved:        {res.get('report_pdf_path', 'N/A')}")
    print("====================================================\n")

if __name__ == "__main__":
    main()
