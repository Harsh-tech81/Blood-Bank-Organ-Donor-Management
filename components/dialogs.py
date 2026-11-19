"""
Reusable dialog helpers.
Confirm, alert, and input dialogs for the application.
"""

from tkinter import messagebox


def confirm_dialog(title, message):
    """Show a Yes/No confirmation dialog. Returns True if confirmed."""
    return messagebox.askyesno(title, message)


def alert_dialog(title, message):
    """Show an informational alert dialog."""
    messagebox.showinfo(title, message)


def error_dialog(title, message):
    """Show an error alert dialog."""
    messagebox.showerror(title, message)


def warning_dialog(title, message):
    """Show a warning alert dialog."""
    messagebox.showwarning(title, message)
