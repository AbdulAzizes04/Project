"""
Copies AI generated 1st floor construction images and fetches real high-res 1st floor worker construction photographs into uploads/images/
"""

import os
import ssl
import shutil
import urllib.request
import glob
from pathlib import Path
from config import UPLOADS_IMAGES

ADDITIONAL_1ST_FLOOR_URLS = {
    "workers_building_1st_floor_wall.jpg": "https://images.unsplash.com/photo-1541888946425-d0fbb186a5b7?q=80&w=1200&auto=format&fit=crop",
    "workers_1st_floor_framing.jpg": "https://images.unsplash.com/photo-1504307651254-35680f356dfd?q=80&w=1200&auto=format&fit=crop",
    "workers_1st_floor_masonry.jpg": "https://images.unsplash.com/photo-1590069261209-f8e9b8642343?q=80&w=1200&auto=format&fit=crop"
}

def main():
    # 1. Copy generated image from brain directory
    brain_dir = Path(os.path.expanduser("~")) / ".gemini" / "antigravity-ide" / "brain"
    gen_imgs = list(brain_dir.glob("**/*workers_1st_floor_bricks*.png"))
    
    if gen_imgs:
        target_gen = UPLOADS_IMAGES / "workers_constructing_1st_floor_building.jpg"
        shutil.copy(gen_imgs[0], target_gen)
        print(f"  [OK] Saved AI generated image to: {target_gen.name}")
        
    # 2. Download additional 1st floor worker construction stock images
    headers = {"User-Agent": "Mozilla/5.0"}
    ctx = ssl._create_unverified_context()
    
    print("Downloading 1st floor construction site worker photographs...")
    for filename, url in ADDITIONAL_1ST_FLOOR_URLS.items():
        try:
            target_path = UPLOADS_IMAGES / filename
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, context=ctx, timeout=15) as response, open(target_path, "wb") as out_file:
                out_file.write(response.read())
            print(f"  [OK] Saved: {filename}")
        except Exception as e:
            print(f"  [FAIL] Could not fetch {filename}: {e}")

if __name__ == "__main__":
    main()
