import cv2

from app.config import CAMERA_INDEX, CAPTURE_WINDOW_NAME


class CameraError(RuntimeError):
    pass


class CameraService:
    def capture_frame(self) -> object:
        capture = cv2.VideoCapture(CAMERA_INDEX)
        if not capture.isOpened():
            raise CameraError("No se pudo abrir la camara.")

        frame = None

        try:
            while True:
                success, current_frame = capture.read()
                if not success:
                    raise CameraError("No se pudo leer un frame de la camara.")

                frame = current_frame
                cv2.imshow(CAPTURE_WINDOW_NAME, frame)
                key = cv2.waitKey(1) & 0xFF
                window_visible = cv2.getWindowProperty(CAPTURE_WINDOW_NAME, cv2.WND_PROP_VISIBLE)

                if key == 27:
                    if frame is None:
                        raise CameraError("No se capturo ninguna imagen.")
                    return frame

                if window_visible < 1:
                    raise CameraError("La captura fue cancelada desde la ventana de la camara.")
        finally:
            capture.release()
            cv2.destroyAllWindows()
