from app.auth_service import AuthService
from app.camera_service import CameraService
from app.database import Database
from app.face_service import FaceService
from app.ui import FaceLoginUI


def main() -> None:
    database = Database()
    camera_service = CameraService()
    face_service = FaceService()
    auth_service = AuthService(database, camera_service, face_service)
    FaceLoginUI(auth_service).run()
