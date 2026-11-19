"""
Organ donor view — CRUD interface for organ donors with consent tracking.
"""

import customtkinter as ctk
from tkinter import simpledialog
from components.data_table import DataTable
from components.form_fields import (
    create_label_entry, create_blood_group_dropdown,
    create_gender_dropdown, create_organ_type_dropdown,
    create_dropdown, create_text_area,
)
from components.dialogs import confirm_dialog, alert_dialog, error_dialog
from services.organ_service import (
    create_organ_donor, edit_organ_donor, remove_organ_donor, list_organ_donors,
    review_donor,
)
from models.organ_donor_model import get_organ_donor_by_id
from utils.constants import (
    ORGAN_DONOR_TABLE_COLUMNS, BLOOD_GROUPS, ORGAN_TYPES,
    CONSENT_STATUSES, ORGAN_DONOR_STATUSES,
)
from config import COLORS


class OrganDonorView(ctk.CTkFrame):
    """Organ donor management screen."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        # ─── Top bar: Search + Filters + Add ─────────────────────
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.pack(fill="x", pady=(0, 10))

        self.search_entry = ctk.CTkEntry(
            top_bar, placeholder_text="🔍 Search by name...",
            width=200, height=35, font=ctk.CTkFont(size=13),
        )
        self.search_entry.pack(side="left", padx=(0, 8))
        self.search_entry.bind("<KeyRelease>", lambda e: self._refresh_table())

        self.organ_filter = ctk.CTkComboBox(
            top_bar, values=["All"] + ORGAN_TYPES, width=130,
            height=35, font=ctk.CTkFont(size=13), state="readonly",
            command=lambda _: self._refresh_table(),
        )
        self.organ_filter.set("All")
        self.organ_filter.pack(side="left", padx=(0, 8))

        self.bg_filter = ctk.CTkComboBox(
            top_bar, values=["All"] + BLOOD_GROUPS, width=100,
            height=35, font=ctk.CTkFont(size=13), state="readonly",
            command=lambda _: self._refresh_table(),
        )
        self.bg_filter.set("All")
        self.bg_filter.pack(side="left", padx=(0, 8))

        add_btn = ctk.CTkButton(
            top_bar, text="➕ Add Organ Donor", width=160, height=35,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLORS["success"], hover_color="#218838",
            command=self._show_add_form,
        )
        add_btn.pack(side="right")

        # ─── Data Table ──────────────────────────────────────────
        self.table = DataTable(self, columns=ORGAN_DONOR_TABLE_COLUMNS, height=12)
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

        review_btn = ctk.CTkButton(
            btn_frame, text="🔎 Record Review", width=140, height=35,
            fg_color=COLORS["primary"], command=self._review_selected,
        )
        review_btn.pack(side="left", padx=(0, 8))

        # Load data
        self._refresh_table()

    def _refresh_table(self):
        """Reload table data with filters."""
        name = self.search_entry.get()
        organ_type = self.organ_filter.get()
        blood_group = self.bg_filter.get()
        donors = list_organ_donors(name, organ_type, blood_group)

        rows = [
            (d["id"], d["name"], d["age"], d["gender"], d.get("blood_group", ""),
             d["organ_type"], d.get("consent_status", "Pending"),
             d.get("review_status", "Pending"),
             d.get("status", "Available"), d.get("registered_on", "")[:10])
            for d in donors
        ]
        self.table.insert_rows(rows)

    def _show_add_form(self):
        """Show add organ donor popup."""
        self._show_form("Add Organ Donor")

    def _show_edit_form(self):
        """Show edit organ donor popup."""
        selected = self.table.get_selected_row()
        if not selected:
            error_dialog("Error", "Please select an organ donor to edit.")
            return
        donor = get_organ_donor_by_id(selected[0])
        if donor:
            self._show_form("Edit Organ Donor", donor)

    def _show_form(self, title, donor=None):
        """Show add/edit form in a popup window."""
        popup = ctk.CTkToplevel(self)
        popup.title(title)
        popup.geometry("520x620")
        popup.resizable(False, False)
        popup.grab_set()

        form = ctk.CTkFrame(popup, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=20, pady=15)

        name_entry = create_label_entry(form, "Name", 0, default_value=donor["name"] if donor else "")
        age_entry = create_label_entry(form, "Age", 1, default_value=str(donor["age"]) if donor else "")
        gender_dd = create_gender_dropdown(form, 2, default=donor["gender"] if donor else None)
        bg_dd = create_blood_group_dropdown(form, 3, default=donor.get("blood_group") if donor else None)
        organ_dd = create_organ_type_dropdown(form, 4, default=donor["organ_type"] if donor else None)
        phone_entry = create_label_entry(form, "Phone", 5, default_value=donor.get("phone", "") if donor else "")
        email_entry = create_label_entry(form, "Email", 6, default_value=donor.get("email", "") if donor else "")
        address_area = create_text_area(form, "Address", 7, default_value=donor.get("address", "") if donor else "")
        consent_dd = create_dropdown(form, "Consent", 8, values=CONSENT_STATUSES,
                                     default_value=donor.get("consent_status", "Pending") if donor else "Pending")

        # Status dropdown (only for edit)
        status_dd = None
        if donor:
            status_dd = create_dropdown(form, "Status", 9, values=ORGAN_DONOR_STATUSES,
                                        default_value=donor.get("status", "Available"))

        def save():
            name = name_entry.get()
            age = age_entry.get()
            gender = gender_dd.get()
            blood_group = bg_dd.get()
            organ_type = organ_dd.get()
            phone = phone_entry.get()
            email = email_entry.get()
            address = address_area.get("1.0", "end-1c")
            consent = consent_dd.get()
            status = status_dd.get() if status_dd else "Available"

            if donor:
                success, msg = edit_organ_donor(
                    donor["id"], name, age, gender, blood_group, organ_type,
                    phone, email, address, consent, status,
                )
            else:
                success, msg = create_organ_donor(
                    name, age, gender, blood_group, organ_type,
                    phone, email, address, consent,
                )

            if success:
                alert_dialog("Success", msg)
                popup.destroy()
                self._refresh_table()
            else:
                error_dialog("Validation Error", msg)

        save_row = 10 if donor else 9
        save_btn = ctk.CTkButton(
            form, text="💾 Save", width=200, height=40,
            font=ctk.CTkFont(size=14, weight="bold"), command=save,
        )
        save_btn.grid(row=save_row, column=0, columnspan=2, pady=15)

    def _review_selected(self):
        """Record a documented administrative review by an authorized user."""
        selected = self.table.get_selected_row()
        if not selected:
            error_dialog("Selection Required", "Please select an organ donor to review.")
            return
        decision = simpledialog.askstring(
            "Donor Review Decision",
            "Enter decision (Verified, Rejected, Under Review, or Expired):",
            parent=self,
            initialvalue="Verified",
        )
        if not decision:
            return
        notes = simpledialog.askstring(
            "Review Notes",
            "Enter review notes or document reference:",
            parent=self,
        )
        if not notes:
            error_dialog("Review Required", "Review notes are required.")
            return
        success, msg = review_donor(selected[0], decision.strip(), notes)
        if success:
            alert_dialog("Review Recorded", msg)
            self._refresh_table()
        else:
            error_dialog("Review Blocked", msg)

    def _delete_donor(self):
        """Delete selected organ donor."""
        selected = self.table.get_selected_row()
        if not selected:
            error_dialog("Error", "Please select an organ donor to delete.")
            return

        if confirm_dialog("Confirm Delete", f"Delete organ donor '{selected[1]}'?"):
            remove_organ_donor(selected[0])
            alert_dialog("Deleted", "Organ donor deleted successfully.")
            self._refresh_table()
