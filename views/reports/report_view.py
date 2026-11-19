"""
Report view — export data to CSV for any module.
"""

import customtkinter as ctk
from components.dialogs import alert_dialog, error_dialog
from services.export_service import export_to_csv
from models.donor_model import get_all_donors
from models.organ_donor_model import get_all_organ_donors
from models.inventory_model import get_all_inventory
from models.blood_request_model import get_all_blood_requests
from models.organ_request_model import get_all_organ_requests
from models.activity_log_model import get_recent_logs
from config import COLORS


class ReportView(ctk.CTkFrame):
    """Reports and CSV export screen."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        header = ctk.CTkLabel(
            self, text="📄 Reports & Data Export",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#ffffff", anchor="w",
        )
        header.pack(fill="x", pady=(0, 10))

        desc = ctk.CTkLabel(
            self, text="Export data from any module to a CSV file for analysis or reporting.",
            font=ctk.CTkFont(size=13), text_color="#aaaaaa", anchor="w",
        )
        desc.pack(fill="x", pady=(0, 20))

        # Export buttons
        exports = [
            ("🩸 Export Blood Donors", self._export_blood_donors),
            ("🫀 Export Organ Donors", self._export_organ_donors),
            ("📦 Export Blood Inventory", self._export_inventory),
            ("📋 Export Blood Requests", self._export_blood_requests),
            ("📝 Export Organ Requests", self._export_organ_requests),
            ("📜 Export Activity Logs", self._export_activity_logs),
        ]

        for text, command in exports:
            btn = ctk.CTkButton(
                self, text=text, width=350, height=45,
                font=ctk.CTkFont(size=14),
                fg_color=COLORS["primary"],
                anchor="w",
                command=command,
            )
            btn.pack(pady=6, padx=20, anchor="w")

    def _do_export(self, data, filename):
        """Common export handler."""
        if not data:
            error_dialog("No Data", "No data available to export.")
            return
        success, msg = export_to_csv(data, filename)
        if success:
            alert_dialog("Export Successful", msg)
        else:
            error_dialog("Export Failed", msg)

    def _export_blood_donors(self):
        self._do_export(get_all_donors(), "blood_donors.csv")

    def _export_organ_donors(self):
        self._do_export(get_all_organ_donors(), "organ_donors.csv")

    def _export_inventory(self):
        self._do_export(get_all_inventory(), "blood_inventory.csv")

    def _export_blood_requests(self):
        self._do_export(get_all_blood_requests(), "blood_requests.csv")

    def _export_organ_requests(self):
        self._do_export(get_all_organ_requests(), "organ_requests.csv")

    def _export_activity_logs(self):
        self._do_export(get_recent_logs(500), "activity_logs.csv")
