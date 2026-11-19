"""
Dashboard stat card component.
Displays a metric with an icon, value, and label.
"""

import customtkinter as ctk
from config import COLORS


class StatCard(ctk.CTkFrame):
    """A card widget showing a statistic (icon + number + label)."""

    def __init__(self, master, title, value, icon="📊", color=None, **kwargs):
        super().__init__(master, corner_radius=12, **kwargs)
        self.configure(
            fg_color=color or COLORS["card_bg"],
            border_width=1,
            border_color="#3a3a3a",
        )

        icon_label = ctk.CTkLabel(self, text=icon, font=ctk.CTkFont(size=30))
        icon_label.pack(pady=(15, 5))

        self.value_label = ctk.CTkLabel(
            self, text=str(value),
            font=ctk.CTkFont(size=28, weight="bold"), text_color="#ffffff",
        )
        self.value_label.pack(pady=(0, 2))

        title_label = ctk.CTkLabel(
            self, text=title,
            font=ctk.CTkFont(size=12), text_color="#aaaaaa",
        )
        title_label.pack(pady=(0, 15))

    def update_value(self, value):
        """Update the displayed value."""
        self.value_label.configure(text=str(value))
