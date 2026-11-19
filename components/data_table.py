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

    def __init__(self, master, columns: list, height=15, page_size=10, **kwargs):
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
        self.page_size = page_size
        self._rows = []
        self._page = 0

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

        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", padx=10, pady=(0, 8))
        self.page_label = ctk.CTkLabel(
            footer, text="No records", font=ctk.CTkFont(size=11),
            text_color=COLORS["text_muted"],
        )
        self.page_label.pack(side="left")
        self.previous_button = ctk.CTkButton(
            footer, text="‹", width=32, height=26, corner_radius=8,
            fg_color=COLORS["secondary"], hover_color=COLORS["surface_hover"],
            command=self.previous_page,
        )
        self.previous_button.pack(side="right", padx=(4, 0))
        self.next_button = ctk.CTkButton(
            footer, text="›", width=32, height=26, corner_radius=8,
            fg_color=COLORS["secondary"], hover_color=COLORS["surface_hover"],
            command=self.next_page,
        )
        self.next_button.pack(side="right")

        self.empty_label = ctk.CTkLabel(
            tree_frame,
            text="No records match the current filters.",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS["text_muted"],
        )

        # Tags for alternating subtle zebra stripes
        self.tree.tag_configure("evenrow", background="#111827")
        self.tree.tag_configure("oddrow", background="#151f30")

        self._sort_column = None
        self._sort_reverse = False

    def insert_rows(self, rows: list):
        """Replace the table data and render the first page."""
        self._rows = list(rows)
        self._page = 0
        self._render_page()

    def _render_page(self):
        """Render the current page and update paging controls."""
        self.clear()
        page_count = max(1, (len(self._rows) + self.page_size - 1) // self.page_size)
        self._page = min(self._page, page_count - 1)
        start = self._page * self.page_size
        for idx, row in enumerate(self._rows[start:start + self.page_size]):
            tag = "evenrow" if idx % 2 == 0 else "oddrow"
            self.tree.insert("", "end", values=row, tags=(tag,))
        if self._rows:
            self.empty_label.place_forget()
            self.page_label.configure(
                text=f"{start + 1}–{min(start + self.page_size, len(self._rows))} of {len(self._rows)}"
            )
        else:
            self.empty_label.place(relx=0.5, rely=0.5, anchor="center")
            self.page_label.configure(text="No records")
        self.previous_button.configure(state="normal" if self._page > 0 else "disabled")
        self.next_button.configure(
            state="normal" if self._page < page_count - 1 else "disabled"
        )

    def clear(self):
        """Remove all rows."""
        for item in self.tree.get_children():
            self.tree.delete(item)

    def previous_page(self):
        """Show the previous page of records."""
        if self._page > 0:
            self._page -= 1
            self._render_page()

    def next_page(self):
        """Show the next page of records."""
        if (self._page + 1) * self.page_size < len(self._rows):
            self._page += 1
            self._render_page()

    def get_selected_row(self):
        """Get the values of the selected row, or None."""
        selection = self.tree.selection()
        if not selection:
            return None
        return self.tree.item(selection[0])["values"]

    def get_all_rows(self) -> list:
        """Get all rows as a list of tuples."""
        return list(self._rows)

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

        column_index = self.column_names.index(column)
        items = [(row[column_index], row) for row in self._rows]

        try:
            items.sort(key=lambda t: float(t[0]), reverse=self._sort_reverse)
        except (ValueError, TypeError):
            items.sort(key=lambda t: str(t[0]).lower(), reverse=self._sort_reverse)

        self._rows = [values for _, values in items]
        self._page = 0
        self._render_page()
