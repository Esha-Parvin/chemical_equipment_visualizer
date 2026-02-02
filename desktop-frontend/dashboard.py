"""
Dashboard Window
Responsive PyQt5 dashboard with proper layouts for Windows high-DPI screens.
"""
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QFrame, QTableWidget, QTableWidgetItem,
    QHeaderView, QScrollArea, QSizePolicy, QMessageBox,
    QSpacerItem, QApplication
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from api import api


class ResponsiveCanvas(FigureCanvas):
    """Matplotlib canvas that resizes properly with layouts."""

    def __init__(self, parent=None):
        self.fig = Figure(facecolor='#fafafa', tight_layout=True)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(200, 180)


class SummaryCard(QFrame):
    """Reusable summary card widget with responsive layout."""

    def __init__(self, title: str, value: str, bg_color: str, text_color: str):
        super().__init__()
        self.setObjectName("summaryCard")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.setStyleSheet(f"""
            #summaryCard {{
                background-color: {bg_color};
                border-radius: 10px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        self.title_label = QLabel(title)
        self.title_label.setFont(QFont("Segoe UI", 10, QFont.DemiBold))
        self.title_label.setStyleSheet(f"color: {text_color}; background: transparent;")
        self.title_label.setWordWrap(True)
        layout.addWidget(self.title_label)

        self.value_label = QLabel(value)
        self.value_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        self.value_label.setStyleSheet(f"color: {text_color}; background: transparent;")
        self.value_label.setWordWrap(True)
        layout.addWidget(self.value_label)

        layout.addStretch()

    def set_value(self, value: str):
        """Update the card value."""
        self.value_label.setText(value)


class DashboardWindow(QWidget):
    """Main dashboard with fully responsive layout."""

    logout_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.summary_data = None
        self._setup_window()
        self._build_ui()
        self._apply_styles()
        self.load_data()

    def _setup_window(self):
        """Configure window properties."""
        self.setWindowTitle("Chemical Equipment Visualizer - Dashboard")
        self.setMinimumSize(900, 600)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def _build_ui(self):
        """Build the dashboard UI with proper layouts."""
        # Root layout
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        # Header bar
        root.addLayout(self._build_header())

        # Scrollable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 8, 0)
        content_layout.setSpacing(14)

        # Upload section
        content_layout.addWidget(self._build_upload_section())

        # Summary cards row
        content_layout.addWidget(self._build_summary_section())

        # Charts section (expandable)
        content_layout.addWidget(self._build_charts_section(), stretch=1)

        # History table
        content_layout.addWidget(self._build_history_section())

        scroll.setWidget(content)
        root.addWidget(scroll, stretch=1)

    def _build_header(self) -> QHBoxLayout:
        """Build the header bar with logo, title, logout."""
        header = QHBoxLayout()
        header.setSpacing(10)

        # Logo
        logo = QLabel("🧪")
        logo.setFont(QFont("Segoe UI Emoji", 20))
        header.addWidget(logo)

        # Title
        title = QLabel("Chemical Equipment Visualizer")
        title.setObjectName("headerTitle")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        header.addWidget(title)

        header.addStretch()

        # Logout button
        self.logout_btn = QPushButton("Logout")
        self.logout_btn.setObjectName("logoutBtn")
        self.logout_btn.setFont(QFont("Segoe UI", 10, QFont.DemiBold))
        self.logout_btn.setCursor(Qt.PointingHandCursor)
        self.logout_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.logout_btn.clicked.connect(self._handle_logout)
        header.addWidget(self.logout_btn)

        return header

    def _build_upload_section(self) -> QFrame:
        """Build file upload section."""
        section = QFrame()
        section.setObjectName("section")

        layout = QVBoxLayout(section)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(10)

        title = QLabel("📁 Upload CSV File")
        title.setObjectName("sectionTitle")
        title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        layout.addWidget(title)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        self.upload_btn = QPushButton("Choose File & Upload")
        self.upload_btn.setObjectName("uploadBtn")
        self.upload_btn.setFont(QFont("Segoe UI", 10, QFont.DemiBold))
        self.upload_btn.setCursor(Qt.PointingHandCursor)
        self.upload_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.upload_btn.clicked.connect(self._upload_csv)
        btn_row.addWidget(self.upload_btn)

        self.upload_status = QLabel("")
        self.upload_status.setFont(QFont("Segoe UI", 10))
        self.upload_status.setWordWrap(True)
        self.upload_status.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        btn_row.addWidget(self.upload_status, stretch=1)

        layout.addLayout(btn_row)

        return section

    def _build_summary_section(self) -> QFrame:
        """Build summary cards section."""
        section = QFrame()
        section.setObjectName("section")

        layout = QVBoxLayout(section)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(10)

        title = QLabel("📊 Data Summary")
        title.setObjectName("sectionTitle")
        title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        layout.addWidget(title)

        cards_row = QHBoxLayout()
        cards_row.setSpacing(12)

        self.card_total = SummaryCard("Total Rows", "—", "#e3f2fd", "#1565c0")
        cards_row.addWidget(self.card_total)

        self.card_capacity = SummaryCard("Avg Capacity", "—", "#f3e5f5", "#7b1fa2")
        cards_row.addWidget(self.card_capacity)

        self.card_pressure = SummaryCard("Avg Pressure", "—", "#e8f5e9", "#2e7d32")
        cards_row.addWidget(self.card_pressure)

        self.card_types = SummaryCard("Equipment Types", "—", "#fff3e0", "#ef6c00")
        cards_row.addWidget(self.card_types)

        layout.addLayout(cards_row)

        return section

    def _build_charts_section(self) -> QFrame:
        """Build charts section with responsive canvases."""
        section = QFrame()
        section.setObjectName("section")
        section.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layout = QVBoxLayout(section)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(10)

        title = QLabel("📈 Equipment Distribution")
        title.setObjectName("sectionTitle")
        title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        layout.addWidget(title)

        charts_row = QHBoxLayout()
        charts_row.setSpacing(14)

        # Bar chart container
        bar_container = QFrame()
        bar_container.setObjectName("chartContainer")
        bar_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        bar_layout = QVBoxLayout(bar_container)
        bar_layout.setContentsMargins(10, 10, 10, 10)
        bar_layout.setSpacing(6)

        bar_title = QLabel("Equipment Count by Type")
        bar_title.setAlignment(Qt.AlignCenter)
        bar_title.setFont(QFont("Segoe UI", 9, QFont.DemiBold))
        bar_title.setStyleSheet("color: #666; background: transparent;")
        bar_layout.addWidget(bar_title)

        self.bar_chart = ResponsiveCanvas(self)
        bar_layout.addWidget(self.bar_chart, stretch=1)

        charts_row.addWidget(bar_container)

        # Pie chart container
        pie_container = QFrame()
        pie_container.setObjectName("chartContainer")
        pie_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        pie_layout = QVBoxLayout(pie_container)
        pie_layout.setContentsMargins(10, 10, 10, 10)
        pie_layout.setSpacing(6)

        pie_title = QLabel("Type Distribution")
        pie_title.setAlignment(Qt.AlignCenter)
        pie_title.setFont(QFont("Segoe UI", 9, QFont.DemiBold))
        pie_title.setStyleSheet("color: #666; background: transparent;")
        pie_layout.addWidget(pie_title)

        self.pie_chart = ResponsiveCanvas(self)
        pie_layout.addWidget(self.pie_chart, stretch=1)

        charts_row.addWidget(pie_container)

        layout.addLayout(charts_row, stretch=1)

        return section

    def _build_history_section(self) -> QFrame:
        """Build upload history table section."""
        section = QFrame()
        section.setObjectName("section")

        layout = QVBoxLayout(section)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(10)

        title = QLabel("📜 Upload History")
        title.setObjectName("sectionTitle")
        title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        layout.addWidget(title)

        self.history_table = QTableWidget()
        self.history_table.setObjectName("historyTable")
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels(["ID", "Filename", "Uploaded At", "Row Count"])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.history_table.setAlternatingRowColors(True)
        self.history_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.history_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.history_table.verticalHeader().setVisible(False)
        self.history_table.setMinimumHeight(120)
        self.history_table.setMaximumHeight(200)
        self.history_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(self.history_table)

        return section

    def _apply_styles(self):
        """Apply stylesheet."""
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f7fa;
            }
            #headerTitle {
                color: #333;
            }
            #logoutBtn {
                background-color: #ef5350;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
            }
            #logoutBtn:hover {
                background-color: #e53935;
            }
            #logoutBtn:pressed {
                background-color: #c62828;
            }
            #section {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #e8e8e8;
            }
            #sectionTitle {
                color: #333;
            }
            #uploadBtn {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #7c4dff, stop:1 #448aff
                );
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 18px;
            }
            #uploadBtn:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #651fff, stop:1 #2979ff
                );
            }
            #chartContainer {
                background-color: #fafafa;
                border-radius: 8px;
                border: 1px solid #eee;
            }
            #historyTable {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                gridline-color: #f0f0f0;
            }
            #historyTable::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 8px;
                border: none;
                border-bottom: 1px solid #e0e0e0;
                font-weight: 600;
                color: #555;
            }
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: #f0f0f0;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                border-radius: 5px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a0a0a0;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
            }
        """)

    def load_data(self):
        """Load summary and history data."""
        self._fetch_summary()
        self._fetch_history()

    def _fetch_summary(self):
        """Fetch summary from API."""
        try:
            response = api.get("/api/summary/")
            if response.status_code == 200:
                data = response.json()
                self.summary_data = data
                self._update_cards(data)
                self._draw_charts(data)
            elif response.status_code == 401:
                self._handle_auth_error()
        except Exception as e:
            self.upload_status.setText(f"Error: {str(e)}")
            self.upload_status.setStyleSheet("color: #e53935;")

    def _fetch_history(self):
        """Fetch history from API."""
        try:
            response = api.get("/api/history/")
            if response.status_code == 200:
                self._update_history(response.json())
            elif response.status_code == 401:
                self._handle_auth_error()
        except Exception:
            pass

    def _update_cards(self, data: dict):
        """Update summary cards."""
        self.card_total.set_value(str(data.get("total_rows", "—")))

        avg_cap = data.get("average_capacity_liters")
        self.card_capacity.set_value(f"{avg_cap:.1f} L" if avg_cap else "—")

        avg_pres = data.get("average_max_pressure_bar")
        self.card_pressure.set_value(f"{avg_pres:.1f} bar" if avg_pres else "—")

        type_counts = data.get("equipment_type_counts", {})
        self.card_types.set_value(str(len(type_counts)))

    def _update_history(self, data: list):
        """Update history table."""
        self.history_table.setRowCount(len(data))
        for row, item in enumerate(data):
            self.history_table.setItem(row, 0, QTableWidgetItem(str(item.get("id", ""))))
            self.history_table.setItem(row, 1, QTableWidgetItem(item.get("filename", "")))
            self.history_table.setItem(row, 2, QTableWidgetItem(item.get("uploaded_at", "")))
            self.history_table.setItem(row, 3, QTableWidgetItem(str(item.get("row_count", ""))))

    def _draw_charts(self, data: dict):
        """Draw bar and pie charts."""
        type_counts = data.get("equipment_type_counts", {})
        if not type_counts:
            return

        labels = list(type_counts.keys())
        values = list(type_counts.values())
        colors = ['#7c4dff', '#448aff', '#00bcd4', '#4caf50', '#ff9800', '#f44336', '#9c27b0', '#795548']

        # Bar chart
        self.bar_chart.axes.clear()
        self.bar_chart.axes.bar(labels, values, color=colors[:len(labels)])
        self.bar_chart.axes.set_ylabel("Count", fontsize=9)
        self.bar_chart.axes.set_facecolor('#fafafa')
        self.bar_chart.axes.tick_params(axis='x', rotation=25, labelsize=8)
        self.bar_chart.axes.tick_params(axis='y', labelsize=8)
        for spine in self.bar_chart.axes.spines.values():
            spine.set_visible(False)
        self.bar_chart.axes.yaxis.grid(True, linestyle='--', alpha=0.4)
        self.bar_chart.fig.tight_layout()
        self.bar_chart.draw()

        # Pie chart
        self.pie_chart.axes.clear()
        wedges, texts, autotexts = self.pie_chart.axes.pie(
            values, labels=labels, colors=colors[:len(labels)],
            autopct='%1.0f%%', startangle=90, textprops={'fontsize': 8}
        )
        for autotext in autotexts:
            autotext.set_fontsize(7)
        self.pie_chart.axes.set_facecolor('#fafafa')
        self.pie_chart.fig.tight_layout()
        self.pie_chart.draw()

    def _upload_csv(self):
        """Handle CSV upload."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select CSV File", "", "CSV Files (*.csv)"
        )
        if not file_path:
            return

        self.upload_btn.setEnabled(False)
        self.upload_status.setText("Uploading...")
        self.upload_status.setStyleSheet("color: #666;")
        QApplication.processEvents()

        try:
            with open(file_path, "rb") as f:
                files = {"file": (os.path.basename(file_path), f, "text/csv")}
                response = api.post("/api/upload/", files=files)

            if response.status_code in [200, 201]:
                self.upload_status.setText("✅ Upload successful!")
                self.upload_status.setStyleSheet("color: #4caf50;")
                self.load_data()
            elif response.status_code == 401:
                self._handle_auth_error()
            else:
                self.upload_status.setText(f"❌ Failed: {response.status_code}")
                self.upload_status.setStyleSheet("color: #e53935;")
        except Exception as e:
            self.upload_status.setText(f"❌ Error: {str(e)}")
            self.upload_status.setStyleSheet("color: #e53935;")
        finally:
            self.upload_btn.setEnabled(True)

    def _handle_logout(self):
        """Handle logout."""
        reply = QMessageBox.question(
            self, "Logout",
            "Are you sure you want to logout?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            api.logout()
            self.logout_requested.emit()

    def _handle_auth_error(self):
        """Handle authentication error."""
        QMessageBox.warning(self, "Session Expired", "Please login again.")
        api.logout()
        self.logout_requested.emit()
