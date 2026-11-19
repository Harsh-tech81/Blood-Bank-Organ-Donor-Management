"""
Reusable modern data table component with dark theme,
custom rounded borders, zebra row striping, and sort indicators.
"""

import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from config import COLORS


class DataTable(ctk.CTkFrame):
    """
    A modernized sortable data table component.
    """

    def __init__(self, master, columns: list, height=15, **kwargs):
        super().__init__(
            master,
            fg_color=COLORS["surface"],
            corner_radius=14,
            border_width=1,
            border_color=COLORS["surface_border"],
            **kwargs,
        )

        self.column_names = [col[0] for col in columns]
        self.column_widths = [col[1] for col in columns]

        # ─── Configure Treeview Style ────────────────────────────
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Modern.Treeview",
            background="#111827",
            foreground="#f3f4f6",
            fieldbackground="#111827",
            rowheight=34,
            font=("Segoe UI", 10),
            borderwidth=0,
        )
        style.configure(
            "Modern.Treeview.Heading",
            background="#1f2937",
            foreground="#9ca3af",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padding=(6, 8),
        )
        style.map(
            "Modern.Treeview",
            background=[("selected", "#2563eb")],
            foreground=[("selected", "#ffffff")],
        )
        style.map(
            "Modern.Treeview.Heading",
            background=[("active", "#374151")],
            foreground=[("active", "#ffffff")],
        )

        # Container
        tree_frame = ctk.CTkFrame(self, fg_color="transparent")
        tree_frame.pack(fill="both", expand=True, padx=8, pady=8)

        self.tree = ttk.Treeview(
            tree_frame,
            columns=self.column_names,
            show="headings",
            height=height,
            style="Modern.Treeview",
            selectmode="browse",
        )

        # Configure columns
        for name, width in columns:
            self.tree.heading(name, text=name, command=lambda c=name: self._sort_by(c))
            self.tree.column(name, width=width, minwidth=50, anchor="center")

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Tags for alternating subtle zebra stripes
        self.tree.tag_configure("evenrow", background="#111827")
        self.tree.tag_configure("oddrow", background="#151f30")

        self._sort_column = None
        self._sort_reverse = False

    def insert_rows(self, rows: list):
        """Clear and insert new rows with alternating colors."""
        self.clear()
        for idx, row in enumerate(rows):
            tag = "evenrow" if idx % 2 == 0 else "oddrow"
            self.tree.insert("", "end", values=row, tags=(tag,))

    def clear(self):
        """Remove all rows."""
        for item in self.tree.get_children():
            self.tree.delete(item)

    def get_selected_row(self):
        """Get the values of the selected row, or None."""
        selection = self.tree.selection()
        if not selection:
            return None
        return self.tree.item(selection[0])["values"]

    def get_all_rows(self) -> list:
        """Get all rows as a list of tuples."""
        return [self.tree.item(item)["values"] for item in self.tree.get_children()]

    def bind_select(self, callback):
        self.tree.bind("<<TreeviewSelect>>", callback)

    def bind_double_click(self, callback):
        self.tree.bind("<Double-1>", callback)

    def _sort_by(self, column: str):
        """Sort rows by a column (toggle ascending/descending)."""
        if self._sort_column == column:
            self._sort_reverse = not self._sort_reverse
        else:
            self._sort_column = column
            self._sort_reverse = False

        items = [(self.tree.set(k, column), k) for k in self.tree.get_children()]

        try:
            items.sort(key=lambda t: float(t[0]), reverse=self._sort_reverse)
        except (ValueError, TypeError):
            items.sort(key=lambda t: str(t[0]).lower(), reverse=self._sort_reverse)

        for index, (_, k) in enumerate(items):
            self.tree.move(k, "", index)
            tag = "evenrow" if index % 2 == 0 else "oddrow"
            self.tree.item(k, tags=(tag,))
