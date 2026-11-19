"""
Blood donor view — CRUD interface for blood donors.
Add, view, edit, delete blood donors + record donations.
"""

import customtkinter as ctk
from components.data_table import DataTable
from components.form_fields import (
    create_label_entry, create_blood_group_dropdown,
    create_gender_dropdown, create_text_area,
)
from components.dialogs import confirm_dialog, alert_dialog, error_dialog
from services.donor_service import create_donor, edit_donor, remove_donor, list_donors, add_donation
from models.donor_model import get_donor_by_id, get_donation_history
from utils.constants import DONOR_TABLE_COLUMNS, BLOOD_GROUPS
from config import COLORS


class BloodDonorView(ctk.CTkFrame):
    """Blood donor management screen."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        # ─── Top bar: Search + Add button ────────────────────────
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.pack(fill="x", pady=(0, 10))

        self.search_entry = ctk.CTkEntry(
            top_bar, placeholder_text="🔍 Search by name...",
            width=250, height=35, font=ctk.CTkFont(size=13),
        )
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", lambda e: self._refresh_table())

        self.filter_dropdown = ctk.CTkComboBox(
            top_bar, values=["All"] + BLOOD_GROUPS, width=120,
            height=35, font=ctk.CTkFont(size=13), state="readonly",
            command=lambda _: self._refresh_table(),
        )
        self.filter_dropdown.set("All")
        self.filter_dropdown.pack(side="left", padx=(0, 10))

        add_btn = ctk.CTkButton(
            top_bar, text="➕ Add Donor", width=140, height=35,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLORS["success"], hover_color="#218838",
            command=self._show_add_form,
        )
        add_btn.pack(side="right")

        # ─── Data Table ──────────────────────────────────────────
        self.table = DataTable(self, columns=DONOR_TABLE_COLUMNS, height=12)
        self.table.pack(fill="both", expand=True, pady=(0, 10))

        # ─── Action Buttons ──────────────────────────────────────
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x")

        edit_btn = ctk.CTkButton(
            btn_frame, text="✏️ Edit", width=100, height=35,
            fg_color=COLORS["info"], command=self._show_edit_form,
        )
        edit_btn.pack(side="left", padx=(0, 8))

        delete_btn = ctk.CTkButton(
            btn_frame, text="🗑️ Delete", width=100, height=35,
            fg_color=COLORS["danger"], command=self._delete_donor,
        )
        delete_btn.pack(side="left", padx=(0, 8))

        donate_btn = ctk.CTkButton(
            btn_frame, text="💉 Record Donation", width=160, height=35,
            fg_color=COLORS["warning"], text_color="#000000",
            command=self._record_donation,
        )
        donate_btn.pack(side="left", padx=(0, 8))

        # Load data
        self._refresh_table()

    def _refresh_table(self):
        """Reload table data with search/filter."""
        name = self.search_entry.get()
        blood_group = self.filter_dropdown.get()
        donors = list_donors(name, blood_group)

        rows = [
            (d["id"], d["name"], d["age"], d["gender"], d["blood_group"],
             d.get("phone", ""), d.get("email", ""),
             d.get("registered_on", "")[:10])
            for d in donors
        ]
        self.table.insert_rows(rows)

    def _show_add_form(self):
        """Show add donor popup."""
        self._show_form("Add Blood Donor")

    def _show_edit_form(self):
        """Show edit donor popup with pre-filled data."""
        selected = self.table.get_selected_row()
        if not selected:
            error_dialog("Error", "Please select a donor to edit.")
            return
        donor = get_donor_by_id(selected[0])
        if donor:
            self._show_form("Edit Blood Donor", donor)

    def _show_form(self, title, donor=None):
        """Show add/edit form in a popup window."""
        popup = ctk.CTkToplevel(self)
        popup.title(title)
        popup.geometry("500x520")
        popup.resizable(False, False)
        popup.grab_set()

        form = ctk.CTkFrame(popup, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=20, pady=15)

        # Form fields
        name_entry = create_label_entry(form, "Name", 0, default_value=donor["name"] if donor else "")
        age_entry = create_label_entry(form, "Age", 1, default_value=str(donor["age"]) if donor else "")
        gender_dd = create_gender_dropdown(form, 2, default=donor["gender"] if donor else None)
        bg_dd = create_blood_group_dropdown(form, 3, default=donor["blood_group"] if donor else None)
        phone_entry = create_label_entry(form, "Phone", 4, default_value=donor.get("phone", "") if donor else "")
        email_entry = create_label_entry(form, "Email", 5, default_value=donor.get("email", "") if donor else "")
        address_area = create_text_area(form, "Address", 6, default_value=donor.get("address", "") if donor else "")

        def save():
            name = name_entry.get()
            age = age_entry.get()
            gender = gender_dd.get()
            blood_group = bg_dd.get()
            phone = phone_entry.get()
            email = email_entry.get()
            address = address_area.get("1.0", "end-1c")

            if donor:
                success, msg = edit_donor(donor["id"], name, age, gender, blood_group, phone, email, address)
            else:
                success, msg = create_donor(name, age, gender, blood_group, phone, email, address)

            if success:
                alert_dialog("Success", msg)
                popup.destroy()
                self._refresh_table()
            else:
                error_dialog("Validation Error", msg)

        save_btn = ctk.CTkButton(
            form, text="💾 Save", width=200, height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=save,
        )
        save_btn.grid(row=7, column=0, columnspan=2, pady=20)

    def _delete_donor(self):
        """Delete selected donor."""
        selected = self.table.get_selected_row()
        if not selected:
            error_dialog("Error", "Please select a donor to delete.")
            return

        if confirm_dialog("Confirm Delete", f"Delete donor '{selected[1]}'?"):
            remove_donor(selected[0])
            alert_dialog("Deleted", "Blood donor deleted successfully.")
            self._refresh_table()

    def _record_donation(self):
        """Record a donation for the selected donor."""
        selected = self.table.get_selected_row()
        if not selected:
            error_dialog("Error", "Please select a donor to record a donation.")
            return

        donor = get_donor_by_id(selected[0])
        if not donor:
            return

        if confirm_dialog("Record Donation",
                          f"Record 1 unit donation from '{donor['name']}' "
                          f"(Blood Group: {donor['blood_group']})?"):
            add_donation(donor["id"], donor["blood_group"], units=1, notes="Routine donation")
            alert_dialog("Success", "Donation recorded and inventory updated!")
            self._refresh_table()
