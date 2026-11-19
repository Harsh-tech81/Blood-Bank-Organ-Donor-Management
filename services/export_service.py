"""
Export service — CSV export for any module's data.
"""

import csv
import os
from tkinter import filedialog
from models.activity_log_model import log_action


def export_to_csv(data, default_filename="export.csv"):
    """
    Export a list of dicts to a CSV file.
    Opens a file dialog for the user to choose where to save.
    Returns (success, filepath_or_message).
    """
    if not data:
        return False, "No data to export."

    # Get column headers from the first row
    headers = list(data[0].keys())

    # Ask user where to save
    filepath = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
        initialfile=default_filename,
        title="Export to CSV",
    )

    if not filepath:
        return False, "Export cancelled."

    try:
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data)

        log_action("Exported data to CSV", "reports",
                   f"File: {os.path.basename(filepath)}, Rows: {len(data)}")
        return True, f"Data exported to {filepath}"
    except Exception as e:
        return False, f"Export failed: {str(e)}"
