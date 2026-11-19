"""
Dashboard view — main application layout with sidebar navigation.
Shows summary statistics and acts as the navigation hub.
"""

import customtkinter as ctk
from config import COLORS
from components.sidebar import Sidebar
from components.navbar import Navbar
from components.stat_card import StatCard
from models.donor_model import get_donor_count
from models.organ_donor_model import get_organ_donor_count
from models.inventory_model import get_total_blood_units
from models.blood_request_model import get_pending_blood_requests_count
from models.organ_request_model import get_pending_organ_requests_count


class DashboardView(ctk.CTkFrame):
    """Main app layout: sidebar + navbar + content area."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.app = master
        self.configure(fg_color="#0e0e1a")

        # ─── Layout: Sidebar | Main Content ──────────────────────
        self.sidebar = Sidebar(self, on_navigate=self._navigate, active_key="dashboard")
        self.sidebar.pack(side="left", fill="y")

        # Right side: Navbar + Content
        right_frame = ctk.CTkFrame(self, fg_color="transparent")
        right_frame.pack(side="right", fill="both", expand=True)

        self.navbar = Navbar(right_frame, title="📊 Dashboard",
                             username=self.app.current_user or "Admin")
        self.navbar.pack(fill="x")

        # Content area
        self.content_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=15)

        # Show dashboard content
        self._show_dashboard()

    def _navigate(self, key):
        """Handle sidebar navigation."""
        # Clear content area
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        page_titles = {
            "dashboard": "📊 Dashboard",
            "blood_donors": "🩸 Blood Donors",
            "blood_inventory": "📦 Blood Inventory",
            "organ_donors": "🫀 Organ Donors",
            "blood_requests": "📋 Blood Requests",
            "organ_requests": "📝 Organ Requests",
            "reports": "📄 Reports",
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
        elif key == "reports":
            from views.reports.report_view import ReportView
            view = ReportView(self.content_frame)
            view.pack(fill="both", expand=True)

    def _show_dashboard(self):
        """Display the dashboard with stat cards."""
        # Welcome message
        welcome = ctk.CTkLabel(
            self.content_frame,
            text="Welcome to Blood Bank & Organ Donors Management System",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#ffffff",
        )
        welcome.pack(pady=(10, 20))

        # Stat cards row
        stats_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        stats_frame.pack(fill="x", pady=10)

        # Fetch stats
        blood_donors = get_donor_count()
        organ_donors = get_organ_donor_count()
        total_blood = get_total_blood_units()
        pending_blood = get_pending_blood_requests_count()
        pending_organ = get_pending_organ_requests_count()

        cards_data = [
            ("Blood Donors", blood_donors, "🩸", "#1a3a5c"),
            ("Organ Donors", organ_donors, "🫀", "#3a1a5c"),
            ("Blood Units", total_blood, "📦", "#1a5c3a"),
            ("Pending Blood Req.", pending_blood, "📋", "#5c3a1a"),
            ("Pending Organ Req.", pending_organ, "📝", "#5c1a3a"),
        ]

        for i, (title, value, icon, color) in enumerate(cards_data):
            card = StatCard(
                stats_frame, title=title, value=value, icon=icon, color=color
            )
            card.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")
            stats_frame.columnconfigure(i, weight=1)

        # Quick actions section
        actions_label = ctk.CTkLabel(
            self.content_frame,
            text="Quick Actions",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#ffffff",
            anchor="w",
        )
        actions_label.pack(fill="x", pady=(30, 10))

        actions_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        actions_frame.pack(fill="x")

        actions = [
            ("🩸 Add Blood Donor", "blood_donors"),
            ("🫀 Add Organ Donor", "organ_donors"),
            ("📋 New Blood Request", "blood_requests"),
            ("📝 New Organ Request", "organ_requests"),
            ("📦 Manage Inventory", "blood_inventory"),
        ]

        for i, (text, key) in enumerate(actions):
            btn = ctk.CTkButton(
                actions_frame,
                text=text,
                font=ctk.CTkFont(size=13),
                height=40,
                corner_radius=8,
                fg_color=COLORS["primary"],
                command=lambda k=key: self._quick_navigate(k),
            )
            btn.grid(row=0, column=i, padx=8, pady=5, sticky="ew")
            actions_frame.columnconfigure(i, weight=1)

    def _quick_navigate(self, key):
        """Navigate to a view from the quick action buttons."""
        self.sidebar.set_active(key)
