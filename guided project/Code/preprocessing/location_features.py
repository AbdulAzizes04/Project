"""
Location Risk Features for GuidedGuard.

This module evaluates geographic and connection region risk:
- location_id
- is_new_location
- distance_from_previous_location
- location_change_frequency
- location_risk_score

DATA PRIVACY & PROVENANCE POLICY:
GuidedGuard NEVER captures real user GPS or physical coordinates.
All location signals represent coarse-grained region descriptors (e.g. Domestic Home, Foreign Proxy, Cross-Border)
and are strictly labelled:
`location_data_source: SYNTHETIC/DEMO REGION IDENTIFIERS`
"""

from typing import Dict, Any, Optional


def compute_location_features(
    location_region: str = "Domestic Home",
    location_id: Optional[str] = None,
    is_new_override: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Compute geographic anomaly and regional risk indicators.
    """
    loc_lower = str(location_region).lower()
    loc_id = location_id or f"LOC-{abs(hash(location_region)) % 10000}"

    is_suspicious = any(k in loc_lower for k in ["foreign", "proxy", "high risk", "cross border", "tor", "vpn"])

    if is_new_override is not None:
        is_new = int(is_new_override)
    else:
        is_new = 1 if is_suspicious else 0

    if is_suspicious:
        dist_km = 4500.0
        risk_score = 95.0
    elif is_new:
        dist_km = 350.0
        risk_score = 60.0
    else:
        dist_km = 12.0
        risk_score = 10.0

    return {
        "location_id": loc_id,
        "location_region": location_region,
        "is_new_location": is_new,
        "distance_from_previous_location_km": dist_km,
        "location_change_frequency": 0.1 if not is_new else 1.2,
        "location_risk_score": float(risk_score),
        "location_data_source": "SYNTHETIC/DEMO REGION IDENTIFIERS",
    }
