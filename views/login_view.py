"""
Login and Registration screen view.
Provides modern glassmorphism styling, role-based tabs,
animated error shake, and fast user switching.
"""

import customtkinter as ctk
from services.auth_service import login, register_user
from config import COLORS


class LoginView(ctk.CTkFrame):
    """Modern authentication screen with Login and Register modes."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.app = master
        self.configure(fg_color=COLORS["bg_main"])
        self.current_mode = "login"

        self._build_ui()

    def _build_ui(self):
        """Construct the modern centered card UI."""
        # Main Elevated Card with subtle border
        self.card = ctk.CTkFrame(
            self,
            fg_color=COLORS["surface"],
            corner_radius=22,
            border_width=1,
            border_color=COLORS["surface_border"],
            width=460,
            height=630,
        )
        self.card.place(relx=0.5, rely=0.5, anchor="center")
        self.card.pack_propagate(False)

        # Header Section: Badge + Title
        badge_frame = ctk.CTkFrame(self.card, fg_color="#1e1b4b", corner_radius=20)
        badge_frame.pack(pady=(35, 10))

        badge_label = ctk.CTkLabel(
            badge_frame,
            text=" 🩸 LIFE LINK HEALTHCARE ",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#818cf8",
        )
        badge_label.pack(padx=14, pady=4)

        title = ctk.CTkLabel(
            self.card,
            text="Blood & Organ Donor Portal",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=COLORS["text_primary"],
        )
        title.pack(pady=(0, 3))

        subtitle = ctk.CTkLabel(
            self.card,
            text="Secure enterprise clinical management system",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_muted"],
        )
        subtitle.pack(pady=(0, 20))

        # Mode Selector: Login vs Register
        self.mode_selector = ctk.CTkSegmentedButton(
            self.card,
            values=["Sign In", "Create Staff Account"],
            font=ctk.CTkFont(size=13, weight="bold"),
            selected_color=COLORS["primary"],
            selected_hover_color=COLORS["primary_hover"],
            unselected_color=COLORS["secondary"],
            unselected_hover_color=COLORS["surface_hover"],
            command=self._on_mode_change,
            height=36,
            corner_radius=10,
        )
        self.mode_selector.set("Sign In")
        self.mode_selector.pack(fill="x", padx=45, pady=(0, 15))

        # Input Container
        self.inputs_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        self.inputs_frame.pack(fill="x", padx=45)

        # Username Field
        u_label = ctk.CTkLabel(
            self.inputs_frame,
            text="Account Username",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["text_secondary"],
            anchor="w",
        )
        u_label.pack(fill="x", pady=(0, 4))

        self.username_entry = ctk.CTkEntry(
            self.inputs_frame,
            height=42,
            font=ctk.CTkFont(size=14),
            placeholder_text="e.g. admin or staff",
            fg_color=COLORS["dark"],
            border_color=COLORS["surface_border"],
            border_width=1,
            corner_radius=10,
        )
        self.username_entry.pack(fill="x", pady=(0, 14))

        # Password Field
        p_label = ctk.CTkLabel(
            self.inputs_frame,
            text="Password",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["text_secondary"],
            anchor="w",
        )
        p_label.pack(fill="x", pady=(0, 4))

        self.password_entry = ctk.CTkEntry(
            self.inputs_frame,
            height=42,
            font=ctk.CTkFont(size=14),
            placeholder_text="Enter credentials",
            show="•",
            fg_color=COLORS["dark"],
            border_color=COLORS["surface_border"],
            border_width=1,
            corner_radius=10,
        )
        self.password_entry.pack(fill="x", pady=(0, 8))

        # Role Selector (only shown in registration mode)
        self.role_frame = ctk.CTkFrame(self.inputs_frame, fg_color="transparent")
        r_label = ctk.CTkLabel(
            self.role_frame,
            text="Assigned Role",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["text_secondary"],
            anchor="w",
        )
        r_label.pack(fill="x", pady=(0, 4))

        self.role_combo = ctk.CTkComboBox(
            self.role_frame,
            values=["Staff Member", "Medical Officer", "Administrator"],
            height=38,
            font=ctk.CTkFont(size=13),
            state="readonly",
            fg_color=COLORS["dark"],
            border_color=COLORS["surface_border"],
            corner_radius=10,
        )
        self.role_combo.set("Staff Member")
        self.role_combo.pack(fill="x", pady=(0, 8))

        # Notification / Error Banner
        self.msg_label = ctk.CTkLabel(
            self.card,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["danger"],
            wraplength=360,
        )
        self.msg_label.pack(pady=(4, 8))

        # Primary Action Button
        self.action_btn = ctk.CTkButton(
            self.card,
            text="Sign In to Portal",
            height=44,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            corner_radius=12,
            command=self._handle_action,
        )
        self.action_btn.pack(fill="x", padx=45, pady=(0, 15))

        # Quick Preset Selector (Demo Friendly)
        self.quick_bar = ctk.CTkFrame(self.card, fg_color="transparent")
        self.quick_bar.pack(fill="x", padx=45)

        quick_label = ctk.CTkLabel(
            self.quick_bar,
            text="⚡ Demo Quick Fill:",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_muted"],
        )
        quick_label.pack(side="left", padx=(0, 8))

        admin_pill = ctk.CTkButton(
            self.quick_bar,
            text="Admin",
            width=65,
            height=26,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#1e293b",
            hover_color="#334155",
            corner_radius=15,
            command=lambda: self._quick_fill("admin", "admin123"),
        )
        admin_pill.pack(side="left", padx=3)

        staff_pill = ctk.CTkButton(
            self.quick_bar,
            text="Staff",
            width=65,
            height=26,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#1e293b",
            hover_color="#334155",
            corner_radius=15,
            command=lambda: self._quick_fill("staff", "staff123"),
        )
        staff_pill.pack(side="left", padx=3)

        # Keyboard bindings
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus())
        self.password_entry.bind("<Return>", lambda e: self._handle_action())
        self.username_entry.focus()

    def _on_mode_change(self, value):
        """Toggle between Sign In and Registration modes."""
        self.msg_label.configure(text="")
        if value == "Sign In":
            self.current_mode = "login"
            self.role_frame.pack_forget()
            self.action_btn.configure(text="Sign In to Portal", fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"])
            self.quick_bar.pack(fill="x", padx=45)
        else:
            self.current_mode = "register"
            self.role_frame.pack(fill="x", pady=(0, 6))
            self.action_btn.configure(text="Register New Account", fg_color=COLORS["accent_emerald"], hover_color=COLORS["accent_emerald_hover"])
            self.quick_bar.pack_forget()

    def _quick_fill(self, username, password):
        """Quickly populate demo credentials."""
        self.username_entry.delete(0, "end")
        self.username_entry.insert(0, username)
        self.password_entry.delete(0, "end")
        self.password_entry.insert(0, password)
        self.msg_label.configure(text=f"Selected {username} demo account", text_color=COLORS["info"])

    def _animate_shake(self):
        """Play a smooth horizontal shake animation on invalid inputs."""
        shifts = [-12, 12, -8, 8, -4, 4, 0]
        base_x = 0.5

        def step(i):
            if i < len(shifts):
                offset = shifts[i] / 1200.0
                self.card.place_configure(relx=base_x + offset)
                self.after(25, lambda: step(i + 1))
            else:
                self.card.place_configure(relx=base_x)

        step(0)

    def _handle_action(self):
        """Submit the login or register request."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if self.current_mode == "login":
            success, message = login(username, password)
            if success:
                self.msg_label.configure(text=message, text_color=COLORS["success"])
                self.after(150, lambda: self.app.show_main_app(username))
            else:
                self.msg_label.configure(text=message, text_color=COLORS["danger"])
                self._animate_shake()
                self.password_entry.delete(0, "end")
                self.password_entry.focus()
        else:
            role = self.role_combo.get()
            success, message = register_user(username, password, role)
            if success:
                self.msg_label.configure(text=message + " You can now sign in.", text_color=COLORS["success"])
                self.mode_selector.set("Sign In")
                self._on_mode_change("Sign In")
                self.password_entry.delete(0, "end")
            else:
                self.msg_label.configure(text=message, text_color=COLORS["danger"])
                self._animate_shake()
