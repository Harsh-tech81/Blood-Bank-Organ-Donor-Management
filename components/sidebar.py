"""
Sidebar navigation component.
Renders a vertical menu with clickable items and active-state highlighting.
"""

import customtkinter as ctk
from config import SIDEBAR_WIDTH, COLORS
from utils.constants import SIDEBAR_MENU


class Sidebar(ctk.CTkFrame):
    """Left navigation sidebar with menu items."""

    def __init__(self, master, on_navigate, active_key="dashboard", **kwargs):
        super().__init__(master, width=SIDEBAR_WIDTH, corner_radius=0, **kwargs)
        self.configure(fg_color=COLORS["sidebar_bg"])
        self.pack_propagate(False)

        self.on_navigate = on_navigate
        self.active_key = active_key
        self.menu_buttons = {}

        self._build_header()
        self._build_menu()
        self._build_footer()

    def _build_header(self):
        """App title/logo in the sidebar header."""
        header = ctk.CTkFrame(self, fg_color="transparent", height=80)
        header.pack(fill="x", padx=10, pady=(15, 5))
        header.pack_propagate(False)

        title = ctk.CTkLabel(
            header,
            text="🏥 BloodBank",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#ffffff",
        )
        title.pack(pady=(10, 0))

        subtitle = ctk.CTkLabel(
            header,
            text="Management System",
            font=ctk.CTkFont(size=11),
            text_color="#aaaaaa",
        )
        subtitle.pack()

    def _build_menu(self):
        """Build clickable menu items."""
        menu_frame = ctk.CTkFrame(self, fg_color="transparent")
        menu_frame.pack(fill="both", expand=True, padx=10, pady=10)

        for item in SIDEBAR_MENU:
            key = item["key"]
            label = item["label"]

            is_active = key == self.active_key
            fg = COLORS["sidebar_active"] if is_active else "transparent"
            hover = COLORS["sidebar_hover"]

            btn = ctk.CTkButton(
                menu_frame,
                text=label,
                font=ctk.CTkFont(size=14),
                fg_color=fg,
                hover_color=hover,
                text_color="#ffffff",
                anchor="w",
                height=40,
                corner_radius=8,
                command=lambda k=key: self._on_click(k),
            )
            btn.pack(fill="x", pady=2)
            self.menu_buttons[key] = btn

    def _build_footer(self):
        """Logout button at the bottom."""
        footer = ctk.CTkFrame(self, fg_color="transparent", height=60)
        footer.pack(fill="x", padx=10, pady=(0, 15))
        footer.pack_propagate(False)

        logout_btn = ctk.CTkButton(
            footer,
            text="🚪  Logout",
            font=ctk.CTkFont(size=14),
            fg_color=COLORS["danger"],
            hover_color="#c82333",
            text_color="#ffffff",
            height=38,
            corner_radius=8,
            command=lambda: self.on_navigate("logout"),
        )
        logout_btn.pack(fill="x", pady=(10, 0))

    def _on_click(self, key: str):
        """Handle menu item click — update active state and navigate."""
        for k, btn in self.menu_buttons.items():
            if k == key:
                btn.configure(fg_color=COLORS["sidebar_active"])
            else:
                btn.configure(fg_color="transparent")
        self.active_key = key
        self.on_navigate(key)

    def set_active(self, key: str):
        """Programmatically set the active menu item."""
        self._on_click(key)
