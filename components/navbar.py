"""
Top navigation bar component with breadcrumbs, role badge,
live digital clock, and clean glass layout.
"""

from datetime import datetime
import customtkinter as ctk
from config import COLORS


class Navbar(ctk.CTkFrame):
    """Top navigation bar with title, live clock, and user badge."""

    def __init__(self, master, title="Dashboard", username="Admin", **kwargs):
        super().__init__(
            master,
            height=64,
            corner_radius=0,
            fg_color=COLORS["surface"],
            border_width=1,
            border_color=COLORS["surface_border"],
            **kwargs,
        )
        self.pack_propagate(False)

        # Left Section: Icon badge + Title
        left_box = ctk.CTkFrame(self, fg_color="transparent")
        left_box.pack(side="left", padx=24, pady=12)

        self.title_label = ctk.CTkLabel(
            left_box,
            text=title,
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=COLORS["text_primary"],
        )
        self.title_label.pack(side="left")

        # Right Section: Clock + User Role Pill
        right_box = ctk.CTkFrame(self, fg_color="transparent")
        right_box.pack(side="right", padx=24)

        # Live Clock
        self.clock_label = ctk.CTkLabel(
            right_box,
            text="",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["text_muted"],
        )
        self.clock_label.pack(side="left", padx=(0, 16))
        self._update_clock()

        # User Role Badge
        role_pill = ctk.CTkFrame(right_box, fg_color="#1e1b4b", corner_radius=14)
        role_pill.pack(side="right")

        user_label = ctk.CTkLabel(
            role_pill,
            text=f"👨‍⚕️ {username.title()}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#a5b4fc",
        )
        user_label.pack(padx=12, pady=5)

    def _update_clock(self):
        """Update the live system clock display."""
        now = datetime.now().strftime("%a, %d %b %Y  •  %H:%M:%S")
        self.clock_label.configure(text=now)
        self.after(1000, self._update_clock)

    def set_title(self, title: str):
        """Update the page title."""
        self.title_label.configure(text=title)
