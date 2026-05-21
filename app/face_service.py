from __future__ import annotations

from pathlib import Path
from typing import Any

import cv2
import numpy as np

from app.config import FACE_MATCH_THRESHOLD, FACES_DIR, ensure_directories

_LANDMARK_COLOR = (255, 255, 0)
_BBOX_COLOR = (0, 255, 0)
_COUNTER_COLOR = (255, 255, 255)
_HELP_COLOR = (200, 200, 200)
_BBOX_THICKNESS = 2
_LANDMARK_RADIUS = 2
_FONT = cv2.FONT_HERSHEY_SIMPLEX


class FaceServiceError(RuntimeError):
    pass


class FaceService:
    def __init__(self) -> None:
        ensure_directories()
        self._face_analysis: Any = None
        self._load_error: str | None = None
        self._initialize_face_analysis()

    def _initialize_face_analysis(self) -> None:
        try:
            self._face_analysis = self._load_face_analysis()
        except FaceServiceError as error:
            self._load_error = str(error)

    def _load_face_analysis(self) -> Any:
        try:
            from insightface.app import FaceAnalysis
        except ImportError as error:
            raise FaceServiceError(
                "InsightFace no esta instalado. Instala 'insightface' y 'onnxruntime'."
            ) from error

        analysis = FaceAnalysis(name="buffalo_l")
        try:
            analysis.prepare(ctx_id=0, det_size=(640, 640))
        except Exception:
            analysis.prepare(ctx_id=-1, det_size=(640, 640))
        return analysis

    def is_available(self) -> bool:
        return self._face_analysis is not None

    def availability_error(self) -> str | None:
        return self._load_error

    def detect_faces(self, frame: np.ndarray) -> list:
        if self._face_analysis is None:
            return []
        return self._face_analysis.get(frame)

    def draw_preview(self, frame: np.ndarray, faces: list) -> np.ndarray:
        canvas = frame.copy()
        height, width = canvas.shape[:2]

        for face in faces:
            x1, y1, x2, y2 = [int(v) for v in face.bbox]
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(width, x2), min(height, y2)
            cv2.rectangle(canvas, (x1, y1), (x2, y2), _BBOX_COLOR, _BBOX_THICKNESS)

            if hasattr(face, "kps") and face.kps is not None:
                for kp in face.kps:
                    px, py = int(kp[0]), int(kp[1])
                    cv2.circle(canvas, (px, py), _LANDMARK_RADIUS, _LANDMARK_COLOR, -1)

        face_label = f"Rostros detectados: {len(faces)}"
        (label_w, label_h), baseline = cv2.getTextSize(face_label, _FONT, 0.7, 2)
        overlay = canvas.copy()
        cv2.rectangle(
            overlay, (8, 4), (12 + label_w, 8 + label_h + baseline), (0, 0, 0), -1,
        )
        canvas = cv2.addWeighted(overlay, 0.6, canvas, 0.4, 0)
        cv2.putText(
            canvas, face_label, (10, 16 + label_h), _FONT, 0.7, _COUNTER_COLOR, 2,
        )

        help_text = "Esc: capturar  |  Cerrar ventana: cancelar"
        (help_w, help_h), _ = cv2.getTextSize(help_text, _FONT, 0.5, 1)
        help_y = height - 10
        overlay = canvas.copy()
        cv2.rectangle(
            overlay,
            (8, help_y - help_h - 6),
            (12 + help_w, help_y + 4),
            (0, 0, 0),
            -1,
        )
        canvas = cv2.addWeighted(overlay, 0.6, canvas, 0.4, 0)
        cv2.putText(
            canvas, help_text, (10, help_y), _FONT, 0.5, _HELP_COLOR, 1,
        )

        return canvas

    def extract_face_data(self, frame: np.ndarray) -> tuple[np.ndarray, list[float]]:
        faces = self.detect_faces(frame)
        if not faces:
            raise FaceServiceError("No se detecto ningun rostro en la captura.")
        if len(faces) > 1:
            raise FaceServiceError("Se detectaron varios rostros. Debe haber solo uno.")
        return self.extract_from_face(faces[0], frame)

    def extract_from_face(self, face: Any, frame: np.ndarray) -> tuple[np.ndarray, list[float]]:
        if self._face_analysis is None:
            raise FaceServiceError(self._load_error or "InsightFace no esta disponible.")

        x1, y1, x2, y2 = [int(value) for value in face.bbox]
        height, width = frame.shape[:2]
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(width, x2), min(height, y2)
        if x2 <= x1 or y2 <= y1:
            raise FaceServiceError("No se pudo recortar el rostro detectado.")

        cropped_face = frame[y1:y2, x1:x2]
        resized_face = cv2.resize(cropped_face, (224, 224), interpolation=cv2.INTER_AREA)
        raw_embedding = face.embedding.astype(float)
        embedding = (raw_embedding / np.linalg.norm(raw_embedding)).tolist()
        return resized_face, embedding

    def save_face_image(self, username: str, face_image: np.ndarray) -> str:
        safe_username = self._normalize_username(username)
        image_path = FACES_DIR / f"{safe_username}.jpg"
        if not cv2.imwrite(str(image_path), face_image):
            raise FaceServiceError("No se pudo guardar la imagen facial.")
        return str(image_path)

    def verify_face(self, stored_embedding: list[float], candidate_embedding: list[float]) -> bool:
        reference = np.asarray(stored_embedding, dtype=np.float32)
        raw_candidate = np.asarray(candidate_embedding, dtype=np.float32)
        candidate = raw_candidate / np.linalg.norm(raw_candidate)
        distance = np.linalg.norm(reference - candidate)
        return float(distance) <= FACE_MATCH_THRESHOLD

    @staticmethod
    def _normalize_username(username: str) -> str:
        normalized = "".join(c for c in username if c.isalnum() or c in {"_", "-"})
        if not normalized:
            raise FaceServiceError("El nombre de usuario contiene caracteres invalidos.")
        return normalized
