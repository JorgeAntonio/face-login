from __future__ import annotations

import json

from app.camera_service import CameraError, CameraService
from app.database import Database
from app.face_service import FaceService, FaceServiceError
from app.security import hash_password, verify_password


class AuthService:
    def __init__(self, database: Database, camera_service: CameraService, face_service: FaceService) -> None:
        self.database = database
        self.camera_service = camera_service
        self.face_service = face_service

    def register_password(self, username: str, password: str) -> str:
        username = self._validate_username(username)
        if not password:
            raise ValueError("La contrasena es obligatoria.")

        self.database.upsert_user(username, hash_password(password))
        return "Registro tradicional completado."

    def register_face(self, username: str) -> str:
        username = self._validate_username(username)
        self.database.upsert_user(username)

        frame, _ = self.camera_service.capture_frame(
            face_detector=self.face_service.detect_faces,
            face_drawer=self.face_service.draw_preview,
        )

        face_image, embedding = self.face_service.extract_face_data(frame)

        image_path = self.face_service.save_face_image(username, face_image)
        self.database.update_face_data(username, image_path, embedding)
        return "Registro facial completado."

    def login_password(self, username: str, password: str) -> str:
        username = self._validate_username(username)
        user = self.database.get_user(username)
        if user is None:
            self.database.record_auth_attempt(username, "password", False, "usuario_no_encontrado")
            raise ValueError("Usuario no encontrado.")

        password_hash = user["password_hash"]
        if not password_hash or not verify_password(password, password_hash):
            self.database.record_auth_attempt(username, "password", False, "contrasena_incorrecta")
            raise ValueError("Contrasena incorrecta.")

        self.database.record_auth_attempt(username, "password", True, "ok")
        return "Inicio de sesion tradicional exitoso."

    def login_face(self, username: str) -> str:
        username = self._validate_username(username)
        user = self.database.get_user(username)
        if user is None:
            self.database.record_auth_attempt(username, "face", False, "usuario_no_encontrado")
            raise ValueError("Usuario no encontrado.")

        if not user["face_embedding"]:
            self.database.record_auth_attempt(username, "face", False, "rostro_no_registrado")
            raise ValueError("El usuario no tiene rostro registrado.")

        frame, _ = self.camera_service.capture_frame(
            face_detector=self.face_service.detect_faces,
            face_drawer=self.face_service.draw_preview,
        )

        _, candidate_embedding = self.face_service.extract_face_data(frame)

        stored_embedding = json.loads(user["face_embedding"])
        is_match = self.face_service.verify_face(stored_embedding, candidate_embedding)
        if not is_match:
            self.database.record_auth_attempt(username, "face", False, "rostro_no_coincide")
            raise ValueError("El rostro no coincide con el usuario registrado.")

        self.database.record_auth_attempt(username, "face", True, "ok")
        return "Inicio de sesion facial exitoso."

    @staticmethod
    def _validate_username(username: str) -> str:
        cleaned_username = username.strip()
        if not cleaned_username:
            raise ValueError("El usuario es obligatorio.")
        return cleaned_username


HANDLED_AUTH_ERRORS = (ValueError, CameraError, FaceServiceError)
