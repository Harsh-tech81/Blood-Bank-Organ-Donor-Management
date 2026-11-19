"""
Reusable form field helper components.
Provides consistent labeled input fields for all forms.
"""

import customtkinter as ctk
from utils.constants import BLOOD_GROUPS, GENDERS, ORGAN_TYPES, URGENCY_LEVELS


def create_label_entry(
    parent, label_text, row, column=0, default_value="",
    width=250, show=None, state="normal",
):
    """Create a labeled text entry field. Returns the CTkEntry widget."""
    label = ctk.CTkLabel(parent, text=label_text, font=ctk.CTkFont(size=13), anchor="w")
    label.grid(row=row, column=column, padx=(10, 5), pady=8, sticky="w")

    entry = ctk.CTkEntry(parent, width=width, height=35, font=ctk.CTkFont(size=13), state=state)
    if show:
        entry.configure(show=show)
    if default_value:
        entry.insert(0, default_value)
    entry.grid(row=row, column=column + 1, padx=(5, 10), pady=8, sticky="w")

    return entry


def create_dropdown(
    parent, label_text, row, column=0, values=None,
    default_value=None, width=250, command=None,
):
    """Create a labeled dropdown field. Returns the CTkComboBox widget."""
    label = ctk.CTkLabel(parent, text=label_text, font=ctk.CTkFont(size=13), anchor="w")
    label.grid(row=row, column=column, padx=(10, 5), pady=8, sticky="w")

    dropdown = ctk.CTkComboBox(
        parent, values=values or [], width=width, height=35,
        font=ctk.CTkFont(size=13), state="readonly", command=command,
    )
    if default_value and default_value in (values or []):
        dropdown.set(default_value)
    elif values:
        dropdown.set(values[0])
    dropdown.grid(row=row, column=column + 1, padx=(5, 10), pady=8, sticky="w")

    return dropdown


def create_text_area(
    parent, label_text, row, column=0, default_value="", width=250, height=80,
):
    """Create a labeled text area. Returns the CTkTextbox widget."""
    label = ctk.CTkLabel(parent, text=label_text, font=ctk.CTkFont(size=13), anchor="w")
    label.grid(row=row, column=column, padx=(10, 5), pady=8, sticky="nw")

    textbox = ctk.CTkTextbox(parent, width=width, height=height, font=ctk.CTkFont(size=13))
    if default_value:
        textbox.insert("1.0", default_value)
    textbox.grid(row=row, column=column + 1, padx=(5, 10), pady=8, sticky="w")

    return textbox


def create_blood_group_dropdown(parent, row, column=0, default=None, **kwargs):
    """Shortcut for blood group dropdown."""
    return create_dropdown(parent, "Blood Group", row, column, BLOOD_GROUPS, default, **kwargs)


def create_gender_dropdown(parent, row, column=0, default=None, **kwargs):
    """Shortcut for gender dropdown."""
    return create_dropdown(parent, "Gender", row, column, GENDERS, default, **kwargs)


def create_organ_type_dropdown(parent, row, column=0, default=None, **kwargs):
    """Shortcut for organ type dropdown."""
    return create_dropdown(parent, "Organ Type", row, column, ORGAN_TYPES, default, **kwargs)


def create_urgency_dropdown(parent, row, column=0, default=None, **kwargs):
    """Shortcut for urgency level dropdown."""
    return create_dropdown(parent, "Urgency", row, column, URGENCY_LEVELS, default, **kwargs)
