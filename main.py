"""
Blood Bank & Organ Donors Management System
Main entry point — launches the desktop application.
"""

import customtkinter as ctk
from config import (
    APP_NAME, WINDOW_WIDTH, WINDOW_HEIGHT,
    MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT,
    APPEARANCE_MODE, COLOR_THEME,
)
from database import initialize_db


class App(ctk.CTk):
    """Main application window."""

    def __init__(self):
        super().__init__()

        # ─── Window Configuration ────────────────────────────────
        self.title(APP_NAME)
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)

        # Center window on screen
        self.update_idletasks()
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = (screen_w - WINDOW_WIDTH) // 2
        y = (screen_h - WINDOW_HEIGHT) // 2
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")

        # ─── Theme ───────────────────────────────────────────────
        ctk.set_appearance_mode(APPEARANCE_MODE)
        ctk.set_default_color_theme(COLOR_THEME)

        # ─── Initialize Database ─────────────────────────────────
        initialize_db()

        # ─── State ───────────────────────────────────────────────
        self.current_user = None
        self.current_frame = None

        # ─── Show Login Screen ───────────────────────────────────
        self._show_login()

    # ─── Navigation Methods ──────────────────────────────────────

    def _show_login(self):
        """Display the login screen."""
        from views.login_view import LoginView
        self._switch_frame(LoginView)

    def show_main_app(self, username: str):
        """Switch from login to the main application layout."""
        self.current_user = username
        from views.dashboard_view import DashboardView
        self._switch_frame(DashboardView)

    def show_view(self, view_class, **kwargs):
        """Switch the content area to a different view."""
        self._switch_frame(view_class, **kwargs)

    def logout(self):
        """Log out and return to the login screen."""
        self.current_user = None
        self._show_login()

    def _switch_frame(self, frame_class, **kwargs):
        """Destroy the current frame and show a new one."""
        if self.current_frame is not None:
            self.current_frame.destroy()
        self.current_frame = frame_class(self, **kwargs)
        self.current_frame.pack(fill="both", expand=True)


def main():
    """Application entry point."""
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
