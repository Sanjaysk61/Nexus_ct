from typing import Any, Dict, List

import numpy as np
from sklearn.ensemble import IsolationForest


class ProcurementMLModel:

    def __init__(self):
        self.model = IsolationForest(
            n_estimators=150,
            contamination="auto",
            random_state=42,
        )

        self.feature_names = [
            "purchase_order_value",
            "supplier_reliability",
            "complexity_score",
            "supplier_risk_score",
        ]

        self.is_trained = False

    def _complexity_score(
        self,
        complexity: str,
    ) -> float:
        mapping = {
            "SIMPLE": 0.10,
            "MODERATE": 0.35,
            "COMPLEX": 0.65,
            "HIGH_COMPLEXITY": 1.00,
        }

        return mapping.get(
            str(complexity).upper(),
            0.10,
        )

    def _supplier_risk_score(
        self,
        supplier_risk: str,
    ) -> float:
        mapping = {
            "LOW": 0.10,
            "MEDIUM": 0.50,
            "HIGH": 1.00,
        }

        return mapping.get(
            str(supplier_risk).upper(),
            0.10,
        )

    def _features(
        self,
        procurement_data: Dict[str, Any],
    ) -> List[float]:

        value = float(
            procurement_data.get(
                "purchase_order_value",
                0,
            )
            or 0
        )

        reliability = float(
            procurement_data.get(
                "supplier_reliability_score",
                1.0,
            )
            or 1.0
        )

        complexity = self._complexity_score(
            procurement_data.get(
                "complexity",
                "SIMPLE",
            )
        )

        supplier_risk = self._supplier_risk_score(
            procurement_data.get(
                "supplier_risk",
                "LOW",
            )
        )

        return [
            np.log1p(value),
            reliability,
            complexity,
            supplier_risk,
        ]

    def train(
        self,
        procurement_records: List[Dict[str, Any]],
    ):

        if len(procurement_records) < 5:
            self.is_trained = False

            return {
                "status": "INSUFFICIENT_DATA",
                "records": len(
                    procurement_records
                ),
                "required": 5,
            }

        matrix = [
            self._features(record)
            for record in procurement_records
        ]

        self.model.fit(matrix)

        self.is_trained = True

        return {
            "status": "TRAINED",
            "records": len(
                procurement_records
            ),
            "features": self.feature_names,
            "algorithm": "ISOLATION_FOREST",
        }

    def predict(
        self,
        procurement_data: Dict[str, Any],
    ):

        if not self.is_trained:
            return {
                "status": "MODEL_NOT_TRAINED",
                "prediction_available": False,
            }

        features = [
            self._features(
                procurement_data
            )
        ]

        prediction = int(
            self.model.predict(features)[0]
        )

        anomaly_score = float(
            -self.model.decision_function(
                features
            )[0]
        )

        anomaly_score = max(
            0.0,
            min(
                anomaly_score,
                1.0,
            ),
        )

        if prediction == -1:
            predicted_risk = "HIGH"

        elif anomaly_score >= 0.25:
            predicted_risk = "MEDIUM"

        else:
            predicted_risk = "LOW"

        return {
            "status": "SUCCESS",
            "prediction_available": True,
            "ml_anomaly": prediction == -1,
            "ml_anomaly_score": round(
                anomaly_score,
                4,
            ),
            "ml_predicted_risk": predicted_risk,
            "algorithm": "ISOLATION_FOREST",
            "features": {
                name: value
                for name, value in zip(
                    self.feature_names,
                    features[0],
                )
            },
        }


ml_model = ProcurementMLModel()