from typing import List, Dict, Tuple, Optional
import math


class HazardEngine:
    """
    Aegis AI - Hazard Intelligence Engine
    Version 8.0 (Hackathon Edition)

    Features:
    - PPE Detection
    - Worker Risk Assessment
    - Machinery & Vehicle Proximity Analysis
    - Risk Scoring
    - Hazard & Recommendation Generation
    """

    MIN_CONFIDENCE = 0.40

    SAFE_DISTANCE = 180
    HIGH_DISTANCE = 120
    CRITICAL_DISTANCE = 60

    ENVIRONMENT = "Factory"
    STATUS = "Completed"

    DUPLICATE_THRESHOLD = 80

    # ---------------------------------------------------------
    # Geometry
    # ---------------------------------------------------------

    def distance(
        self,
        p1: Tuple[int, int],
        p2: Tuple[int, int]
    ) -> float:
        """Calculate Euclidean distance."""

        return math.sqrt(
            (p1[0] - p2[0]) ** 2 +
            (p1[1] - p2[1]) ** 2
        )

    # ---------------------------------------------------------
    # Utilities
    # ---------------------------------------------------------

    def unique(self, items: List[str]) -> List[str]:
        """Remove duplicated items while preserving order."""
        return list(dict.fromkeys(items))

    def filter_detections(
        self,
        detections: List[Dict]
    ) -> List[Dict]:
        """Ignore detections below confidence threshold."""

        return [
            detection
            for detection in detections
            if detection.get("confidence", 1.0)
            >= self.MIN_CONFIDENCE
        ]

    # ---------------------------------------------------------
    # Object Classification
    # ---------------------------------------------------------

    def classify_objects(
        self,
        detections: List[Dict]
    ) -> Dict:

        people = []
        machinery = []
        vehicles = []
        labels = set()

        for detection in detections:

            label = detection["class"].lower()

            labels.add(label)

            if label == "person":
                people.append(detection)

            elif label == "machinery":
                machinery.append(detection)

            elif label == "vehicle":
                vehicles.append(detection)

        return {
            "people": people,
            "machinery": machinery,
            "vehicles": vehicles,
            "labels": labels
        }

    # ---------------------------------------------------------
    # Duplicate Suppression
    # ---------------------------------------------------------

    def group_large_objects(
        self,
        objects: List[Dict]
    ) -> List[Dict]:

        if not objects:
            return []

        objects = sorted(
            objects,
            key=lambda obj: obj["confidence"],
            reverse=True
        )

        grouped = []

        for obj in objects:

            duplicate = False

            ox1, oy1, ox2, oy2 = obj["bbox"]

            for kept in grouped:

                kx1, ky1, kx2, ky2 = kept["bbox"]

                if (
                    abs(ox1 - kx1) < self.DUPLICATE_THRESHOLD
                    and
                    abs(oy1 - ky1) < self.DUPLICATE_THRESHOLD
                    and
                    abs(ox2 - kx2) < self.DUPLICATE_THRESHOLD
                    and
                    abs(oy2 - ky2) < self.DUPLICATE_THRESHOLD
                ):
                    duplicate = True
                    break

            if not duplicate:
                grouped.append(obj)

        return grouped

    # ---------------------------------------------------------
    # Nearest Object
    # ---------------------------------------------------------

    def nearest_object(
        self,
        person: Dict,
        objects: List[Dict]
    ) -> Tuple[
        Optional[Dict],
        Optional[float]
    ]:

        if not objects:
            return None, None

        nearest = None
        nearest_distance = float("inf")

        for obj in objects:

            current_distance = self.distance(
                person["center"],
                obj["center"]
            )

            if current_distance < nearest_distance:

                nearest_distance = current_distance
                nearest = obj

        return nearest, nearest_distance

    # ---------------------------------------------------------
    # Risk Classification
    # ---------------------------------------------------------

    def risk_level(
        self,
        distance: float
    ) -> Tuple[str, int]:

        if distance <= self.CRITICAL_DISTANCE:
            return "critical", 30

        if distance <= self.HIGH_DISTANCE:
            return "high", 20

        if distance <= self.SAFE_DISTANCE:
            return "medium", 10

        return "safe", 0

            # ---------------------------------------------------------
    # Main Analysis
    # ---------------------------------------------------------

    def analyze(
        self,
        detections: List[Dict]
    ) -> Dict:

        detections = self.filter_detections(detections)

        data = self.classify_objects(detections)

        people = data["people"]
        machinery = self.group_large_objects(data["machinery"])
        vehicles = self.group_large_objects(data["vehicles"])
        labels = data["labels"]

        hazards = []
        recommendations = []
        workers = []

        risk_score = 0

        has_person = len(people) > 0

        # -------------------------------------------------
        # PPE Detection
        # -------------------------------------------------

        has_hardhat = "hardhat" in labels
        has_no_hardhat = "no-hardhat" in labels

        has_vest = "safety vest" in labels
        has_no_vest = "no-safety vest" in labels

        has_mask = "mask" in labels
        has_no_mask = "no-mask" in labels

        if has_person:

            if has_no_hardhat and not has_hardhat:

                hazards.append(
                    "Worker without hardhat."
                )

                recommendations.append(
                    "Wear a safety helmet."
                )

                risk_score += 35

            if has_no_vest and not has_vest:

                hazards.append(
                    "Worker without safety vest."
                )

                recommendations.append(
                    "Wear a high-visibility safety vest."
                )

                risk_score += 25

            if has_no_mask and not has_mask:

                hazards.append(
                    "Worker without protective mask."
                )

                recommendations.append(
                    "Wear an approved safety mask."
                )

                risk_score += 15

        # -------------------------------------------------
        # Worker Analysis
        # -------------------------------------------------

        for index, person in enumerate(
            people,
            start=1
        ):

            nearest_name = None
            nearest_distance = None

            worker_risk = "SAFE"

            machine, machine_distance = self.nearest_object(
                person,
                machinery
            )

            vehicle, vehicle_distance = self.nearest_object(
                person,
                vehicles
            )

            if (
                machine_distance is not None
                and
                (
                    vehicle_distance is None
                    or
                    machine_distance <= vehicle_distance
                )
            ):

                nearest_name = "machinery"
                nearest_distance = machine_distance

            elif vehicle_distance is not None:

                nearest_name = "vehicle"
                nearest_distance = vehicle_distance

            if (
                nearest_distance is not None
                and
                nearest_distance < self.SAFE_DISTANCE
            ):

                worker_risk, score = self.risk_level(
                    nearest_distance
                )

                # Machinery receives a slightly higher weight

                if nearest_name == "machinery":
                    risk_score += score + 5
                else:
                    risk_score += score

                hazards.append(
                    f"Worker {worker_risk} proximity to {nearest_name} ({nearest_distance:.0f}px)."
                )

                if nearest_name == "machinery":

                    recommendations.append(
                        "Increase separation from machinery."
                    )

                else:

                    recommendations.append(
                        "Maintain safe distance from vehicles."
                    )

            workers.append({

                "worker_id": index,

                "risk": worker_risk.upper(),

                "nearest_object": nearest_name,

                "distance": (
                    round(nearest_distance)
                    if nearest_distance is not None
                    else None
                ),

                "ppe": {

                    "helmet_detected": has_hardhat,

                    "vest_detected": has_vest,

                    "mask_detected": has_mask

                }

            })
                    # -------------------------------------------------
        # Remove Duplicate Messages
        # -------------------------------------------------

        hazards = self.unique(hazards)
        recommendations = self.unique(recommendations)

        # -------------------------------------------------
        # Normalize Risk Score
        # -------------------------------------------------

        risk_score = min(risk_score, 100)

        # -------------------------------------------------
        # Severity Classification
        # -------------------------------------------------

        if risk_score >= 80:
            severity = "CRITICAL"

        elif risk_score >= 60:
            severity = "HIGH"

        elif risk_score >= 30:
            severity = "MEDIUM"

        else:
            severity = "LOW"

        # -------------------------------------------------
        # Analysis Summary
        # -------------------------------------------------

        summary = {

            "workers": len(people),

            "machinery": len(machinery),

            "vehicles": len(vehicles),

            "hazards": len(hazards),

            "recommendations": len(recommendations)

        }

        # -------------------------------------------------
        # Final Report
        # -------------------------------------------------

        return {

            # -------------------------------------------------
            # Existing Fields (Backward Compatible)
            # -------------------------------------------------

            "severity": severity,

            "risk_score": risk_score,

            "workers": workers,

            "hazards": hazards,

            "recommendations": recommendations,

            # -------------------------------------------------
            # New Metadata
            # -------------------------------------------------

            "environment": self.ENVIRONMENT,

            "analysis_status": self.STATUS,

            "summary": summary

        }