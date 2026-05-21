from tkinter import Button, END, Entry, Label, LabelFrame, StringVar, Tk, Toplevel, messagebox

from app.auth_service import AuthService, HANDLED_AUTH_ERRORS


class FaceLoginUI:
    def __init__(self, auth_service: AuthService) -> None:
        self.auth_service = auth_service
        self.root = Tk()
        self.root.geometry("340x260")
        self.root.title("Face Login")
        self._build_home()

    def run(self) -> None:
        self.root.mainloop()

    def _build_home(self) -> None:
        Label(
            self.root,
            text="Login Inteligente",
            bg="gray",
            width=300,
            height=2,
            font=("Verdana", 13),
        ).pack()
        Label(self.root, text="").pack()
        Button(self.root, text="Iniciar Sesion", height=2, width=30, command=self._open_login).pack()
        Label(self.root, text="").pack()
        Button(self.root, text="Registro", height=2, width=30, command=self._open_register).pack()
        if not self.auth_service.face_service.is_available():
            Label(
                self.root,
                text=self.auth_service.face_service.availability_error(),
                fg="red",
                wraplength=300,
                justify="left",
            ).pack(pady=12)

    def _open_register(self) -> None:
        window = Toplevel(self.root)
        window.title("Registro")
        window.geometry("360x520")

        username = StringVar()
        password = StringVar()

        Label(window, text="Usuario *", font=("Calibri", 11, "bold")).pack(pady=(8, 0))
        Entry(window, textvariable=username, width=32).pack(pady=(2, 12))

        trad_frame = LabelFrame(window, text="Registro Tradicional", padx=8, pady=6)
        trad_frame.pack(fill="x", padx=12, pady=(0, 8))
        Label(trad_frame, text="Contrasena *").pack()
        Entry(trad_frame, textvariable=password, show="*", width=28).pack(pady=(2, 6))
        Button(
            trad_frame,
            text="Registrar con usuario + contrasena",
            width=30,
            command=lambda: self._execute_action(
                action=lambda: self.auth_service.register_password(username.get(), password.get()),
                status_label=status,
                username_var=username,
                password_var=password,
                owner=window,
            ),
        ).pack(pady=(4, 2))

        face_frame = LabelFrame(window, text="Registro Facial", padx=8, pady=6)
        face_frame.pack(fill="x", padx=12, pady=(0, 8))
        Label(
            face_frame,
            text="Solo necesitas un usuario.\nNo requiere contrasena.",
            wraplength=280,
            justify="left",
            fg="gray30",
        ).pack(pady=(2, 6))
        Button(
            face_frame,
            text="Registrar con rostro",
            width=30,
            command=lambda: self._execute_action(
                action=lambda: self.auth_service.register_face(username.get()),
                status_label=status,
                username_var=username,
                password_var=password,
                clear_password=False,
                owner=window,
            ),
        ).pack(pady=(2, 4))

        Label(
            window,
            text="Presiona Esc para capturar o\ncierra la ventana de camara para cancelar.",
            wraplength=300,
            fg="gray40",
            font=("Calibri", 8),
        ).pack(pady=(4, 6))

        status = Label(window, text="", wraplength=300, justify="left", fg="black")
        status.pack(pady=(0, 8))

    def _open_login(self) -> None:
        window = Toplevel(self.root)
        window.title("Login")
        window.geometry("360x520")

        username = StringVar()
        password = StringVar()

        Label(window, text="Usuario *", font=("Calibri", 11, "bold")).pack(pady=(8, 0))
        Entry(window, textvariable=username, width=32).pack(pady=(2, 12))

        trad_frame = LabelFrame(window, text="Login Tradicional", padx=8, pady=6)
        trad_frame.pack(fill="x", padx=12, pady=(0, 8))
        Label(trad_frame, text="Contrasena *").pack()
        Entry(trad_frame, textvariable=password, show="*", width=28).pack(pady=(2, 6))
        Button(
            trad_frame,
            text="Iniciar con contrasena",
            width=30,
            command=lambda: self._execute_action(
                action=lambda: self.auth_service.login_password(username.get(), password.get()),
                status_label=status,
                username_var=username,
                password_var=password,
                owner=window,
            ),
        ).pack(pady=(4, 2))

        face_frame = LabelFrame(window, text="Login Facial", padx=8, pady=6)
        face_frame.pack(fill="x", padx=12, pady=(0, 8))
        Label(
            face_frame,
            text="Solo necesitas tu rostro.\nNo requiere contrasena.",
            wraplength=280,
            justify="left",
            fg="gray30",
        ).pack(pady=(2, 6))
        Button(
            face_frame,
            text="Iniciar con rostro",
            width=30,
            command=lambda: self._execute_action(
                action=lambda: self.auth_service.login_face(username.get()),
                status_label=status,
                username_var=username,
                password_var=password,
                clear_password=False,
                owner=window,
            ),
        ).pack(pady=(2, 4))

        Label(
            window,
            text="Presiona Esc para capturar o\ncierra la ventana de camara para cancelar.",
            wraplength=300,
            fg="gray40",
            font=("Calibri", 8),
        ).pack(pady=(4, 6))

        status = Label(window, text="", wraplength=300, justify="left", fg="black")
        status.pack(pady=(0, 8))

    def _execute_action(
        self,
        action,
        status_label: Label,
        username_var: StringVar,
        password_var: StringVar,
        owner: Toplevel,
        clear_password: bool = True,
    ) -> None:
        try:
            message = action()
        except HANDLED_AUTH_ERRORS as error:
            status_label.config(text=str(error), fg="red")
            messagebox.showerror("Error", str(error), parent=owner)
        else:
            status_label.config(text=message, fg="green")
            messagebox.showinfo("Exito", message, parent=owner)
            username_var.set("")
            if clear_password:
                password_var.set("")
