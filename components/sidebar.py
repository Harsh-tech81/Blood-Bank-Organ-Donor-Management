"""
Sidebar navigation component with sleek dark modern look,
subtle active indicators, user profile pill, and smooth interactions.
"""

import customtkinter as ctk
from config import SIDEBAR_WIDTH, COLORS
from utils.constants import SIDEBAR_MENU


class Sidebar(ctk.CTkFrame):
    """Left navigation sidebar with modern UI and active-state styling."""

    def __init__(self, master, on_navigate, active_key="dashboard", username="Admin", **kwargs):
        super().__init__(
            master,
            width=SIDEBAR_WIDTH,
            corner_radius=0,
            fg_color=COLORS["sidebar_bg"],
            border_width=1,
            border_color=COLORS["surface_border"],
            **kwargs,
        )
        self.pack_propagate(False)

        self.on_navigate = on_navigate
        self.active_key = active_key
        self.username = username
        self.menu_buttons = {}

        self._build_header()
        self._build_menu()
        self._build_footer()

    def _build_header(self):
        """Header with brand icon and subtitle."""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(20, 16))

        logo_row = ctk.CTkFrame(header, fg_color="transparent")
        logo_row.pack(fill="x")

        logo_badge = ctk.CTkFrame(
            logo_row, width=34, height=34, corner_radius=10, fg_color=COLORS["accent_red"]
        )
        logo_badge.pack(side="left")
        logo_badge.pack_propagate(False)

        badge_ico = ctk.CTkLabel(logo_badge, text="🩸", font=ctk.CTkFont(size=18))
        badge_ico.place(relx=0.5, rely=0.5, anchor="center")

        brand_text_box = ctk.CTkFrame(logo_row, fg_color="transparent")
        brand_text_box.pack(side="left", padx=(10, 0))

        title = ctk.CTkLabel(
            brand_text_box,
            text="LifeLink",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=COLORS["text_primary"],
        )
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            brand_text_box,
            text="CLINICAL PORTAL",
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color=COLORS["text_muted"],
        )
        subtitle.pack(anchor="w")

        # Subtle divider
        divider = ctk.CTkFrame(self, height=1, fg_color=COLORS["surface_border"])
        divider.pack(fill="x", padx=16, pady=(0, 12))

    def _build_menu(self):
        """Build menu items with clean hovering."""
        menu_frame = ctk.CTkFrame(self, fg_color="transparent")
        menu_frame.pack(fill="both", expand=True, padx=12, pady=4)

        nav_header = ctk.CTkLabel(
            menu_frame,
            text="NAVIGATION",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=COLORS["text_muted"],
            anchor="w",
        )
        nav_header.pack(fill="x", padx=10, pady=(0, 6))

        for item in SIDEBAR_MENU:
            key = item["key"]
            label = item["label"]

            is_active = key == self.active_key
            fg = COLORS["sidebar_active"] if is_active else "transparent"
            text_color = "#ffffff" if is_active else COLORS["text_secondary"]

            btn = ctk.CTkButton(
                menu_frame,
                text=label,
                font=ctk.CTkFont(size=13, weight="bold" if is_active else "normal"),
                fg_color=fg,
                hover_color=COLORS["sidebar_hover"],
                text_color=text_color,
                anchor="w",
                height=40,
                corner_radius=10,
                command=lambda k=key: self._on_click(k),
            )
            btn.pack(fill="x", pady=2)
            self.menu_buttons[key] = btn

    def _build_footer(self):
        """User profile chip + logout button."""
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", padx=14, pady=(0, 18))

        # User Profile Pill
        user_chip = ctk.CTkFrame(
            footer,
            fg_color=COLORS["surface"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["surface_border"],
            height=46,
        )
        user_chip.pack(fill="x", pady=(0, 8))
        user_chip.pack_propagate(False)

        avatar = ctk.CTkFrame(user_chip, width=28, height=28, corner_radius=14, fg_color="#3b82f6")
        avatar.pack(side="left", padx=10)
        avatar.pack_propagate(False)
        av_lbl = ctk.CTkLabel(avatar, text=self.username[:1].upper(), font=ctk.CTkFont(size=12, weight="bold"))
        av_lbl.place(relx=0.5, rely=0.5, anchor="center")

        uname_box = ctk.CTkFrame(user_chip, fg_color="transparent")
        uname_box.pack(side="left", fill="both", expand=True)

        uname_lbl = ctk.CTkLabel(
            uname_box,
            text=self.username,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["text_primary"],
            anchor="w",
        )
        uname_lbl.pack(fill="x", pady=(5, 0))

        status_lbl = ctk.CTkLabel(
            uname_box,
            text="Online Session",
            font=ctk.CTkFont(size=9),
            text_color=COLORS["success"],
            anchor="w",
        )
        status_lbl.pack(fill="x")

        # Logout Button
        logout_btn = ctk.CTkButton(
            footer,
            text="🚪  Sign Out",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="transparent",
            hover_color="#450a0a",
            text_color="#fca5a5",
            border_width=1,
            border_color="#7f1d1d",
            height=36,
            corner_radius=10,
            command=lambda: self.on_navigate("logout"),
        )
        logout_btn.pack(fill="x")

    def _on_click(self, key: str):
        """Update active button state with modern colors."""
        for k, btn in self.menu_buttons.items():
            if k == key:
                btn.configure(
                    fg_color=COLORS["sidebar_active"],
                    text_color="#ffffff",
                    font=ctk.CTkFont(size=13, weight="bold"),
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=COLORS["text_secondary"],
                    font=ctk.CTkFont(size=13, weight="normal"),
                )
        self.active_key = key
        self.on_navigate(key)

    def set_active(self, key: str):
        self._on_click(key)
