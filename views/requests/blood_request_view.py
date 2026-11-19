"""
Blood request view — manage blood requests with urgency triage,
stock validation indicators, and automatic inventory fulfillment.
"""

import customtkinter as ctk
from components.data_table import DataTable
from components.form_fields import (
    create_label_entry, create_blood_group_dropdown,
    create_urgency_dropdown, create_dropdown,
)
from components.dialogs import confirm_dialog, alert_dialog, error_dialog
from services.blood_request_service import (
    create_blood_request, change_blood_request_status,
    remove_blood_request, list_blood_requests,
)
from models.inventory_model import get_inventory_by_blood_group
from utils.constants import BLOOD_REQUEST_TABLE_COLUMNS, BLOOD_GROUPS, BLOOD_REQUEST_STATUSES
from config import COLORS


class BloodRequestView(ctk.CTkFrame):
    """Blood request management screen with clinical priority triage."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        # ─── Top Header Notice ───────────────────────────────────
        triage_banner = ctk.CTkFrame(self, fg_color="#181e2e", corner_radius=12, border_width=1, border_color="#1e293b")
        triage_banner.pack(fill="x", pady=(0, 12))

        tb_inner = ctk.CTkFrame(triage_banner, fg_color="transparent")
        tb_inner.pack(fill="x", padx=16, pady=8)

        ctk.CTkLabel(
            tb_inner,
            text="🚨 CLINICAL TRIAGE PRIORITY ACTIVE",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS["danger"],
        ).pack(side="left")

        ctk.CTkLabel(
            tb_inner,
            text="— 'Critical' and 'Urgent' cases are automatically pinned to the top.",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_muted"],
        ).pack(side="left", padx=8)

        # ─── Filter & Action Bar ─────────────────────────────────
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.pack(fill="x", pady=(0, 10))

        self.search_entry = ctk.CTkEntry(
            top_bar, placeholder_text="🔍 Search patient name...",
            width=220, height=36, font=ctk.CTkFont(size=13),
        )
        self.search_entry.pack(side="left", padx=(0, 8))
        self.search_entry.bind("<KeyRelease>", lambda e: self._refresh_table())

        self.bg_filter = ctk.CTkComboBox(
            top_bar, values=["All"] + BLOOD_GROUPS, width=100,
            height=36, state="readonly", command=lambda _: self._refresh_table(),
        )
        self.bg_filter.set("All")
        self.bg_filter.pack(side="left", padx=(0, 8))

        self.status_filter = ctk.CTkComboBox(
            top_bar, values=["All"] + BLOOD_REQUEST_STATUSES, width=120,
            height=36, state="readonly", command=lambda _: self._refresh_table(),
        )
        self.status_filter.set("All")
        self.status_filter.pack(side="left", padx=(0, 8))

        add_btn = ctk.CTkButton(
            top_bar, text="➕ Place Request", width=140, height=36,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
            command=self._show_add_form,
        )
        add_btn.pack(side="right")

        # ─── Data Table ──────────────────────────────────────────
        self.table = DataTable(self, columns=BLOOD_REQUEST_TABLE_COLUMNS, height=13)
        self.table.pack(fill="both", expand=True, pady=(0, 10))

        # ─── Action Buttons ──────────────────────────────────────
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x")

        fulfill_btn = ctk.CTkButton(
            btn_frame, text="📦 Verify & Fulfill (Deduct Stock)", width=230, height=36,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLORS["accent_emerald"], hover_color=COLORS["accent_emerald_hover"],
            command=lambda: self._handle_fulfill(),
        )
        fulfill_btn.pack(side="left", padx=(0, 8))

        approve_btn = ctk.CTkButton(
            btn_frame, text="✅ Approve Requisition", width=160, height=36,
            font=ctk.CTkFont(size=13),
            fg_color="#334155", hover_color="#475569",
            command=lambda: self._update_status("Approved"),
        )
        approve_btn.pack(side="left", padx=(0, 8))

        reject_btn = ctk.CTkButton(
            btn_frame, text="❌ Reject", width=100, height=36,
            fg_color=COLORS["danger"], hover_color="#b91c1c",
            command=lambda: self._update_status("Rejected"),
        )
        reject_btn.pack(side="left", padx=(0, 8))

        delete_btn = ctk.CTkButton(
            btn_frame, text="🗑️ Delete", width=100, height=36,
            fg_color="#1e293b", hover_color="#334155",
            command=self._delete_request,
        )
        delete_btn.pack(side="left", padx=(0, 8))

        self._refresh_table()

    def _refresh_table(self):
        """Reload table data preserving urgency order."""
        name = self.search_entry.get()
        blood_group = self.bg_filter.get()
        status = self.status_filter.get()
        requests = list_blood_requests(name, blood_group, status)

        rows = []
        for r in requests:
            urg = r["urgency"]
            urg_display = f"🚨 {urg}" if urg == "Critical" else (f"⚠️ {urg}" if urg == "Urgent" else urg)
            rows.append((
                r["id"],
                r["patient_name"],
                r["blood_group"],
                r["units_needed"],
                r.get("hospital", ""),
                urg_display,
                r["status"],
                r.get("requested_on", "")[:10],
            ))
        self.table.insert_rows(rows)

    def _show_add_form(self):
        """Show add blood request popup with live inventory indicator."""
        popup = ctk.CTkToplevel(self)
        popup.title("Register Blood Requisition")
        popup.geometry("520x490")
        popup.resizable(False, False)
        popup.grab_set()

        form = ctk.CTkFrame(popup, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=24, pady=18)

        patient_entry = create_label_entry(form, "Patient Name", 0)

        # Blood group with live stock indicator
        bg_dd = create_blood_group_dropdown(form, 1)

        stock_info_lbl = ctk.CTkLabel(
            form, text="Reserve check: Select group",
            font=ctk.CTkFont(size=11), text_color=COLORS["text_muted"], anchor="w",
        )
        stock_info_lbl.grid(row=2, column=1, padx=(5, 10), pady=(0, 6), sticky="w")

        def update_stock_preview(choice):
            inv = get_inventory_by_blood_group(choice)
            avail = inv["units_available"] if inv else 0
            if avail > 0:
                stock_info_lbl.configure(text=f"✓ Current Reserve: {avail} unit(s) available", text_color=COLORS["success"])
            else:
                stock_info_lbl.configure(text="⚠️ Current Reserve: 0 units available (Shortage)", text_color=COLORS["danger"])

        bg_dd.configure(command=update_stock_preview)
        update_stock_preview(bg_dd.get())

        units_entry = create_label_entry(form, "Units Required", 3, default_value="1")
        hospital_entry = create_label_entry(form, "Hospital / Facility", 4)
        urgency_dd = create_urgency_dropdown(form, 5, default="Normal")

        def save():
            success, msg = create_blood_request(
                patient_entry.get(), bg_dd.get(), units_entry.get(),
                hospital_entry.get(), urgency_dd.get(),
            )
            if success:
                alert_dialog("Requisition Logged", msg)
                popup.destroy()
                self._refresh_table()
            else:
                error_dialog("Validation Error", msg)

        save_btn = ctk.CTkButton(
            form, text="💾 Submit Requisition", width=220, height=42,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
            command=save,
        )
        save_btn.grid(row=6, column=0, columnspan=2, pady=20)

    def _handle_fulfill(self):
        """Fulfill selected request with inventory validation."""
        selected = self.table.get_selected_row()
        if not selected:
            error_dialog("Selection Required", "Please select a requisition to fulfill.")
            return

        req_id = selected[0]
        patient = selected[1]
        blood_group = selected[2]
        units = selected[3]

        if confirm_dialog(
            "Confirm Stock Fulfillment",
            f"Fulfill request #{req_id} for patient '{patient}'?\n\n"
            f"This will immediately verify reserves and deduct {units} unit(s) of {blood_group} from the blood inventory.",
        ):
            success, msg = change_blood_request_status(req_id, "Fulfilled")
            if success:
                alert_dialog("Fulfillment Complete", msg)
                self._refresh_table()
            else:
                error_dialog("Fulfillment Blocked", msg)

    def _update_status(self, status):
        """Update the status of the selected request."""
        selected = self.table.get_selected_row()
        if not selected:
            error_dialog("Selection Required", "Please select a requisition.")
            return

        req_id = selected[0]
        if confirm_dialog("Update Status", f"Set request #{req_id} to '{status}'?"):
            success, msg = change_blood_request_status(req_id, status)
            if success:
                alert_dialog("Success", msg)
                self._refresh_table()
            else:
                error_dialog("Error", msg)

    def _delete_request(self):
        """Delete selected request."""
        selected = self.table.get_selected_row()
        if not selected:
            error_dialog("Selection Required", "Please select a requisition to delete.")
            return

        if confirm_dialog("Confirm Delete", f"Permanently delete requisition #{selected[0]}?"):
            remove_blood_request(selected[0])
            alert_dialog("Deleted", "Blood requisition removed.")
            self._refresh_table()
