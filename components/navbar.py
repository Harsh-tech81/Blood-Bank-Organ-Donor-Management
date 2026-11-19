"""
Top navigation bar component.
Shows the current page title and user info.
"""

import customtkinter as ctk
from config import COLORS


class Navbar(ctk.CTkFrame):
    """Top navigation bar with title and user info."""

    def __init__(self, master, title="Dashboard", username="Admin", **kwargs):
        super().__init__(master, height=60, corner_radius=0, **kwargs)
        self.configure(fg_color=COLORS["secondary"])
        self.pack_propagate(False)

        # Page title (left)
        self.title_label = ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#ffffff",
        )
        self.title_label.pack(side="left", padx=20)

        # User info (right)
        user_frame = ctk.CTkFrame(self, fg_color="transparent")
        user_frame.pack(side="right", padx=20)

        user_label = ctk.CTkLabel(
            user_frame,
            text=f"👤 {username}",
            font=ctk.CTkFont(size=13),
            text_color="#cccccc",
        )
        user_label.pack(side="right")

    def set_title(self, title: str):
        """Update the page title."""
        self.title_label.configure(text=title)
