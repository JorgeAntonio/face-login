from tkinter import Button, END, Entry, Label, StringVar, Tk, Toplevel, messagebox

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
        window.geometry("340x420")
        username = StringVar()
        password = StringVar()

        Label(window, text="Registro facial: ingresa un usuario.").pack()
        Label(window, text="Registro tradicional: usuario y contrasena.").pack()
        Label(window, text="").pack()
        Label(window, text="Usuario *").pack()
        username_entry = Entry(window, textvariable=username)
        username_entry.pack()
        Label(window, text="Contrasena *").pack()
        password_entry = Entry(window, textvariable=password, show="*")
        password_entry.pack()
        Label(window, text="").pack()

        status = Label(window, text="", wraplength=300, justify="left", fg="black")
        status.pack(pady=6)

        Button(
            window,
            text="Registro Tradicional",
            width=18,
            command=lambda: self._execute_action(
                action=lambda: self.auth_service.register_password(username.get(), password.get()),
                status_label=status,
                username_entry=username_entry,
                password_entry=password_entry,
                owner=window,
            ),
        ).pack(pady=2)
        Button(
            window,
            text="Registro Facial",
            width=18,
            command=lambda: self._execute_action(
                action=lambda: self.auth_service.register_face(username.get()),
                status_label=status,
                username_entry=username_entry,
                password_entry=password_entry,
                clear_password=False,
                owner=window,
            ),
        ).pack(pady=2)
        Label(
            window,
            text="Presiona Esc para capturar o\ncierra la ventana de camara para cancelar.",
            wraplength=300,
        ).pack(pady=12)

    def _open_login(self) -> None:
        window = Toplevel(self.root)
        window.title("Login")
        window.geometry("340x420")
        username = StringVar()
        password = StringVar()

        Label(window, text="Login facial: ingresa tu usuario.").pack()
        Label(window, text="Login tradicional: usuario y contrasena.").pack()
        Label(window, text="").pack()
        Label(window, text="Usuario *").pack()
        username_entry = Entry(window, textvariable=username)
        username_entry.pack()
        Label(window, text="Contrasena *").pack()
        password_entry = Entry(window, textvariable=password, show="*")
        password_entry.pack()
        Label(window, text="").pack()

        status = Label(window, text="", wraplength=300, justify="left", fg="black")
        status.pack(pady=6)

        Button(
            window,
            text="Inicio Tradicional",
            width=18,
            command=lambda: self._execute_action(
                action=lambda: self.auth_service.login_password(username.get(), password.get()),
                status_label=status,
                username_entry=username_entry,
                password_entry=password_entry,
                owner=window,
            ),
        ).pack(pady=2)
        Button(
            window,
            text="Inicio Facial",
            width=18,
            command=lambda: self._execute_action(
                action=lambda: self.auth_service.login_face(username.get()),
                status_label=status,
                username_entry=username_entry,
                password_entry=password_entry,
                clear_password=False,
                owner=window,
            ),
        ).pack(pady=2)
        Label(
            window,
            text="Presiona Esc para capturar o\ncierra la ventana de camara para cancelar.",
            wraplength=300,
        ).pack(pady=12)

    def _execute_action(
        self,
        action,
        status_label: Label,
        username_entry: Entry,
        password_entry: Entry,
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
            username_entry.delete(0, END)
            if clear_password:
                password_entry.delete(0, END)
