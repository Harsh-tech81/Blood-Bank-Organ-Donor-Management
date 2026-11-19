"""
Reusable data table component.
Wraps tkinter Treeview with sorting, selection, and styling.
"""

import tkinter as tk
from tkinter import ttk
import customtkinter as ctk


class DataTable(ctk.CTkFrame):
    """
    A reusable sortable table component.

    Usage:
        table = DataTable(parent, columns=[("ID", 50), ("Name", 150), ...])
        table.insert_rows([(1, "John"), (2, "Jane"), ...])
        selected = table.get_selected_row()
    """

    def __init__(self, master, columns: list, height=15, **kwargs):
        """
        Args:
            columns: List of (column_name, width) tuples.
            height: Number of visible rows.
        """
        super().__init__(master, **kwargs)

        self.column_names = [col[0] for col in columns]
        self.column_widths = [col[1] for col in columns]

        # ─── Style ───────────────────────────────────────────────
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Custom.Treeview",
            background="#2b2b2b",
            foreground="#ffffff",
            fieldbackground="#2b2b2b",
            rowheight=32,
            font=("Segoe UI", 11),
        )
        style.configure(
            "Custom.Treeview.Heading",
            background="#1a1a2e",
            foreground="#ffffff",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
        )
        style.map(
            "Custom.Treeview",
            background=[("selected", "#1f6aa5")],
            foreground=[("selected", "#ffffff")],
        )
        style.map(
            "Custom.Treeview.Heading",
            background=[("active", "#16213e")],
        )

        # ─── Treeview ────────────────────────────────────────────
        tree_frame = ctk.CTkFrame(self, fg_color="transparent")
        tree_frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(
            tree_frame,
            columns=self.column_names,
            show="headings",
            height=height,
            style="Custom.Treeview",
            selectmode="browse",
        )

        # Configure columns
        for name, width in columns:
            self.tree.heading(name, text=name, command=lambda c=name: self._sort_by(c))
            self.tree.column(name, width=width, minwidth=40, anchor="center")

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Sort state
        self._sort_column = None
        self._sort_reverse = False

    def insert_rows(self, rows: list):
        """Clear and insert new rows."""
        self.clear()
        for row in rows:
            self.tree.insert("", "end", values=row)

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
        """Bind a callback to row selection events."""
        self.tree.bind("<<TreeviewSelect>>", callback)

    def bind_double_click(self, callback):
        """Bind a callback to double-click events."""
        self.tree.bind("<Double-1>", callback)

    def _sort_by(self, column: str):
        """Sort rows by a column (toggle ascending/descending)."""
        if self._sort_column == column:
            self._sort_reverse = not self._sort_reverse
        else:
            self._sort_column = column
            self._sort_reverse = False

        items = [(self.tree.set(k, column), k) for k in self.tree.get_children()]

        # Try numeric sort, fall back to string
        try:
            items.sort(key=lambda t: float(t[0]), reverse=self._sort_reverse)
        except ValueError:
            items.sort(key=lambda t: t[0].lower(), reverse=self._sort_reverse)

        for index, (_, k) in enumerate(items):
            self.tree.move(k, "", index)
