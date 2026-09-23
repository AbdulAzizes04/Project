import sys
import os

# Resolve the ml/ directory relative to this file's location in backend/app/utils/
# backend/app/utils/ -> backend/app/ -> backend/ -> project_root/ -> ml/
_BACKEND_APP_UTILS = os.path.dirname(os.path.abspath(__file__))   # backend/app/utils
_BACKEND_APP     = os.path.dirname(_BACKEND_APP_UTILS)            # backend/app
_BACKEND         = os.path.dirname(_BACKEND_APP)                  # backend
_PROJECT_ROOT    = os.path.dirname(_BACKEND)                      # project root
_ML_DIR          = os.path.join(_PROJECT_ROOT, "ml")              # ml/

for _p in [_ML_DIR, _BACKEND, _PROJECT_ROOT]:
    if _p not in sys.path:
        sys.path.insert(0, _p)
