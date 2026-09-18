"""
Device Risk Features for GuidedGuard.

This module evaluates client device trustworthiness:
- device_id
- is_new_device
- device_change_frequency
- device_risk_score
- device_type (Mobile App, Web Browser, Unknown Proxy, Rooted Device)

DATA PROVENANCE POLICY:
Public financial datasets (such as PaySim) lack low-level client hardware / device telemetry.
When device attributes are provided via UI or simulator, they are explicitly tagged:
`device_data_source: SIMULATED FOR PROTOTYPE`
to ensure complete scientific integrity without misrepresenting synthetic inputs as real banking logs.
"""

from typing import Dict, Any, Optional


def compute_device_features(
    device_type: str = "Mobile App",
    device_id: Optional[str] = None,
    is_new_override: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Evaluate device risk score and novel device indicators.
    """
    dev_lower = str(device_type).lower()
    dev_id = device_id or f"DEV-{abs(hash(device_type)) % 100000}"

    is_proxy = any(k in dev_lower for k in ["proxy", "vpn", "tor", "unknown", "emulator", "rooted"])
    
    if is_new_override is not None:
        is_new = int(is_new_override)
    else:
        is_new = 1 if (is_proxy or "web" in dev_lower) else 0

    if is_proxy:
        risk_score = 95.0
    elif is_new:
        risk_score = 65.0
    elif "web" in dev_lower:
        risk_score = 35.0
    else:
        risk_score = 10.0

    return {
        "device_id": dev_id,
        "device_type": device_type,
        "is_new_device": is_new,
        "device_is_proxy": 1 if is_proxy else 0,
        "device_change_frequency": 0.2 if not is_new else 1.5,
        "device_risk_score": float(risk_score),
        "device_data_source": "SIMULATED FOR PROTOTYPE",
    }
