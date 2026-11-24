"""
ROADGUARD AI - AI Road Damage Detector
Modular YOLO-based road damage detector. Supports custom fine-tuned checkpoints (models/best.pt),
standard pretrained checkpoints with mapping, and a clearly labeled fallback demonstration mode.
"""

import os
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional, Union
import logging
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2

from config import (
    DEFAULT_MODEL_PATH,
    MODELS_DIR,
    DAMAGE_CLASSES,
    CONFIDENCE_THRESHOLD,
    IOU_THRESHOLD
)

logger = logging.getLogger("roadguard.detector")

class RoadDamageDetector:
    """
    Manages YOLO model loading, inference, bounding box annotation,
    and structured detection extraction.
    """

    def __init__(self, model_path: Optional[Union[str, Path]] = None):
        self.model_path = Path(model_path) if model_path else DEFAULT_MODEL_PATH
        self.model = None
        self.model_status = "UNINITIALIZED"
        self.is_custom_model = False
        self.class_names: Dict[int, str] = {}
        self.load_error: Optional[str] = None
        self._initialize_model()

    def _initialize_model(self):
        """Attempts to load the configured YOLO model checkpoint."""
        # 1. Check if user-provided / default best.pt exists
        if self.model_path.exists():
            try:
                from ultralytics import YOLO
                self.model = YOLO(str(self.model_path))
                self.model_status = "CUSTOM_MODEL_LOADED"
                self.is_custom_model = True
                self.class_names = self.model.names if hasattr(self.model, "names") else {}
                logger.info(f"Loaded custom road damage model from {self.model_path}")
                return
            except Exception as e:
                self.load_error = f"Error loading checkpoint at {self.model_path}: {str(e)}"
                logger.error(self.load_error)

        # 2. Check if a fallback YOLO model is present in models/
        fallback_path = MODELS_DIR / "yolov8n.pt"
        if fallback_path.exists():
            try:
                from ultralytics import YOLO
                self.model = YOLO(str(fallback_path))
                self.model_status = "BASE_MODEL_LOADED"
                self.is_custom_model = False
                self.class_names = self.model.names if hasattr(self.model, "names") else {}
                logger.info("Loaded base YOLO model from models/yolov8n.pt")
                return
            except Exception as e:
                self.load_error = f"Error loading fallback model: {str(e)}"

        # 3. No local weights found
        self.model = None
        self.model_status = "CHECKPOINT_NOT_FOUND"
        self.is_custom_model = False
        logger.warning(f"No checkpoint found at {self.model_path}. Detector ready for model configuration.")

    def reload_model(self, new_path: Union[str, Path]) -> Tuple[bool, str]:
        """Allows switching or updating the model path dynamically."""
        target = Path(new_path)
        if not target.exists():
            return False, f"Model file not found at: {target}"
        try:
            from ultralytics import YOLO
            self.model = YOLO(str(target))
            self.model_path = target
            self.model_status = "CUSTOM_MODEL_LOADED"
            self.is_custom_model = True
            self.class_names = self.model.names if hasattr(self.model, "names") else {}
            self.load_error = None
            return True, f"Successfully loaded model from {target.name}"
        except Exception as e:
            return False, f"Failed to load weights: {str(e)}"

    def get_status_info(self) -> Dict[str, Any]:
        """Returns clean diagnostic information regarding model readiness."""
        return {
            "status": self.model_status,
            "model_path": str(self.model_path),
            "exists": self.model_path.exists(),
            "is_custom": self.is_custom_model,
            "classes": self.class_names,
            "error": self.load_error
        }

    def predict(
        self,
        image_input: Union[str, Path, Image.Image, np.ndarray],
        conf_threshold: float = CONFIDENCE_THRESHOLD,
        iou_threshold: float = IOU_THRESHOLD,
        allow_demo_fallback: bool = False
    ) -> Dict[str, Any]:
        """
        Executes damage detection on the provided road image.
        Returns bounding boxes, labels, confidence, and annotated image.
        """
        # Convert image to PIL and OpenCV formats
        if isinstance(image_input, (str, Path)):
            pil_img = Image.open(str(image_input)).convert("RGB")
        elif isinstance(image_input, np.ndarray):
            pil_img = Image.fromarray(cv2.cvtColor(image_input, cv2.COLOR_BGR2RGB) if len(image_input.shape) == 3 and image_input.shape[2] == 3 else image_input)
        elif isinstance(image_input, Image.Image):
            pil_img = image_input.convert("RGB")
        else:
            raise ValueError("Unsupported image input type")

        img_w, img_h = pil_img.size

        # Case A: Live Model Checkpoint is Available
        if self.model is not None:
            np_img = np.array(pil_img)
            results = self.model.predict(
                source=np_img,
                conf=conf_threshold,
                iou=iou_threshold,
                verbose=False
            )

            detections: List[Dict[str, Any]] = []
            annotated_np = np_img.copy()

            if results and len(results) > 0:
                res = results[0]
                boxes = res.boxes

                if boxes is not None and len(boxes) > 0:
                    for box in boxes:
                        xyxy = box.xyxy[0].cpu().numpy()
                        x1, y1, x2, y2 = float(xyxy[0]), float(xyxy[1]), float(xyxy[2]), float(xyxy[3])
                        conf = float(box.conf[0].cpu().numpy())
                        cls_id = int(box.cls[0].cpu().numpy())
                        raw_name = self.class_names.get(cls_id, f"Class {cls_id}")

                        # Map class name if custom road damage mapping matches
                        class_name = self._normalize_class_name(raw_name)

                        # Calculate relative area
                        box_w = max(0.0, x2 - x1)
                        box_h = max(0.0, y2 - y1)
                        area_ratio = (box_w * box_h) / float(img_w * img_h)

                        detections.append({
                            "class_id": cls_id,
                            "class_name": class_name,
                            "confidence": round(conf, 3),
                            "box_x1": round(x1, 1),
                            "box_y1": round(y1, 1),
                            "box_x2": round(x2, 1),
                            "box_y2": round(y2, 1),
                            "area_ratio": round(area_ratio, 4)
                        })

            # Annotate image
            annotated_pil = self._draw_annotations(pil_img, detections, is_demo=False)

            avg_conf = (
                sum(d["confidence"] for d in detections) / len(detections)
                if detections else 0.0
            )
            max_conf = (
                max(d["confidence"] for d in detections)
                if detections else 0.0
            )

            primary_type = "No Damage Detected"
            if detections:
                has_pothole = any("pothole" in d["class_name"].lower() for d in detections)
                has_crack = any("crack" in d["class_name"].lower() for d in detections)
                if has_pothole and has_crack:
                    primary_type = "Pothole & Surface Cracks"
                elif has_pothole:
                    primary_type = "Pothole"
                elif has_crack:
                    primary_type = "Crack"
                else:
                    primary_type = detections[0]["class_name"]

            return {
                "success": True,
                "is_demo": False,
                "model_source": f"YOLO ({self.model_path.name})",
                "detection_count": len(detections),
                "detections": detections,
                "primary_type": primary_type,
                "max_confidence": round(max_conf, 3),
                "avg_confidence": round(avg_conf, 3),
                "annotated_image": annotated_pil,
                "original_image": pil_img
            }

        # Case B: No Model Checkpoint Found
        if not allow_demo_fallback:
            return {
                "success": False,
                "is_demo": False,
                "error": (
                    f"No trained YOLO model weights found at '{self.model_path}'. "
                    f"Please place your trained road damage weights (e.g. best.pt) in the models/ directory "
                    f"or enable Demo Simulation Mode to preview pipeline functionality."
                ),
                "original_image": pil_img,
                "annotated_image": pil_img,
                "detections": [],
                "detection_count": 0
            }

        # Case C: Explicitly Requested Demo Simulation Mode (CLEARLY LABELED)
        return self._generate_labeled_demo_detection(pil_img)

    def _normalize_class_name(self, name: str) -> str:
        """Normalizes dataset class labels into human-readable road engineering terms."""
        nl = name.lower()
        if "d00" in nl or "pothole" in nl:
            return "Pothole"
        elif "d10" in nl or "alligator" in nl:
            return "Alligator Crack"
        elif "d20" in nl or "longitudinal" in nl:
            return "Longitudinal Crack"
        elif "d40" in nl or "transverse" in nl:
            return "Transverse Crack"
        elif "manhole" in nl:
            return "Manhole Cover Defect"
        return name.title()

    def _generate_labeled_demo_detection(self, pil_img: Image.Image) -> Dict[str, Any]:
        """
        Generates simulated demo detections for testing UI/database pipelines when no weights are installed.
        CRITICAL: All outputs are prominently tagged with '[DEMO SIMULATION]'.
        """
        img_w, img_h = pil_img.size

        # Generate realistic simulated sample detections proportional to image dimensions
        detections = [
            {
                "class_id": 0,
                "class_name": "Pothole [DEMO SIMULATION]",
                "confidence": 0.885,
                "box_x1": round(img_w * 0.28, 1),
                "box_y1": round(img_h * 0.42, 1),
                "box_x2": round(img_w * 0.62, 1),
                "box_y2": round(img_h * 0.76, 1),
                "area_ratio": round(((img_w * 0.34) * (img_h * 0.34)) / (img_w * img_h), 4)
            },
            {
                "class_id": 1,
                "class_name": "Longitudinal Crack [DEMO SIMULATION]",
                "confidence": 0.742,
                "box_x1": round(img_w * 0.68, 1),
                "box_y1": round(img_h * 0.30, 1),
                "box_x2": round(img_w * 0.82, 1),
                "box_y2": round(img_h * 0.65, 1),
                "area_ratio": round(((img_w * 0.14) * (img_h * 0.35)) / (img_w * img_h), 4)
            }
        ]

        annotated_pil = self._draw_annotations(pil_img, detections, is_demo=True)

        return {
            "success": True,
            "is_demo": True,
            "model_source": "DEMO SIMULATION (No weights at models/best.pt)",
            "detection_count": len(detections),
            "detections": detections,
            "primary_type": "Pothole & Surface Crack [DEMO]",
            "max_confidence": 0.885,
            "avg_confidence": 0.814,
            "annotated_image": annotated_pil,
            "original_image": pil_img
        }

    def _draw_annotations(
        self,
        pil_img: Image.Image,
        detections: List[Dict[str, Any]],
        is_demo: bool = False
    ) -> Image.Image:
        """Renders high-visibility bounding boxes and damage tags on the image."""
        annotated = pil_img.copy()
        draw = ImageDraw.Draw(annotated)
        w, h = annotated.size

        # Dynamic line width based on image resolution
        line_w = max(3, int(min(w, h) * 0.005))
        font_size = max(14, int(min(w, h) * 0.024))

        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except Exception:
            font = ImageFont.load_default()

        # Color mapping
        class_colors = {
            "pothole": "#EF4444",      # Vivid red
            "alligator": "#DC2626",    # Deep red
            "longitudinal": "#F59E0B", # Amber
            "transverse": "#FBBF24",   # Gold
            "crack": "#F59E0B",
            "demo": "#06B6D4"          # Cyan
        }

        for det in detections:
            x1, y1, x2, y2 = det["box_x1"], det["box_y1"], det["box_x2"], det["box_y2"]
            c_name = det["class_name"]
            conf = det["confidence"]

            # Select color
            color = "#EF4444"
            for k, hex_val in class_colors.items():
                if k in c_name.lower():
                    color = hex_val
                    break

            # Draw outer rectangle
            draw.rectangle([x1, y1, x2, y2], outline=color, width=line_w)

            # Label text
            label_text = f"{c_name} {int(conf * 100)}%"

            # Calculate label text bounding box
            try:
                left, top, right, bottom = draw.textbbox((x1, y1), label_text, font=font)
                text_w = right - left
                text_h = bottom - top
            except Exception:
                text_w, text_h = 100, 20

            # Draw label background badge
            badge_y1 = max(0, y1 - text_h - 8)
            badge_y2 = y1
            draw.rectangle([x1, badge_y1, x1 + text_w + 12, badge_y2], fill=color)
            draw.text((x1 + 6, badge_y1 + 2), label_text, fill="#FFFFFF", font=font)

        # Prominent watermark if Demo Mode
        if is_demo:
            demo_banner_h = max(28, int(h * 0.04))
            draw.rectangle([0, 0, w, demo_banner_h], fill="#0F172A")
            demo_msg = "[DEMO SIMULATION DATA - PLACE TRAINED WEIGHTS IN models/best.pt FOR REAL PREDICTIONS]"
            draw.text((12, 6), demo_msg, fill="#38BDF8", font=font)

        return annotated


# Global singleton instance helper
_detector_instance: Optional[RoadDamageDetector] = None

def get_detector(model_path: Optional[Union[str, Path]] = None) -> RoadDamageDetector:
    global _detector_instance
    if _detector_instance is None or (model_path and Path(model_path) != _detector_instance.model_path):
        _detector_instance = RoadDamageDetector(model_path)
    return _detector_instance
