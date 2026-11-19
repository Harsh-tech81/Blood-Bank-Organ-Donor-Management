"""
Blood inventory view — manage blood stock levels.
"""

import customtkinter as ctk
from components.data_table import DataTable
from components.dialogs import alert_dialog, error_dialog, confirm_dialog
from services.inventory_service import get_inventory, add_blood_units, remove_blood_units
from utils.constants import INVENTORY_TABLE_COLUMNS
from config import COLORS


class InventoryView(ctk.CTkFrame):
    """Blood inventory management screen."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        # ─── Header ──────────────────────────────────────────────
        header = ctk.CTkLabel(
            self, text="Blood Inventory — Stock Levels by Blood Group",
            font=ctk.CTkFont(size=16, weight="bold"), text_color="#ffffff", anchor="w",
        )
        header.pack(fill="x", pady=(0, 10))

        # ─── Data Table ──────────────────────────────────────────
        self.table = DataTable(self, columns=INVENTORY_TABLE_COLUMNS, height=10)
        self.table.pack(fill="both", expand=True, pady=(0, 15))

        # ─── Action Bar ──────────────────────────────────────────
        action_frame = ctk.CTkFrame(self, fg_color="#1e1e2e", corner_radius=10)
        action_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            action_frame, text="Units:", font=ctk.CTkFont(size=13),
        ).pack(side="left", padx=(15, 5), pady=10)

        self.units_entry = ctk.CTkEntry(
            action_frame, width=80, height=35, font=ctk.CTkFont(size=13),
            placeholder_text="1",
        )
        self.units_entry.insert(0, "1")
        self.units_entry.pack(side="left", padx=5, pady=10)

        add_btn = ctk.CTkButton(
            action_frame, text="➕ Add Units", width=130, height=35,
            fg_color=COLORS["success"], hover_color="#218838",
            command=self._add_units,
        )
        add_btn.pack(side="left", padx=8, pady=10)

        remove_btn = ctk.CTkButton(
            action_frame, text="➖ Remove Units", width=140, height=35,
            fg_color=COLORS["danger"], hover_color="#c82333",
            command=self._remove_units,
        )
        remove_btn.pack(side="left", padx=8, pady=10)

        refresh_btn = ctk.CTkButton(
            action_frame, text="🔄 Refresh", width=100, height=35,
            fg_color=COLORS["info"],
            command=self._refresh_table,
        )
        refresh_btn.pack(side="right", padx=15, pady=10)

        # Load data
        self._refresh_table()

    def _refresh_table(self):
        """Reload inventory data."""
        inventory = get_inventory()
        rows = [
            (item["id"], item["blood_group"], item["units_available"],
             item.get("next_expiry_date") or "No dated stock",
             item.get("batch_units_available", 0),
             item.get("last_updated", "")[:19])
            for item in inventory
        ]
        self.table.insert_rows(rows)

    def _get_units(self):
        """Get the number of units from the entry field."""
        try:
            units = int(self.units_entry.get())
            if units < 1:
                raise ValueError
            return units
        except ValueError:
            error_dialog("Error", "Please enter a valid positive number for units.")
            return None

    def _add_units(self):
        """Add units to selected blood group."""
        selected = self.table.get_selected_row()
        if not selected:
            error_dialog("Error", "Please select a blood group from the table.")
            return

        units = self._get_units()
        if units is None:
            return

        blood_group = selected[1]
        add_blood_units(blood_group, units)
        alert_dialog("Success", f"Added {units} unit(s) to {blood_group}.")
        self._refresh_table()

    def _remove_units(self):
        """Remove units from selected blood group."""
        selected = self.table.get_selected_row()
        if not selected:
            error_dialog("Error", "Please select a blood group from the table.")
            return

        units = self._get_units()
        if units is None:
            return

        blood_group = selected[1]
        if not confirm_dialog(
            "Confirm Stock Removal",
            f"Remove {units} unit(s) from {blood_group}?\n\n"
            "This changes the available reserve and is recorded in the workflow.",
        ):
            return
        success, msg = remove_blood_units(blood_group, units)
        if success:
            alert_dialog("Success", f"Removed {units} unit(s) from {blood_group}.")
        else:
            error_dialog("Error", f"Cannot remove {units} unit(s): not enough stock.")
        self._refresh_table()
