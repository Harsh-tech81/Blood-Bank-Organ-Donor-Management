"""
Organ request view — manage organ requests with clinical urgency triage,
registry match verification, and donor allocation workflows.
"""

import customtkinter as ctk
from tkinter import simpledialog
from components.data_table import DataTable
from components.form_fields import (
    create_label_entry, create_blood_group_dropdown,
    create_organ_type_dropdown, create_urgency_dropdown,
)
from components.dialogs import confirm_dialog, alert_dialog, error_dialog
from services.organ_request_service import (
    create_organ_request, change_organ_request_status,
    remove_organ_request, list_organ_requests, review_request,
    propose_allocation, authorize_transplant,
)
from models.organ_donor_model import search_organ_donors
from models.organ_request_model import get_organ_request_by_id
from utils.constants import ORGAN_REQUEST_TABLE_COLUMNS, ORGAN_TYPES, ORGAN_REQUEST_STATUSES
from config import COLORS


class OrganRequestView(ctk.CTkFrame):
    """Organ request management screen with clinical urgency triage."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        # ─── Top Header Notice ───────────────────────────────────
        triage_banner = ctk.CTkFrame(self, fg_color="#181e2e", corner_radius=12, border_width=1, border_color="#1e293b")
        triage_banner.pack(fill="x", pady=(0, 12))

        tb_inner = ctk.CTkFrame(triage_banner, fg_color="transparent")
        tb_inner.pack(fill="x", padx=16, pady=8)

        ctk.CTkLabel(
            tb_inner,
            text="🫀 ORGAN ALLOCATION TRIAGE ACTIVE",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS["accent_purple"],
        ).pack(side="left")

        ctk.CTkLabel(
            tb_inner,
            text="— Requisitions are strictly prioritized by Clinical Urgency and waiting time.",
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

        self.organ_filter = ctk.CTkComboBox(
            top_bar, values=["All"] + ORGAN_TYPES, width=130,
            height=36, state="readonly", command=lambda _: self._refresh_table(),
        )
        self.organ_filter.set("All")
        self.organ_filter.pack(side="left", padx=(0, 8))

        self.status_filter = ctk.CTkComboBox(
            top_bar, values=["All"] + ORGAN_REQUEST_STATUSES, width=120,
            height=36, state="readonly", command=lambda _: self._refresh_table(),
        )
        self.status_filter.set("All")
        self.status_filter.pack(side="left", padx=(0, 8))

        add_btn = ctk.CTkButton(
            top_bar, text="➕ Place Requisition", width=160, height=36,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLORS["accent_purple"], hover_color=COLORS["accent_purple_hover"],
            command=self._show_add_form,
        )
        add_btn.pack(side="right")

        # ─── Data Table ──────────────────────────────────────────
        self.table = DataTable(self, columns=ORGAN_REQUEST_TABLE_COLUMNS, height=13)
        self.table.pack(fill="both", expand=True, pady=(0, 10))

        # ─── Action Buttons ──────────────────────────────────────
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x")

        match_btn = ctk.CTkButton(
            btn_frame, text="🔗 Reserve Authorized", width=180, height=36,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
            command=lambda: self._handle_match(),
        )
        match_btn.pack(side="left", padx=(0, 8))

        fulfill_btn = ctk.CTkButton(
            btn_frame, text="✅ Complete Workflow", width=170, height=36,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLORS["accent_emerald"], hover_color=COLORS["accent_emerald_hover"],
            command=lambda: self._handle_fulfill(),
        )
        fulfill_btn.pack(side="left", padx=(0, 8))

        reject_btn = ctk.CTkButton(
            btn_frame, text="❌ Reject", width=100, height=36,
            fg_color=COLORS["danger"], hover_color="#b91c1c",
            command=lambda: self._update_status("Rejected"),
        )
        reject_btn.pack(side="left", padx=(0, 8))

        review_btn = ctk.CTkButton(
            btn_frame, text="📝 Review Request", width=140, height=36,
            fg_color=COLORS["info"], command=self._review_selected,
        )
        review_btn.pack(side="left", padx=(0, 8))

        proposal_btn = ctk.CTkButton(
            btn_frame, text="🔎 Propose Candidate", width=150, height=36,
            fg_color=COLORS["primary"], command=self._propose_selected,
        )
        proposal_btn.pack(side="left", padx=(0, 8))

        authority_btn = ctk.CTkButton(
            btn_frame, text="📄 Record Authority", width=150, height=36,
            fg_color=COLORS["warning"], command=self._authorize_selected,
        )
        authority_btn.pack(side="left", padx=(0, 8))

        delete_btn = ctk.CTkButton(
            btn_frame, text="🗑️ Delete", width=100, height=36,
            fg_color="#1e293b", hover_color="#334155",
            command=self._delete_request,
        )
        delete_btn.pack(side="left", padx=(0, 8))

        self._refresh_table()

    def _refresh_table(self):
        """Reload table data preserving urgency ordering."""
        name = self.search_entry.get()
        organ_type = self.organ_filter.get()
        status = self.status_filter.get()
        requests = list_organ_requests(name, organ_type, status)

        rows = []
        for r in requests:
            urg = r["urgency"]
            urg_display = f"🚨 {urg}" if urg == "Critical" else (f"⚠️ {urg}" if urg == "Urgent" else urg)
            rows.append((
                r["id"],
                r["patient_name"],
                r["organ_type"],
                r.get("blood_group", ""),
                r.get("hospital", ""),
                urg_display,
                r["status"],
                r.get("requested_on", "")[:10],
            ))
        self.table.insert_rows(rows)

    def _show_add_form(self):
        """Show add organ request popup with live registry preview."""
        popup = ctk.CTkToplevel(self)
        popup.title("Register Organ Requisition")
        popup.geometry("520x490")
        popup.resizable(False, False)
        popup.grab_set()

        form = ctk.CTkFrame(popup, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=24, pady=18)

        patient_entry = create_label_entry(form, "Patient Name", 0)
        organ_dd = create_organ_type_dropdown(form, 1)

        match_info_lbl = ctk.CTkLabel(
            form, text="Registry match check: Select organ",
            font=ctk.CTkFont(size=11), text_color=COLORS["text_muted"], anchor="w",
        )
        match_info_lbl.grid(row=2, column=1, padx=(5, 10), pady=(0, 6), sticky="w")

        def update_registry_preview(choice):
            matches = search_organ_donors(organ_type=choice)
            consented = [
                d for d in matches
                if d.get("consent_status") == "Consented"
                and d.get("status") == "Available"
                and d.get("review_status") == "Verified"
            ]
            if consented:
                match_info_lbl.configure(
                    text=f"✓ Registry: {len(consented)} reviewed donor candidate(s)",
                    text_color=COLORS["success"],
                )
            else:
                match_info_lbl.configure(
                    text="⚠️ Registry: no reviewed donor candidates currently available",
                    text_color=COLORS["warning"],
                )

        organ_dd.configure(command=update_registry_preview)
        update_registry_preview(organ_dd.get())

        bg_dd = create_blood_group_dropdown(form, 3)
        hospital_entry = create_label_entry(form, "Hospital / Transplant Unit", 4)
        urgency_dd = create_urgency_dropdown(form, 5, default="Normal")

        def save():
            success, msg = create_organ_request(
                patient_entry.get(), organ_dd.get(), bg_dd.get(),
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
            fg_color=COLORS["accent_purple"], hover_color=COLORS["accent_purple_hover"],
            command=save,
        )
        save_btn.grid(row=6, column=0, columnspan=2, pady=20)

    def _handle_match(self):
        """Match request with an active consented donor."""
        selected = self.table.get_selected_row()
        if not selected:
            error_dialog("Selection Required", "Please select a requisition.")
            return

        req_id = selected[0]
        patient = selected[1]
        organ = selected[2]

        if confirm_dialog(
            "Reserve Authorized Allocation",
            f"Reserve the approved allocation proposal for '{patient}'?\n\n"
            "This records workflow authorization; it does not determine clinical eligibility.",
        ):
            success, msg = change_organ_request_status(req_id, "Matched")
            if success:
                alert_dialog("Donor Matched", msg)
                self._refresh_table()
            else:
                error_dialog("Match Blocked", msg)

    def _handle_fulfill(self):
        """Allocate organ and transition request to Fulfilled."""
        selected = self.table.get_selected_row()
        if not selected:
            error_dialog("Selection Required", "Please select a requisition.")
            return

        req_id = selected[0]
        patient = selected[1]
        organ = selected[2]

        if confirm_dialog(
            "Confirm Organ Allocation",
            f"Fulfill request #{req_id} for '{patient}'?\n\n"
            f"This will complete the recorded workflow for '{organ}'.\n\n"
            "Confirm that the external clinical and authority procedures have already occurred.",
        ):
            success, msg = change_organ_request_status(req_id, "Fulfilled")
            if success:
                alert_dialog("Allocation Successful", msg)
                self._refresh_table()
            else:
                error_dialog("Allocation Blocked", msg)

    def _review_selected(self):
        """Record recipient/request review."""
        selected = self.table.get_selected_row()
        if not selected:
            error_dialog("Selection Required", "Please select a requisition.")
            return
        notes = simpledialog.askstring(
            "Request Review Notes",
            "Enter review notes or supporting document reference:",
            parent=self,
        )
        if not notes:
            return
        success, msg = review_request(selected[0], "Approved", notes)
        if success:
            alert_dialog("Review Recorded", msg)
            self._refresh_table()
        else:
            error_dialog("Review Blocked", msg)

    def _propose_selected(self):
        """Create a non-clinical registry candidate proposal."""
        selected = self.table.get_selected_row()
        if not selected:
            error_dialog("Selection Required", "Please select a requisition.")
            return
        success, msg = propose_allocation(selected[0])
        if success:
            alert_dialog("Proposal Recorded", msg)
            self._refresh_table()
        else:
            error_dialog("Proposal Blocked", msg)

    def _authorize_selected(self):
        """Record external transplant-authority approval."""
        selected = self.table.get_selected_row()
        if not selected:
            error_dialog("Selection Required", "Please select a requisition.")
            return
        request = get_organ_request_by_id(selected[0])
        if not request or not request.get("matched_donor_id"):
            error_dialog("Authorization Blocked", "Create an allocation proposal first.")
            return
        authority = simpledialog.askstring(
            "Transplant Authority", "Authority name:", parent=self,
        )
        reference = simpledialog.askstring(
            "Authorization Reference", "External reference number:", parent=self,
        )
        notes = simpledialog.askstring(
            "Authorization Notes", "Approval notes:", parent=self,
        )
        if not authority or not reference or not notes:
            error_dialog("Authorization Required", "All authority fields are required.")
            return
        success, msg = authorize_transplant(
            selected[0], request["matched_donor_id"], authority, reference, notes,
        )
        if success:
            alert_dialog("Authority Recorded", msg)
            self._refresh_table()
        else:
            error_dialog("Authorization Blocked", msg)

    def _update_status(self, status):
        """Update the status of the selected request."""
        selected = self.table.get_selected_row()
        if not selected:
            error_dialog("Selection Required", "Please select a requisition.")
            return

        req_id = selected[0]
        if confirm_dialog("Update Status", f"Set request #{req_id} to '{status}'?"):
            success, msg = change_organ_request_status(req_id, status)
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
            remove_organ_request(selected[0])
            alert_dialog("Deleted", "Organ requisition deleted.")
            self._refresh_table()
