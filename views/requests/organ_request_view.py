"""
Organ request view — manage organ requests with status tracking.
"""

import customtkinter as ctk
from components.data_table import DataTable
from components.form_fields import (
    create_label_entry, create_blood_group_dropdown,
    create_organ_type_dropdown, create_urgency_dropdown,
)
from components.dialogs import confirm_dialog, alert_dialog, error_dialog
from services.organ_request_service import (
    create_organ_request, change_organ_request_status,
    remove_organ_request, list_organ_requests,
)
from utils.constants import ORGAN_REQUEST_TABLE_COLUMNS, ORGAN_TYPES, ORGAN_REQUEST_STATUSES
from config import COLORS


class OrganRequestView(ctk.CTkFrame):
    """Organ request management screen."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        # ─── Top bar ─────────────────────────────────────────────
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.pack(fill="x", pady=(0, 10))

        self.search_entry = ctk.CTkEntry(
            top_bar, placeholder_text="🔍 Search patient...",
            width=200, height=35, font=ctk.CTkFont(size=13),
        )
        self.search_entry.pack(side="left", padx=(0, 8))
        self.search_entry.bind("<KeyRelease>", lambda e: self._refresh_table())

        self.organ_filter = ctk.CTkComboBox(
            top_bar, values=["All"] + ORGAN_TYPES, width=130,
            height=35, state="readonly", command=lambda _: self._refresh_table(),
        )
        self.organ_filter.set("All")
        self.organ_filter.pack(side="left", padx=(0, 8))

        self.status_filter = ctk.CTkComboBox(
            top_bar, values=["All"] + ORGAN_REQUEST_STATUSES, width=120,
            height=35, state="readonly", command=lambda _: self._refresh_table(),
        )
        self.status_filter.set("All")
        self.status_filter.pack(side="left", padx=(0, 8))

        add_btn = ctk.CTkButton(
            top_bar, text="➕ New Request", width=140, height=35,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLORS["success"], hover_color="#218838",
            command=self._show_add_form,
        )
        add_btn.pack(side="right")

        # ─── Data Table ──────────────────────────────────────────
        self.table = DataTable(self, columns=ORGAN_REQUEST_TABLE_COLUMNS, height=12)
        self.table.pack(fill="both", expand=True, pady=(0, 10))

        # ─── Action Buttons ──────────────────────────────────────
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x")

        match_btn = ctk.CTkButton(
            btn_frame, text="🔗 Match", width=100, height=35,
            fg_color=COLORS["success"],
            command=lambda: self._update_status("Matched"),
        )
        match_btn.pack(side="left", padx=(0, 8))

        fulfill_btn = ctk.CTkButton(
            btn_frame, text="✅ Fulfill", width=100, height=35,
            fg_color=COLORS["info"],
            command=lambda: self._update_status("Fulfilled"),
        )
        fulfill_btn.pack(side="left", padx=(0, 8))

        reject_btn = ctk.CTkButton(
            btn_frame, text="❌ Reject", width=100, height=35,
            fg_color=COLORS["danger"],
            command=lambda: self._update_status("Rejected"),
        )
        reject_btn.pack(side="left", padx=(0, 8))

        delete_btn = ctk.CTkButton(
            btn_frame, text="🗑️ Delete", width=100, height=35,
            fg_color="#555555",
            command=self._delete_request,
        )
        delete_btn.pack(side="left", padx=(0, 8))

        self._refresh_table()

    def _refresh_table(self):
        """Reload table data."""
        name = self.search_entry.get()
        organ_type = self.organ_filter.get()
        status = self.status_filter.get()
        requests = list_organ_requests(name, organ_type, status)

        rows = [
            (r["id"], r["patient_name"], r["organ_type"], r.get("blood_group", ""),
             r.get("hospital", ""), r["urgency"], r["status"],
             r.get("requested_on", "")[:10])
            for r in requests
        ]
        self.table.insert_rows(rows)

    def _show_add_form(self):
        """Show add organ request popup."""
        popup = ctk.CTkToplevel(self)
        popup.title("New Organ Request")
        popup.geometry("500x420")
        popup.resizable(False, False)
        popup.grab_set()

        form = ctk.CTkFrame(popup, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=20, pady=15)

        patient_entry = create_label_entry(form, "Patient Name", 0)
        organ_dd = create_organ_type_dropdown(form, 1)
        bg_dd = create_blood_group_dropdown(form, 2)
        hospital_entry = create_label_entry(form, "Hospital", 3)
        urgency_dd = create_urgency_dropdown(form, 4, default="Normal")

        def save():
            success, msg = create_organ_request(
                patient_entry.get(), organ_dd.get(), bg_dd.get(),
                hospital_entry.get(), urgency_dd.get(),
            )
            if success:
                alert_dialog("Success", msg)
                popup.destroy()
                self._refresh_table()
            else:
                error_dialog("Validation Error", msg)

        save_btn = ctk.CTkButton(
            form, text="💾 Save Request", width=200, height=40,
            font=ctk.CTkFont(size=14, weight="bold"), command=save,
        )
        save_btn.grid(row=5, column=0, columnspan=2, pady=20)

    def _update_status(self, status):
        """Update the status of the selected request."""
        selected = self.table.get_selected_row()
        if not selected:
            error_dialog("Error", "Please select a request.")
            return

        if confirm_dialog("Update Status", f"Set request #{selected[0]} to '{status}'?"):
            change_organ_request_status(selected[0], status)
            alert_dialog("Success", f"Request status updated to '{status}'.")
            self._refresh_table()

    def _delete_request(self):
        """Delete selected request."""
        selected = self.table.get_selected_row()
        if not selected:
            error_dialog("Error", "Please select a request to delete.")
            return

        if confirm_dialog("Confirm Delete", f"Delete request #{selected[0]}?"):
            remove_organ_request(selected[0])
            alert_dialog("Deleted", "Organ request deleted.")
            self._refresh_table()
