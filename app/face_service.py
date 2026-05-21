from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from app.config import FACE_MATCH_THRESHOLD, FACES_DIR, ensure_directories


class FaceServiceError(RuntimeError):
    pass


class FaceService:
    def __init__(self) -> None:
        ensure_directories()
        self._face_analysis = None
        self._load_error = None
        self._initialize_face_analysis()

    def _initialize_face_analysis(self) -> None:
        try:
            self._face_analysis = self._load_face_analysis()
        except FaceServiceError as error:
            self._load_error = str(error)

    def _load_face_analysis(self):
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

    def extract_face_data(self, frame: np.ndarray) -> tuple[np.ndarray, list[float]]:
        if self._face_analysis is None:
            raise FaceServiceError(self._load_error or "InsightFace no esta disponible.")

        faces = self._face_analysis.get(frame)
        if not faces:
            raise FaceServiceError("No se detecto ningun rostro en la captura.")
        if len(faces) > 1:
            raise FaceServiceError("Se detectaron varios rostros. Debe haber solo uno.")

        face = faces[0]
        x1, y1, x2, y2 = [int(value) for value in face.bbox]
        height, width = frame.shape[:2]
        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(width, x2)
        y2 = min(height, y2)
        if x2 <= x1 or y2 <= y1:
            raise FaceServiceError("No se pudo recortar el rostro detectado.")

        cropped_face = frame[y1:y2, x1:x2]
        resized_face = cv2.resize(cropped_face, (224, 224), interpolation=cv2.INTER_AREA)
        embedding = face.embedding.astype(float).tolist()
        return resized_face, embedding

    def save_face_image(self, username: str, face_image: np.ndarray) -> str:
        safe_username = self._normalize_username(username)
        image_path = FACES_DIR / f"{safe_username}.jpg"
        if not cv2.imwrite(str(image_path), face_image):
            raise FaceServiceError("No se pudo guardar la imagen facial.")
        return str(image_path)

    def verify_face(self, stored_embedding: list[float], candidate_embedding: list[float]) -> bool:
        reference = np.asarray(stored_embedding, dtype=np.float32)
        candidate = np.asarray(candidate_embedding, dtype=np.float32)
        distance = np.linalg.norm(reference - candidate)
        return float(distance) <= FACE_MATCH_THRESHOLD

    @staticmethod
    def _normalize_username(username: str) -> str:
        normalized = "".join(character for character in username if character.isalnum() or character in {"_", "-"})
        if not normalized:
            raise FaceServiceError("El nombre de usuario contiene caracteres invalidos.")
        return normalized
