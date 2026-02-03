"""
Chemical Equipment Parameter Visualizer — Desktop (PyQt5 + Matplotlib).
"""
import sys
import os
from pathlib import Path

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QFileDialog,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QComboBox,
    QGroupBox,
    QFormLayout,
    QTabWidget,
    QScrollArea,
    QFrame,
    QDialog,
    QDialogButtonBox,
    QGridLayout,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from api_client import EquipmentAPIClient, DEFAULT_BASE


class AuthDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Basic Authentication")
        layout = QFormLayout(self)
        self.user_edit = QLineEdit(self)
        self.user_edit.setPlaceholderText("Username")
        self.pass_edit = QLineEdit(self)
        self.pass_edit.setPlaceholderText("Password")
        self.pass_edit.setEchoMode(QLineEdit.Password)
        layout.addRow("Username:", self.user_edit)
        layout.addRow("Password:", self.pass_edit)
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addRow(btns)

    def get_credentials(self):
        return self.user_edit.text().strip(), self.pass_edit.text()


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.setParent(parent)

    def plot_doughnut(self, type_distribution: dict):
        self.fig.clear()
        if not type_distribution:
            ax = self.fig.add_subplot(111)
            ax.text(0.5, 0.5, "No type distribution", ha="center", va="center")
            self.draw()
            return
        ax = self.fig.add_subplot(111)
        labels = list(type_distribution.keys())
        sizes = list(type_distribution.values())
        colors = ["#38bdf8", "#34d399", "#fbbf24", "#f87171", "#a78bfa"][: len(labels)]
        wedges, _ = ax.pie(sizes, labels=labels, autopct="%1.1f%%", colors=colors, startangle=90)
        ax.axis("equal")
        self.draw()

    def plot_bars(self, raw_rows: list, max_items=15):
        self.fig.clear()
        if not raw_rows:
            ax = self.fig.add_subplot(111)
            ax.text(0.5, 0.5, "No data", ha="center", va="center")
            self.draw()
            return
        rows = raw_rows[:max_items]
        names = [r.get("Equipment Name", f"#{i+1}") for i, r in enumerate(rows)]
        flow = [ r.get("Flowrate") if r.get("Flowrate") is not None else 0 for r in rows ]
        press = [ r.get("Pressure") if r.get("Pressure") is not None else 0 for r in rows ]
        temp = [ r.get("Temperature") if r.get("Temperature") is not None else 0 for r in rows ]
        x = range(len(names))
        w = 0.25
        ax = self.fig.add_subplot(111)
        ax.bar([i - w for i in x], flow, w, label="Flowrate", color="#38bdf8")
        ax.bar(x, press, w, label="Pressure", color="#34d399")
        ax.bar([i + w for i in x], temp, w, label="Temperature", color="#fbbf24")
        ax.set_xticks(x)
        ax.set_xticklabels(names, rotation=45, ha="right")
        ax.legend()
        ax.set_ylabel("Value")
        self.fig.tight_layout()
        self.draw()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chemical Equipment Parameter Visualizer (Desktop)")
        self.resize(1000, 750)
        self.client = EquipmentAPIClient(DEFAULT_BASE)
        self.history = []
        self.selected = None
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Top: upload + auth
        top = QHBoxLayout()
        self.upload_btn = QPushButton("Upload CSV")
        self.upload_btn.clicked.connect(self._on_upload)
        self.auth_btn = QPushButton("Basic Auth")
        self.auth_btn.clicked.connect(self._on_auth)
        top.addWidget(self.upload_btn)
        top.addWidget(self.auth_btn)
        top.addStretch()
        layout.addLayout(top)

        # History combo
        hist_layout = QHBoxLayout()
        hist_layout.addWidget(QLabel("History (last 5):"))
        self.history_combo = QComboBox()
        self.history_combo.currentIndexChanged.connect(self._on_history_selected)
        hist_layout.addWidget(self.history_combo, 1)
        layout.addLayout(hist_layout)

        # Tabs: Summary, Charts, Table
        self.tabs = QTabWidget()
        # Summary
        summary_w = QWidget()
        summary_layout = QVBoxLayout(summary_w)
        self.summary_group = QGroupBox("Summary")
        fl = QFormLayout(self.summary_group)
        self.summary_count = QLabel("—")
        self.summary_flow = QLabel("—")
        self.summary_pressure = QLabel("—")
        self.summary_temp = QLabel("—")
        fl.addRow("Total count:", self.summary_count)
        fl.addRow("Avg Flowrate:", self.summary_flow)
        fl.addRow("Avg Pressure:", self.summary_pressure)
        fl.addRow("Avg Temperature:", self.summary_temp)
        summary_layout.addWidget(self.summary_group)
        self.pdf_btn = QPushButton("Download PDF report")
        self.pdf_btn.clicked.connect(self._on_download_pdf)
        self.pdf_btn.setEnabled(False)
        summary_layout.addWidget(self.pdf_btn)
        self.tabs.addTab(summary_w, "Summary")

        # Charts
        charts_w = QWidget()
        charts_layout = QVBoxLayout(charts_w)
        self.doughnut_canvas = MplCanvas(self, width=5, height=4)
        charts_layout.addWidget(self.doughnut_canvas)
        self.bar_canvas = MplCanvas(self, width=6, height=4)
        charts_layout.addWidget(self.bar_canvas)
        self.tabs.addTab(charts_w, "Charts")

        # Table
        self.table = QTableWidget()
        self.tabs.addTab(self.table, "Data table")

        layout.addWidget(self.tabs)
        self._load_history()

    def _on_auth(self):
        d = AuthDialog(self)
        if d.exec_() == QDialog.Accepted:
            u, p = d.get_credentials()
            if u or p:
                self.client = EquipmentAPIClient(DEFAULT_BASE, u, p)
                self.auth_btn.setText(f"Auth: {u}")
            self._load_history()

    def _on_upload(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select CSV", "", "CSV (*.csv)")
        if not path:
            return
        try:
            name = Path(path).stem
            data = self.client.upload_csv(path, name)
            self.history.insert(0, data)
            self.history = self.history[:5]
            self._refresh_history_combo()
            self.history_combo.setCurrentIndex(0)
            self._set_selected(data)
            QMessageBox.information(self, "Upload", "File uploaded successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Upload error", str(e))

    def _load_history(self):
        try:
            self.history = self.client.get_history()
            self._refresh_history_combo()
            if self.history:
                self.history_combo.setCurrentIndex(0)
                self._set_selected(self.history[0])
            else:
                self._set_selected(None)
        except Exception as e:
            self.history = []
            self._refresh_history_combo()
            self._set_selected(None)
            QMessageBox.warning(self, "API", f"Could not load history: {e}")

    def _refresh_history_combo(self):
        self.history_combo.blockSignals(True)
        self.history_combo.clear()
        for item in self.history:
            self.history_combo.addItem(f"{item.get('name', '—')} — {item.get('total_count', 0)} rows", item)
        self.history_combo.blockSignals(False)

    def _on_history_selected(self, index):
        if index < 0 or index >= len(self.history):
            return
        self._set_selected(self.history[index])

    def _set_selected(self, data):
        self.selected = data
        self.pdf_btn.setEnabled(data is not None)
        if not data:
            self.summary_count.setText("—")
            self.summary_flow.setText("—")
            self.summary_pressure.setText("—")
            self.summary_temp.setText("—")
            self.doughnut_canvas.plot_doughnut({})
            self.bar_canvas.plot_bars([])
            self.table.setRowCount(0)
            self.table.setColumnCount(0)
            return
        self.summary_count.setText(str(data.get("total_count", "—")))
        self.summary_flow.setText(str(data.get("avg_flowrate")) if data.get("avg_flowrate") is not None else "—")
        self.summary_pressure.setText(str(data.get("avg_pressure")) if data.get("avg_pressure") is not None else "—")
        self.summary_temp.setText(str(data.get("avg_temperature")) if data.get("avg_temperature") is not None else "—")
        self.doughnut_canvas.plot_doughnut(data.get("type_distribution") or {})
        self.bar_canvas.plot_bars(data.get("raw_rows") or [])
        rows = data.get("raw_rows") or []
        if rows:
            headers = list(rows[0].keys())
            self.table.setColumnCount(len(headers))
            self.table.setHorizontalHeaderLabels(headers)
            self.table.setRowCount(len(rows))
            for i, row in enumerate(rows):
                for j, h in enumerate(headers):
                    v = row.get(h)
                    self.table.setItem(i, j, QTableWidgetItem(str(v) if v is not None else "—"))
        else:
            self.table.setRowCount(0)
            self.table.setColumnCount(0)

    def _on_download_pdf(self):
        if not self.selected:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Save PDF", f"equipment_report_{self.selected['id']}.pdf", "PDF (*.pdf)"
        )
        if not path:
            return
        try:
            self.client.download_pdf(self.selected["id"], path)
            QMessageBox.information(self, "PDF", f"Saved to {path}")
        except Exception as e:
            QMessageBox.critical(self, "PDF error", str(e))


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
