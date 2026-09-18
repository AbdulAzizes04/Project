"""
User Behavioural Baseline & Deviation Profiling for GuidedGuard.

This module builds comprehensive historical profiles for customers and evaluates
how strongly an active payment deviates from that individual's normal habits.
In scam-guided (APP) fraud, authentication credentials are valid, but the
transaction pattern deviates significantly from the user's historical baseline.
"""

from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd


class UserBehavioralProfiler:
    """
    Constructs and persists per-customer historical behavioural baselines and
    computes multi-dimensional deviation signals at inference time.
    """

    def __init__(self, default_profile: Optional[Dict[str, Any]] = None):
        self.profiles: Dict[str, Dict[str, Any]] = {}
        # Global fallback baseline across population
        self.global_baseline = default_profile or {
            "avg_amount": 2500.0,
            "median_amount": 1200.0,
            "std_amount": 2800.0,
            "max_amount": 15000.0,
            "daily_txns": 2.0,
            "usual_hours": list(range(8, 22)),  # 08:00 to 21:00
            "usual_days": [0, 1, 2, 3, 4],     # Weekdays
            "common_beneficiaries": [],
            "avg_gap_hours": 18.0,
            "typical_types": ["PAYMENT", "TRANSFER"],
            "typical_device": "Mobile App",
            "typical_location": "Domestic Home",
        }

    def build_profiles_from_dataframe(
        self,
        df: pd.DataFrame,
        user_col: str = "nameOrig",
        amount_col: str = "amount",
        step_col: str = "step",
        dest_col: str = "nameDest",
        type_col: str = "type",
    ) -> Dict[str, Dict[str, Any]]:
        """
        Build behavioural baseline profiles from historical transaction records.
        """
        if user_col not in df.columns:
            return self.profiles

        grouped = df.groupby(user_col)
        for user_id, group in grouped:
            amounts = group[amount_col].values
            avg_amt = float(np.mean(amounts))
            med_amt = float(np.median(amounts))
            std_amt = float(np.std(amounts)) if len(amounts) > 1 else max(avg_amt * 0.5, 100.0)
            max_amt = float(np.max(amounts))

            hours = (group[step_col] % 24).tolist() if step_col in group.columns else [12]
            days = ((group[step_col] // 24) % 7).tolist() if step_col in group.columns else [0]
            beneficiaries = group[dest_col].tolist() if dest_col in group.columns else []
            types = group[type_col].tolist() if type_col in group.columns else ["TRANSFER"]
            devices = group["device_id"].tolist() if "device_id" in group.columns else ["DEV_A"]
            locations = group["location_region"].tolist() if "location_region" in group.columns else ["REG_NORTH"]

            self.profiles[str(user_id)] = {
                "avg_amount": round(avg_amt, 2),
                "mean_amount": round(avg_amt, 2),
                "median_amount": round(med_amt, 2),
                "std_amount": round(std_amt, 2),
                "max_amount": round(max_amt, 2),
                "total_txns": len(group),
                "tx_count": len(group),
                "daily_txns": round(len(group) / max(1, (group[step_col].max() - group[step_col].min()) / 24.0), 2) if step_col in group.columns else 2.0,
                "usual_hours": list(set(hours)),
                "usual_days": list(set(days)),
                "common_beneficiaries": list(set(beneficiaries)),
                "known_recipients": list(set(beneficiaries)),
                "known_devices": list(set(devices)),
                "known_locations": list(set(locations)),
                "typical_types": list(set(types)),
                "typical_device": devices[0] if devices else "Mobile App",
                "typical_location": locations[0] if locations else "Domestic Home",
                "avg_gap_hours": 12.0,
            }

        return self.profiles

    def fit(self, df: pd.DataFrame) -> 'UserBehavioralProfiler':
        """Fit profiler on historical transactions DataFrame."""
        self.build_profiles_from_dataframe(df)
        return self

    @property
    def customer_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Dictionary of fitted user profiles."""
        return self.profiles

    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Retrieve profile for user, or global baseline if user is new/unseen."""
        return self.profiles.get(str(user_id), self.global_baseline)

    def compute_deviations(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """Compute deviations for a single transaction dictionary."""
        user_id = str(transaction.get("nameOrig", transaction.get("customer_id", "default")))
        is_cold = 1 if user_id not in self.profiles else 0
        devs = self.calculate_deviations(user_id=user_id, current_txn=transaction)
        
        # Add test-friendly semantic keys
        devs["amount_to_avg_ratio"] = devs.get("amount_ratio", 1.0)
        devs["customer_zscore_amount"] = devs.get("amount_z_score", 0.0)
        devs["is_new_payee"] = 1 if is_cold else devs.get("is_new_beneficiary", 0)
        devs["is_new_device"] = 1 if is_cold else devs.get("device_novelty", 0)
        devs["is_new_location"] = 1 if is_cold else devs.get("location_novelty", 0)
        devs["is_cold_start"] = is_cold
        return devs

    def calculate_deviations(
        self,
        user_id: str,
        current_txn: Dict[str, Any],
    ) -> Dict[str, float]:
        """
        Compute multi-signal deviation features between current payment and user baseline.
        
        Returns:
            Dict of deviation metrics and normalized behavioural risk scores (0-100).
        """
        profile = self.get_user_profile(user_id)
        amt = float(current_txn.get("amount", 0.0))
        hour = int(current_txn.get("hour", current_txn.get("hour_of_day", 12)))
        day = int(current_txn.get("day_of_week", 0))
        beneficiary = str(current_txn.get("beneficiary_id", current_txn.get("nameDest", "")))
        device = str(current_txn.get("device_type", current_txn.get("device_id", "Mobile App")))
        location = str(current_txn.get("location", current_txn.get("location_region", "Domestic Home")))

        # 1. Amount Deviations
        avg_amt = profile.get("avg_amount", 2500.0)
        std_amt = max(10.0, profile.get("std_amount", 1000.0))
        amount_ratio = amt / max(1.0, avg_amt)
        amount_z_score = (amt - avg_amt) / std_amt
        amount_deviation_score = min(100.0, max(0.0, (amount_ratio - 1.0) * 20.0)) if amount_ratio > 1.0 else 0.0

        # 2. Temporal Deviation
        usual_hours = profile.get("usual_hours", list(range(8, 22)))
        is_unusual_hour = 1 if hour not in usual_hours else 0
        time_deviation_score = 75.0 if is_unusual_hour else 10.0

        # 3. Beneficiary Novelty
        common_bens = profile.get("common_beneficiaries", profile.get("known_recipients", []))
        is_new_ben = 1 if (not common_bens or beneficiary not in common_bens) else 0
        beneficiary_novelty_score = 80.0 if is_new_ben else 10.0

        # 4. Device & Location Novelty
        typ_dev = profile.get("typical_device", "Mobile App")
        typ_loc = profile.get("typical_location", "Domestic Home")
        known_devs = profile.get("known_devices", [typ_dev])
        known_locs = profile.get("known_locations", [typ_loc])

        dev_novelty = 1 if (device not in known_devs and device.lower() != typ_dev.lower()) or "proxy" in device.lower() or "vpn" in device.lower() else 0
        loc_novelty = 1 if (location not in known_locs and location.lower() != typ_loc.lower()) or "proxy" in location.lower() or "foreign" in location.lower() else 0
        device_deviation_score = 85.0 if dev_novelty else 10.0
        location_deviation_score = 85.0 if loc_novelty else 10.0

        # 5. Composite Behavioural Risk Index (0-100)
        # Weighted blend of deviations:
        # Amount: 35%, Beneficiary: 25%, Device: 15%, Location: 15%, Time: 10%
        composite_behavioural_score = (
            0.35 * amount_deviation_score +
            0.25 * beneficiary_novelty_score +
            0.15 * device_deviation_score +
            0.15 * location_deviation_score +
            0.10 * time_deviation_score
        )

        return {
            "user_baseline_avg": avg_amt,
            "user_baseline_std": std_amt,
            "current_amount": amt,
            "amount_ratio": round(amount_ratio, 2),
            "amount_z_score": round(amount_z_score, 2),
            "amount_deviation_score": round(amount_deviation_score, 1),
            "is_unusual_hour": is_unusual_hour,
            "time_deviation_score": round(time_deviation_score, 1),
            "is_new_beneficiary": is_new_ben,
            "beneficiary_novelty_score": round(beneficiary_novelty_score, 1),
            "device_novelty": dev_novelty,
            "device_deviation_score": round(device_deviation_score, 1),
            "location_novelty": loc_novelty,
            "location_deviation_score": round(location_deviation_score, 1),
            "composite_behavioural_score": round(min(100.0, max(0.0, composite_behavioural_score)), 1),
        }
