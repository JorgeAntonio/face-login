from __future__ import annotations

from collections.abc import Callable

import cv2

from app.config import CAMERA_INDEX, CAPTURE_WINDOW_NAME

FaceDetector = Callable[[object], list]
FaceDrawer = Callable[[object, list], object]


class CameraError(RuntimeError):
    pass


class CameraService:
    def capture_frame(
        self,
        face_detector: FaceDetector | None = None,
        face_drawer: FaceDrawer | None = None,
    ) -> tuple[object, list]:
        capture = cv2.VideoCapture(CAMERA_INDEX)
        if not capture.isOpened():
            raise CameraError("No se pudo abrir la camara.")

        frame = None
        detected_faces: list = []
        frame_count = 0
        detection_interval = 3

        try:
            while True:
                success, current_frame = capture.read()
                if not success:
                    raise CameraError("No se pudo leer un frame de la camara.")

                frame = current_frame

                if face_detector is not None and frame_count % detection_interval == 0:
                    detected_faces = face_detector(frame)

                display_frame = frame
                if face_drawer is not None and detected_faces:
                    display_frame = face_drawer(frame, detected_faces)

                cv2.imshow(CAPTURE_WINDOW_NAME, display_frame)
                key = cv2.waitKey(1) & 0xFF
                window_visible = cv2.getWindowProperty(CAPTURE_WINDOW_NAME, cv2.WND_PROP_VISIBLE)
                frame_count += 1

                if key == 27:
                    if frame is None:
                        raise CameraError("No se capturo ninguna imagen.")
                    return frame, detected_faces

                if window_visible < 1:
                    raise CameraError("La captura fue cancelada desde la ventana de la camara.")
        finally:
            capture.release()
            cv2.destroyAllWindows()
