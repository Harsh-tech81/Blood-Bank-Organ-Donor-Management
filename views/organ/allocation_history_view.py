"""Allocation history view for completed and in-flight organ workflows."""

import customtkinter as ctk

from components.data_table import DataTable
from components.dialogs import error_dialog
from config import COLORS
from models.organ_allocation_model import get_all_allocations
from utils.constants import ALLOCATION_TABLE_COLUMNS


class AllocationHistoryView(ctk.CTkFrame):
    """Read-only history of organ donor-to-recipient allocations."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(
            header, text="🔗 Allocation History",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["text_primary"], anchor="w",
        ).pack(side="left")
        ctk.CTkLabel(
            header,
            text="Traceable donor, recipient, hospital, and authorization outcomes",
            font=ctk.CTkFont(size=12), text_color=COLORS["text_muted"],
        ).pack(side="left", padx=14)
        ctk.CTkButton(
            header, text="↻ Refresh", width=100, height=32,
            fg_color=COLORS["secondary"], hover_color=COLORS["surface_hover"],
            command=self._refresh_table,
        ).pack(side="right")

        self.table = DataTable(self, columns=ALLOCATION_TABLE_COLUMNS, height=13)
        self.table.pack(fill="both", expand=True)
        self._refresh_table()

    def _refresh_table(self):
        """Reload allocation records from the audit-backed model."""
        try:
            allocations = get_all_allocations()
        except Exception as exc:
            error_dialog("Unable to load history", str(exc))
            return
        rows = [
            (
                allocation["id"],
                allocation.get("donor_name") or "Unknown donor",
                allocation.get("recipient_name") or "Unassigned",
                allocation.get("organ_type") or "—",
                allocation.get("hospital_name") or "—",
                allocation.get("status") or "—",
                (allocation.get("allocated_on") or allocation.get("created_at") or "")[:19],
            )
            for allocation in allocations
        ]
        self.table.insert_rows(rows)
