"""
Dashboard view — main application layout with sidebar navigation,
modern analytics cards with animations, inventory visual bars,
and clinical quick shortcuts.
"""

import customtkinter as ctk
from config import COLORS
from components.sidebar import Sidebar
from components.navbar import Navbar
from components.stat_card import StatCard
from models.donor_model import get_donor_count
from models.organ_donor_model import get_organ_donor_count
from models.inventory_model import get_total_blood_units, get_all_inventory
from models.blood_request_model import get_pending_blood_requests_count
from models.organ_request_model import get_pending_organ_requests_count
from models.activity_log_model import get_recent_logs


class DashboardView(ctk.CTkFrame):
    """Main app layout: sidebar + navbar + content area with sleek dark UI."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.app = master
        self.configure(fg_color=COLORS["bg_main"])

        # ─── Layout: Sidebar | Main Content ──────────────────────
        self.sidebar = Sidebar(
            self,
            on_navigate=self._navigate,
            active_key="dashboard",
            username=self.app.current_user or "Admin",
        )
        self.sidebar.pack(side="left", fill="y")

        # Right side: Navbar + Content Canvas
        right_frame = ctk.CTkFrame(self, fg_color="transparent")
        right_frame.pack(side="right", fill="both", expand=True)

        self.navbar = Navbar(
            right_frame,
            title="Overview & Metrics",
            username=self.app.current_user or "Admin",
        )
        self.navbar.pack(fill="x")

        # Scrollable / Responsive Content Area
        self.content_frame = ctk.CTkScrollableFrame(
            right_frame,
            fg_color="transparent",
            corner_radius=0,
        )
        self.content_frame.pack(fill="both", expand=True, padx=24, pady=18)

        self._show_dashboard()

    def _navigate(self, key):
        """Handle sidebar navigation between views."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        page_titles = {
            "dashboard": "Overview & Metrics",
            "blood_donors": "Blood Donors Directory",
            "blood_inventory": "Blood Bank Stock & Reserves",
            "organ_donors": "Organ Registry & Pledges",
            "blood_requests": "Blood Allocation Demands",
            "organ_requests": "Organ Match Requisitions",
            "allocations": "Allocation History",
            "reports": "Clinical Analytics & Exports",
        }

        if key == "logout":
            from services.auth_service import logout
            logout()
            self.app.logout()
            return

        self.navbar.set_title(page_titles.get(key, key))

        if key == "dashboard":
            self._show_dashboard()
        elif key == "blood_donors":
            from views.blood.donor_view import BloodDonorView
            view = BloodDonorView(self.content_frame)
            view.pack(fill="both", expand=True)
        elif key == "blood_inventory":
            from views.blood.inventory_view import InventoryView
            view = InventoryView(self.content_frame)
            view.pack(fill="both", expand=True)
        elif key == "organ_donors":
            from views.organ.organ_donor_view import OrganDonorView
            view = OrganDonorView(self.content_frame)
            view.pack(fill="both", expand=True)
        elif key == "blood_requests":
            from views.requests.blood_request_view import BloodRequestView
            view = BloodRequestView(self.content_frame)
            view.pack(fill="both", expand=True)
        elif key == "organ_requests":
            from views.requests.organ_request_view import OrganRequestView
            view = OrganRequestView(self.content_frame)
            view.pack(fill="both", expand=True)
        elif key == "allocations":
            from views.organ.allocation_history_view import AllocationHistoryView
            view = AllocationHistoryView(self.content_frame)
            view.pack(fill="both", expand=True)
        elif key == "reports":
            from views.reports.report_view import ReportView
            view = ReportView(self.content_frame)
            view.pack(fill="both", expand=True)

    def _show_dashboard(self):
        """Display the modern dashboard layout."""
        # Top Hero Greeting Banner
        banner = ctk.CTkFrame(
            self.content_frame,
            fg_color=COLORS["surface"],
            corner_radius=18,
            border_width=1,
            border_color=COLORS["surface_border"],
        )
        banner.pack(fill="x", pady=(0, 20))

        banner_inner = ctk.CTkFrame(banner, fg_color="transparent")
        banner_inner.pack(fill="x", padx=24, pady=18)

        welcome_title = ctk.CTkLabel(
            banner_inner,
            text=f"Welcome back, {self.app.current_user or 'Clinician'} 👋",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=COLORS["text_primary"],
            anchor="w",
        )
        welcome_title.pack(fill="x")

        welcome_sub = ctk.CTkLabel(
            banner_inner,
            text="Real-time operational dashboard for blood reserves, donor registrations, and active clinical allocation requests.",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_muted"],
            anchor="w",
        )
        welcome_sub.pack(fill="x", pady=(3, 0))

        # ─── Metrics Grid (StatCards with animated counters) ───
        stats_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 24))

        blood_donors = get_donor_count()
        organ_donors = get_organ_donor_count()
        total_blood = get_total_blood_units()
        pending_blood = get_pending_blood_requests_count()
        pending_organ = get_pending_organ_requests_count()

        cards_data = [
            ("Blood Donors", blood_donors, "🩸", COLORS["accent_red"], "Donors"),
            ("Blood Units Stock", total_blood, "📦", COLORS["accent_emerald"], "Units"),
            ("Organ Pledges", organ_donors, "🫀", COLORS["accent_purple"], "Registered"),
            ("Blood Requests", pending_blood, "📋", COLORS["accent_amber"], "Pending"),
            ("Organ Requests", pending_organ, "🏥", "#0284c7", "Queue"),
        ]

        for i, (title, value, icon, accent_col, badge) in enumerate(cards_data):
            card = StatCard(
                stats_frame,
                title=title,
                value=value,
                icon=icon,
                accent_color=accent_col,
                badge_text=badge,
            )
            card.grid(row=0, column=i, padx=6, pady=4, sticky="nsew")
            stats_frame.columnconfigure(i, weight=1)

        # ─── Dual Panels Section: Inventory Levels + Quick Actions ───
        panels_row = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        panels_row.pack(fill="x", pady=(0, 20))
        panels_row.columnconfigure(0, weight=3)
        panels_row.columnconfigure(1, weight=2)

        # Left Panel: Blood Group Stock Progress Bars
        inventory_panel = ctk.CTkFrame(
            panels_row,
            fg_color=COLORS["surface"],
            corner_radius=18,
            border_width=1,
            border_color=COLORS["surface_border"],
        )
        inventory_panel.grid(row=0, column=0, padx=(0, 12), sticky="nsew")

        inv_header = ctk.CTkFrame(inventory_panel, fg_color="transparent")
        inv_header.pack(fill="x", padx=20, pady=(16, 12))

        ctk.CTkLabel(
            inv_header,
            text="🩸 Blood Reserves by Group",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text_primary"],
        ).pack(side="left")

        # Render visual blood group chips
        inv_items = get_all_inventory()
        inv_grid = ctk.CTkFrame(inventory_panel, fg_color="transparent")
        inv_grid.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        for idx, item in enumerate(inv_items):
            r = idx // 4
            c = idx % 4
            inv_grid.columnconfigure(c, weight=1)

            unit_count = item["units_available"]
            chip = ctk.CTkFrame(inv_grid, fg_color="#0f172a", corner_radius=12, border_width=1, border_color="#1e293b")
            chip.grid(row=r, column=c, padx=6, pady=6, sticky="nsew")

            group_lbl = ctk.CTkLabel(
                chip,
                text=item["blood_group"],
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=COLORS["accent_red"],
            )
            group_lbl.pack(pady=(8, 0))

            qty_lbl = ctk.CTkLabel(
                chip,
                text=f"{unit_count} Units",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=COLORS["text_secondary"],
            )
            qty_lbl.pack(pady=(0, 8))

        # Right Panel: Workflow Shortcuts
        actions_panel = ctk.CTkFrame(
            panels_row,
            fg_color=COLORS["surface"],
            corner_radius=18,
            border_width=1,
            border_color=COLORS["surface_border"],
        )
        actions_panel.grid(row=0, column=1, sticky="nsew")

        act_header = ctk.CTkFrame(actions_panel, fg_color="transparent")
        act_header.pack(fill="x", padx=20, pady=(16, 12))

        ctk.CTkLabel(
            act_header,
            text="⚡ Clinical Workflow Actions",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text_primary"],
        ).pack(side="left")

        actions_list = [
            ("➕ Register New Blood Donor", "blood_donors", COLORS["primary"], COLORS["primary_hover"]),
            ("🫀 Register Organ Donor Pledge", "organ_donors", COLORS["accent_purple"], COLORS["accent_purple_hover"]),
            ("📋 File Blood Requisition", "blood_requests", COLORS["accent_amber"], "#b45309"),
            ("📦 Update Inventory Reserves", "blood_inventory", COLORS["accent_emerald"], COLORS["accent_emerald_hover"]),
            ("📊 Generate & Export Reports", "reports", "#475569", "#334155"),
        ]

        for text, key, col, hover_col in actions_list:
            btn = ctk.CTkButton(
                actions_panel,
                text=text,
                font=ctk.CTkFont(size=13, weight="bold"),
                height=38,
                corner_radius=10,
                fg_color=col,
                hover_color=hover_col,
                anchor="w",
                command=lambda k=key: self._quick_navigate(k),
            )
            btn.pack(fill="x", padx=18, pady=4)

        # Recent activity gives operators a quick audit trail without leaving overview.
        activity_panel = ctk.CTkFrame(
            self.content_frame, fg_color=COLORS["surface"], corner_radius=18,
            border_width=1, border_color=COLORS["surface_border"],
        )
        activity_panel.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(
            activity_panel, text="🕘 Recent Activity",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text_primary"], anchor="w",
        ).pack(fill="x", padx=20, pady=(16, 8))
        logs = get_recent_logs(5)
        if not logs:
            ctk.CTkLabel(
                activity_panel, text="No activity recorded yet.",
                font=ctk.CTkFont(size=12), text_color=COLORS["text_muted"],
            ).pack(anchor="w", padx=20, pady=(0, 16))
        else:
            for log in logs:
                row = ctk.CTkFrame(activity_panel, fg_color="transparent")
                row.pack(fill="x", padx=20, pady=3)
                ctk.CTkLabel(
                    row, text=f"•  {log.get('action', 'Activity')}",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=COLORS["text_secondary"], anchor="w",
                ).pack(side="left")
                ctk.CTkLabel(
                    row, text=f"{log.get('performed_by', 'system')}  ·  {(log.get('timestamp') or '')[:16]}",
                    font=ctk.CTkFont(size=11), text_color=COLORS["text_muted"],
                ).pack(side="right")

    def _quick_navigate(self, key):
        """Navigate smoothly from workflow buttons."""
        self.sidebar.set_active(key)
