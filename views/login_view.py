"""
Login screen view.
Displays username/password fields and handles authentication.
"""

import customtkinter as ctk
from services.auth_service import login
from config import COLORS


class LoginView(ctk.CTkFrame):
    """Login screen with username and password fields."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.app = master
        self.configure(fg_color="#1a1a2e")
        self._build_ui()

    def _build_ui(self):
        """Build the login form UI."""
        # Center container
        center_frame = ctk.CTkFrame(
            self, fg_color="#16213e", corner_radius=20, width=420, height=520
        )
        center_frame.place(relx=0.5, rely=0.5, anchor="center")
        center_frame.pack_propagate(False)

        # Icon / Title
        icon_label = ctk.CTkLabel(center_frame, text="🏥", font=ctk.CTkFont(size=50))
        icon_label.pack(pady=(40, 5))

        title = ctk.CTkLabel(
            center_frame,
            text="Blood Bank & Organ Donors",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#ffffff",
        )
        title.pack(pady=(0, 2))

        subtitle = ctk.CTkLabel(
            center_frame,
            text="Management System",
            font=ctk.CTkFont(size=14),
            text_color="#aaaaaa",
        )
        subtitle.pack(pady=(0, 25))

        # Username
        username_label = ctk.CTkLabel(
            center_frame, text="Username", font=ctk.CTkFont(size=13), anchor="w"
        )
        username_label.pack(padx=40, anchor="w")

        self.username_entry = ctk.CTkEntry(
            center_frame, width=340, height=42,
            font=ctk.CTkFont(size=14), placeholder_text="Enter username",
        )
        self.username_entry.pack(padx=40, pady=(5, 15))

        # Password
        password_label = ctk.CTkLabel(
            center_frame, text="Password", font=ctk.CTkFont(size=13), anchor="w"
        )
        password_label.pack(padx=40, anchor="w")

        self.password_entry = ctk.CTkEntry(
            center_frame, width=340, height=42,
            font=ctk.CTkFont(size=14), placeholder_text="Enter password", show="•",
        )
        self.password_entry.pack(padx=40, pady=(5, 10))

        # Error message label (hidden by default)
        self.error_label = ctk.CTkLabel(
            center_frame, text="", font=ctk.CTkFont(size=12),
            text_color=COLORS["danger"],
        )
        self.error_label.pack(pady=(0, 5))

        # Login button
        login_btn = ctk.CTkButton(
            center_frame, text="🔐  Login", width=340, height=42,
            font=ctk.CTkFont(size=15, weight="bold"), corner_radius=10,
            command=self._handle_login,
        )
        login_btn.pack(padx=40, pady=(5, 10))

        # Default credentials hint
        hint = ctk.CTkLabel(
            center_frame, text="Default: admin / admin123",
            font=ctk.CTkFont(size=11), text_color="#666666",
        )
        hint.pack(pady=(5, 20))

        # Bind Enter key
        self.password_entry.bind("<Return>", lambda e: self._handle_login())
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus())

        # Auto-focus username
        self.username_entry.focus()

    def _handle_login(self):
        """Process login attempt."""
        username = self.username_entry.get()
        password = self.password_entry.get()

        success, message = login(username, password)

        if success:
            self.error_label.configure(text="", text_color=COLORS["success"])
            self.app.show_main_app(username)
        else:
            self.error_label.configure(text=message, text_color=COLORS["danger"])
            self.password_entry.delete(0, "end")
            self.password_entry.focus()
