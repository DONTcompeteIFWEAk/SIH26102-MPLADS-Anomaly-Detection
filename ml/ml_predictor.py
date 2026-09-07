import os
import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
MODELS_DIR = BASE_DIR / "models"

SCALER_PATH = MODELS_DIR / "real_work_scaler.pkl"
IF_MODEL_PATH = MODELS_DIR / "real_work_isolation_forest.pkl"
PCA_PATH = MODELS_DIR / "real_work_pca.pkl"
METADATA_PATH = MODELS_DIR / "real_work_metadata.json"

class MPLADSAnomalyPredictor:
    def __init__(self):
        self.scaler = None
        self.if_model = None
        self.pca = None
        self.metadata = {}
        self.load_models()

    def load_models(self):
        try:
            if SCALER_PATH.exists():
                self.scaler = joblib.load(SCALER_PATH)
            if IF_MODEL_PATH.exists():
                self.if_model = joblib.load(IF_MODEL_PATH)
            if PCA_PATH.exists():
                self.pca = joblib.load(PCA_PATH)
            if METADATA_PATH.exists():
                with open(METADATA_PATH, "r", encoding="utf-8") as f:
                    self.metadata = json.load(f)
        except Exception as e:
            print(f"Error loading models: {e}")

    def predict_work(self, data: dict) -> dict:
        """
        Accepts dictionary containing proposed or inspected work parameters:
        {
            "work": str,
            "category": str,
            "state": str,
            "constituency": str,
            "village": str,
            "block": str,
            "allocation_amount": float,
            "days_since_recommendation": int,
            "status": str
        }
        Returns hybrid risk score, risk level, feature attribution, and CAG rule triggers.
        """
        allocation = float(data.get("allocation_amount", 0.0) or 0.0)
        work_text = str(data.get("work", "") or "").strip().lower()
        state = str(data.get("state", "") or "Default")
        category = str(data.get("category", "") or "Normal/Others")
        days = int(data.get("days_since_recommendation", 30) or 30)
        status = str(data.get("status", "Unsanctioned") or "Unsanctioned").lower()

        # Rule evaluation
        rule_split_tender = int(
            (475000 <= allocation <= 499999) or
            (950000 <= allocation <= 999999) or
            (2400000 <= allocation <= 2499999)
        )
        
        # Approximate baseline comparison
        state_median_estimate = 500000.0
        allocation_vs_state = allocation / max(state_median_estimate, 1.0)
        rule_high_state = int(allocation_vs_state >= 3.0)

        # Repetition heuristics
        repeat_count = int(data.get("same_work_location_count", 1) or 1)
        rule_cluster_work = int(repeat_count >= 3)
        rule_prolonged_inaction = int(days > 180 and "unsanctioned" in status)
        rule_vague = int(len(work_text) < 15 and allocation > 500000)

        rule_score = (
            rule_split_tender * 25 +
            rule_cluster_work * 25 +
            rule_high_state * 20 +
            rule_prolonged_inaction * 15 +
            rule_vague * 15
        )
        rule_score = min(100.0, float(rule_score))

        # ML Features vector
        features = self.metadata.get("features", [
            "allocation_amount_log", "allocation_vs_state_median",
            "allocation_vs_constituency_median", "allocation_vs_category_median",
            "days_since_recommendation", "recommendation_year",
            "recommendation_month", "recommendation_quarter",
            "work_description_length", "work_word_count",
            "same_work_description_count", "same_work_location_count",
            "split_tender_flag", "cluster_work_flag", "prolonged_inaction_flag"
        ])

        row_dict = {
            "allocation_amount_log": np.log1p(max(0.0, allocation)),
            "allocation_vs_state_median": allocation_vs_state,
            "allocation_vs_constituency_median": allocation_vs_state,
            "allocation_vs_category_median": allocation_vs_state,
            "days_since_recommendation": days,
            "recommendation_year": 2024,
            "recommendation_month": 3,
            "recommendation_quarter": 1,
            "work_description_length": len(work_text),
            "work_word_count": len(work_text.split()),
            "same_work_description_count": max(1, int(data.get("same_work_description_count", 1) or 1)),
            "same_work_location_count": repeat_count,
            "split_tender_flag": rule_split_tender,
            "cluster_work_flag": rule_cluster_work,
            "prolonged_inaction_flag": rule_prolonged_inaction
        }

        # Vector as DataFrame with column names
        vec_df = pd.DataFrame([row_dict])[features]

        ml_score = 50.0
        if self.scaler is not None and self.if_model is not None:
            try:
                vec_scaled = self.scaler.transform(vec_df)
                if_raw = -float(self.if_model.score_samples(vec_scaled)[0])
                # Calibrate to roughly 0-100
                ml_score = np.clip((if_raw + 0.6) * 100.0, 10.0, 99.0)
            except Exception as ex:
                print(f"Inference error: {ex}")

        hybrid_score = round(0.60 * ml_score + 0.40 * rule_score, 2)

        if hybrid_score >= 75:
            risk_level = "CRITICAL"
        elif hybrid_score >= 55:
            risk_level = "HIGH"
        elif hybrid_score >= 35:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        # Explainability
        reasons = []
        actions = []
        if rule_split_tender:
            reasons.append(f"Allocation Rs. {int(allocation):,} falls in high-risk tender split window (GFR Rule 149 evasion pattern)")
            actions.append("Examine if project was intentionally fragmented to bypass e-tender")
        if rule_cluster_work:
            reasons.append(f"Repeated identical work count ({repeat_count}) in the same localized area")
            actions.append("Mandate geo-tagged photo verification before releasing second milestone")
        if rule_high_state:
            reasons.append(f"Cost is {allocation_vs_state:.1f}x higher than standard median benchmarks")
            actions.append("Audit Detailed Project Report (DPR) unit rates")
        if rule_prolonged_inaction:
            reasons.append(f"Prolonged administrative dormancy ({days} days elapsed without sanction)")
            actions.append("Request status explanation from District Implementing Authority")
        if rule_vague:
            reasons.append("Non-specific description for substantial fund allocation")
            actions.append("Require itemized Bill of Quantities (BOQ)")

        if not reasons:
            reasons.append("Work metrics conform to typical MPLADS distribution patterns")
            actions.append("Routine administrative clearance")

        return {
            "allocation_amount": allocation,
            "ml_risk_score": round(ml_score, 2),
            "rule_risk_score": round(rule_score, 2),
            "hybrid_risk_score": hybrid_score,
            "risk_level": risk_level,
            "anomaly_flag": bool(hybrid_score >= 65.0),
            "rule_triggers": {
                "split_tender": bool(rule_split_tender),
                "cluster_work": bool(rule_cluster_work),
                "high_allocation": bool(rule_high_state),
                "prolonged_inaction": bool(rule_prolonged_inaction),
                "vague_description": bool(rule_vague)
            },
            "top_reasons": reasons[:3],
            "recommended_actions": actions[:2]
        }

# Global predictor instance
predictor = MPLADSAnomalyPredictor()
