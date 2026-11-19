"""
Dashboard stat card component with modern glassmorphism aesthetic,
subtle border accents, and dynamic animated counter effect.
"""

import customtkinter as ctk
from config import COLORS


class StatCard(ctk.CTkFrame):
    """A sleek card widget showing an icon, animated value, and subtitle."""

    def __init__(
        self,
        master,
        title: str,
        value: str | int,
        icon: str = "📊",
        accent_color: str = "#2563eb",
        badge_text: str = "Active",
        **kwargs,
    ):
        super().__init__(
            master,
            corner_radius=16,
            fg_color=COLORS["surface"],
            border_width=1,
            border_color=COLORS["surface_border"],
            **kwargs,
        )
        self.accent_color = accent_color
        self.final_value = value
        self.target_number = 0
        self.is_numeric = False

        try:
            self.target_number = int(value)
            self.is_numeric = True
        except (ValueError, TypeError):
            self.is_numeric = False

        self._build_card(title, icon, badge_text)
        if self.is_numeric and self.target_number > 0:
            self._animate_counter(0, self.target_number)
        else:
            self.value_label.configure(text=str(value))

    def _build_card(self, title: str, icon: str, badge_text: str):
        # Top bar inside card: Icon badge + Status pill
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.pack(fill="x", padx=16, pady=(16, 8))

        # Icon with soft background circular badge
        icon_badge = ctk.CTkFrame(
            top_bar,
            width=42,
            height=42,
            corner_radius=12,
            fg_color=self.accent_color,
        )
        icon_badge.pack(side="left")
        icon_badge.pack_propagate(False)

        icon_lbl = ctk.CTkLabel(
            icon_badge,
            text=icon,
            font=ctk.CTkFont(size=20),
        )
        icon_lbl.place(relx=0.5, rely=0.5, anchor="center")

        # Status badge pill
        pill = ctk.CTkFrame(top_bar, fg_color="#1e293b", corner_radius=10)
        pill.pack(side="right")
        pill_lbl = ctk.CTkLabel(
            pill,
            text=f"● {badge_text}",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#94a3b8",
        )
        pill_lbl.pack(padx=8, pady=2)

        # Main numeric metric
        self.value_label = ctk.CTkLabel(
            self,
            text="0",
            font=ctk.CTkFont(family="Segoe UI", size=32, weight="bold"),
            text_color=COLORS["text_primary"],
            anchor="w",
        )
        self.value_label.pack(fill="x", padx=18, pady=(4, 0))

        # Metric descriptive title
        title_label = ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["text_muted"],
            anchor="w",
        )
        title_label.pack(fill="x", padx=18, pady=(0, 16))

    def _animate_counter(self, current: int, target: int, step: int = 1):
        """Smoothly increment the number for an appealing animation."""
        if current <= target:
            self.value_label.configure(text=str(current))
            increment = max(1, (target - current) // 6)
            self.after(25, lambda: self._animate_counter(current + increment, target, step))
        else:
            self.value_label.configure(text=str(target))

    def update_value(self, value: str | int):
        """Update and optionally animate the value."""
        try:
            new_target = int(value)
            self.target_number = new_target
            self._animate_counter(0, new_target)
        except (ValueError, TypeError):
            self.value_label.configure(text=str(value))
