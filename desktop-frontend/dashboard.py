"""
Dashboard Window
Professional PyQt5 dashboard with colorful cards, View Results, and Clear History.
"""
import os
import requests
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QFrame, QTableWidget, QTableWidgetItem,
    QHeaderView, QScrollArea, QSizePolicy, QMessageBox,
    QSpacerItem, QApplication
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPalette

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from api import api


def format_to_ist(iso_string: str) -> str:
    """Convert ISO timestamp to Indian Standard Time (IST) format."""
    try:
        # Parse ISO format
        dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
        # Convert to IST (UTC+5:30)
        from datetime import timezone, timedelta
        ist = timezone(timedelta(hours=5, minutes=30))
        dt_ist = dt.astimezone(ist)
        return dt_ist.strftime("%d %b %Y, %I:%M %p")
    except Exception:
        return iso_string


class ResponsiveCanvas(FigureCanvas):
    """Matplotlib canvas that resizes properly with layouts."""

    def __init__(self, parent=None):
        self.fig = Figure(facecolor='#f8fafc', tight_layout=True)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(200, 180)


class ColorfulSummaryCard(QFrame):
    """Colorful summary card with icon, value, and unit."""

    def __init__(self, icon: str, title: str, value: str, unit: str, 
                 bg_gradient: tuple, value_color: str):
        super().__init__()
        self.setObjectName("colorfulCard")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        # Store colors for styling
        self.bg_start, self.bg_end = bg_gradient
        self.accent_color = value_color
        
        self._apply_card_style()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignCenter)

        # Icon
        self.icon_label = QLabel(icon)
        self.icon_label.setFont(QFont("Segoe UI Emoji", 24))
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setStyleSheet("background: transparent;")
        layout.addWidget(self.icon_label)

        # Title
        self.title_label = QLabel(title.upper())
        self.title_label.setFont(QFont("Segoe UI", 8, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("color: #64748b; background: transparent; letter-spacing: 1px;")
        layout.addWidget(self.title_label)

        # Value
        self.value_label = QLabel(value)
        self.value_label.setFont(QFont("Segoe UI", 26, QFont.Bold))
        self.value_label.setAlignment(Qt.AlignCenter)
        self.value_label.setStyleSheet(f"color: {value_color}; background: transparent;")
        layout.addWidget(self.value_label)

        # Unit
        self.unit_label = QLabel(unit)
        self.unit_label.setFont(QFont("Segoe UI", 9, QFont.DemiBold))
        self.unit_label.setAlignment(Qt.AlignCenter)
        self.unit_label.setStyleSheet("color: #94a3b8; background: transparent;")
        layout.addWidget(self.unit_label)

    def _apply_card_style(self):
        self.setStyleSheet(f"""
            #colorfulCard {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {self.bg_start}, stop:1 {self.bg_end}
                );
                border-radius: 16px;
                border-top: 4px solid {self.accent_color};
            }}
            #colorfulCard:hover {{
                border-top: 4px solid {self.accent_color};
            }}
        """)

    def set_value(self, value: str):
        """Update the card value."""
        self.value_label.setText(value)


class DashboardWindow(QWidget):
    """Main dashboard with professional theme."""

    logout_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.summary_data = None
        self.show_results = False  # Toggle for showing results
        self.history_data = []
        self._setup_window()
        self._build_ui()
        self._apply_styles()
        self._load_initial_data()

    def _setup_window(self):
        """Configure window properties."""
        self.setWindowTitle("Chemical Equipment Visualizer - Dashboard")
        self.setMinimumSize(1000, 700)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def _build_ui(self):
        """Build the dashboard UI with proper layouts."""
        # Root layout
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Header bar
        root.addWidget(self._build_header())

        # Scrollable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        content = QWidget()
        content.setObjectName("contentArea")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(24, 24, 24, 24)
        content_layout.setSpacing(20)

        # Upload section
        content_layout.addWidget(self._build_upload_section())

        # Summary cards row (hidden initially)
        self.summary_section = self._build_summary_section()
        self.summary_section.setVisible(False)
        content_layout.addWidget(self.summary_section)

        # Charts section (hidden initially)
        self.charts_section = self._build_charts_section()
        self.charts_section.setVisible(False)
        content_layout.addWidget(self.charts_section, stretch=1)

        # History table
        content_layout.addWidget(self._build_history_section())

        # Footer spacer
        content_layout.addStretch()

        scroll.setWidget(content)
        root.addWidget(scroll, stretch=1)

        # Footer
        root.addWidget(self._build_footer())

    def _build_header(self) -> QFrame:
        """Build the professional header bar."""
        header = QFrame()
        header.setObjectName("headerFrame")
        header.setFixedHeight(80)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(24, 0, 24, 0)
        layout.setSpacing(16)

        # Logo + Title
        logo = QLabel("🧪")
        logo.setFont(QFont("Segoe UI Emoji", 24))
        logo.setStyleSheet("background: transparent;")
        layout.addWidget(logo)

        title_container = QVBoxLayout()
        title_container.setSpacing(2)

        title = QLabel("Chemical Equipment Visualizer")
        title.setObjectName("headerTitle")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_container.addWidget(title)

        subtitle = QLabel("Upload CSV files and visualize equipment data")
        subtitle.setObjectName("headerSubtitle")
        subtitle.setFont(QFont("Segoe UI", 9))
        title_container.addWidget(subtitle)

        layout.addLayout(title_container)
        layout.addStretch()

        # Logout button
        self.logout_btn = QPushButton("🚪 Logout")
        self.logout_btn.setObjectName("logoutBtn")
        self.logout_btn.setFont(QFont("Segoe UI", 10, QFont.DemiBold))
        self.logout_btn.setCursor(Qt.PointingHandCursor)
        self.logout_btn.clicked.connect(self._handle_logout)
        layout.addWidget(self.logout_btn)

        return header

    def _build_upload_section(self) -> QFrame:
        """Build file upload section with all action buttons."""
        section = QFrame()
        section.setObjectName("section")

        layout = QVBoxLayout(section)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        title = QLabel("📤 Upload CSV File")
        title.setObjectName("sectionTitle")
        title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        layout.addWidget(title)

        # Buttons row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        # Upload button
        self.upload_btn = QPushButton("🚀 Upload CSV")
        self.upload_btn.setObjectName("uploadBtn")
        self.upload_btn.setFont(QFont("Segoe UI", 10, QFont.DemiBold))
        self.upload_btn.setCursor(Qt.PointingHandCursor)
        self.upload_btn.setMinimumWidth(140)
        self.upload_btn.clicked.connect(self._upload_csv)
        btn_row.addWidget(self.upload_btn)

        # View Results button
        self.view_btn = QPushButton("👁️ View Results")
        self.view_btn.setObjectName("viewBtn")
        self.view_btn.setFont(QFont("Segoe UI", 10, QFont.DemiBold))
        self.view_btn.setCursor(Qt.PointingHandCursor)
        self.view_btn.setMinimumWidth(140)
        self.view_btn.clicked.connect(self._toggle_results)
        self.view_btn.setEnabled(False)
        btn_row.addWidget(self.view_btn)

        # Export PDF button
        self.export_pdf_btn = QPushButton("📄 Download PDF")
        self.export_pdf_btn.setObjectName("exportPdfBtn")
        self.export_pdf_btn.setFont(QFont("Segoe UI", 10, QFont.DemiBold))
        self.export_pdf_btn.setCursor(Qt.PointingHandCursor)
        self.export_pdf_btn.setMinimumWidth(140)
        self.export_pdf_btn.clicked.connect(self._download_pdf)
        self.export_pdf_btn.setEnabled(False)
        btn_row.addWidget(self.export_pdf_btn)

        btn_row.addStretch()

        # Status label
        self.upload_status = QLabel("")
        self.upload_status.setFont(QFont("Segoe UI", 10))
        self.upload_status.setWordWrap(True)
        btn_row.addWidget(self.upload_status)

        layout.addLayout(btn_row)

        # Hint
        hint = QLabel("ℹ️ Required columns: Equipment Name, Type, Flowrate, Pressure, Temperature")
        hint.setObjectName("hintLabel")
        hint.setFont(QFont("Segoe UI", 9))
        layout.addWidget(hint)

        return section

    def _build_summary_section(self) -> QFrame:
        """Build colorful summary cards section."""
        section = QFrame()
        section.setObjectName("section")

        layout = QVBoxLayout(section)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        title = QLabel("📊 Summary Dashboard")
        title.setObjectName("sectionTitle")
        title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        layout.addWidget(title)

        # Colorful cards row
        cards_row = QHBoxLayout()
        cards_row.setSpacing(16)

        # Card 1: Total Records - Purple
        self.card_total = ColorfulSummaryCard(
            icon="📋", title="Total Records", value="—", unit="",
            bg_gradient=("#f5f3ff", "#ede9fe"), value_color="#7c3aed"
        )
        cards_row.addWidget(self.card_total)

        # Card 2: Avg Flowrate - Blue
        self.card_flowrate = ColorfulSummaryCard(
            icon="💧", title="Avg Flowrate", value="—", unit="m³/h",
            bg_gradient=("#eff6ff", "#dbeafe"), value_color="#2563eb"
        )
        cards_row.addWidget(self.card_flowrate)

        # Card 3: Avg Pressure - Amber
        self.card_pressure = ColorfulSummaryCard(
            icon="⚡", title="Avg Pressure", value="—", unit="bar",
            bg_gradient=("#fffbeb", "#fef3c7"), value_color="#d97706"
        )
        cards_row.addWidget(self.card_pressure)

        # Card 4: Avg Temperature - Green
        self.card_temperature = ColorfulSummaryCard(
            icon="🌡️", title="Avg Temperature", value="—", unit="°C",
            bg_gradient=("#ecfdf5", "#d1fae5"), value_color="#059669"
        )
        cards_row.addWidget(self.card_temperature)

        layout.addLayout(cards_row)

        return section

    def _build_charts_section(self) -> QFrame:
        """Build charts section with responsive canvases."""
        section = QFrame()
        section.setObjectName("section")
        section.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layout = QVBoxLayout(section)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        title = QLabel("📈 Data Visualization")
        title.setObjectName("sectionTitle")
        title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        layout.addWidget(title)

        charts_row = QHBoxLayout()
        charts_row.setSpacing(20)

        # Bar chart container
        bar_container = QFrame()
        bar_container.setObjectName("chartContainer")
        bar_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        bar_layout = QVBoxLayout(bar_container)
        bar_layout.setContentsMargins(16, 16, 16, 16)
        bar_layout.setSpacing(10)

        bar_title = QLabel("Average Values Comparison")
        bar_title.setAlignment(Qt.AlignCenter)
        bar_title.setFont(QFont("Segoe UI", 10, QFont.DemiBold))
        bar_title.setStyleSheet("color: #475569; background: transparent;")
        bar_layout.addWidget(bar_title)

        self.bar_chart = ResponsiveCanvas(self)
        bar_layout.addWidget(self.bar_chart, stretch=1)

        charts_row.addWidget(bar_container)

        # Pie chart container
        pie_container = QFrame()
        pie_container.setObjectName("chartContainer")
        pie_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        pie_layout = QVBoxLayout(pie_container)
        pie_layout.setContentsMargins(16, 16, 16, 16)
        pie_layout.setSpacing(10)

        pie_title = QLabel("Equipment Type Distribution")
        pie_title.setAlignment(Qt.AlignCenter)
        pie_title.setFont(QFont("Segoe UI", 10, QFont.DemiBold))
        pie_title.setStyleSheet("color: #475569; background: transparent;")
        pie_layout.addWidget(pie_title)

        self.pie_chart = ResponsiveCanvas(self)
        pie_layout.addWidget(self.pie_chart, stretch=1)

        charts_row.addWidget(pie_container)

        layout.addLayout(charts_row, stretch=1)

        return section

    def _build_history_section(self) -> QFrame:
        """Build upload history table section with clear button."""
        section = QFrame()
        section.setObjectName("section")

        layout = QVBoxLayout(section)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        # Header row with title and clear button
        header_row = QHBoxLayout()

        title = QLabel("📁 Upload History")
        title.setObjectName("sectionTitle")
        title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        header_row.addWidget(title)

        header_row.addStretch()

        # Clear History button
        self.clear_history_btn = QPushButton("🗑️ Clear History")
        self.clear_history_btn.setObjectName("clearHistoryBtn")
        self.clear_history_btn.setFont(QFont("Segoe UI", 9, QFont.DemiBold))
        self.clear_history_btn.setCursor(Qt.PointingHandCursor)
        self.clear_history_btn.clicked.connect(self._clear_history)
        self.clear_history_btn.setVisible(False)
        header_row.addWidget(self.clear_history_btn)

        layout.addLayout(header_row)

        # Table
        self.history_table = QTableWidget()
        self.history_table.setObjectName("historyTable")
        self.history_table.setColumnCount(3)
        self.history_table.setHorizontalHeaderLabels(["#", "Filename", "Uploaded At"])
        self.history_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.history_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.history_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.history_table.setColumnWidth(0, 50)
        self.history_table.setAlternatingRowColors(True)
        self.history_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.history_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.history_table.verticalHeader().setVisible(False)
        self.history_table.setMinimumHeight(120)
        self.history_table.setMaximumHeight(200)
        self.history_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(self.history_table)

        # No data message
        self.no_history_label = QLabel("No uploads yet. Upload a CSV file to get started.")
        self.no_history_label.setObjectName("noDataLabel")
        self.no_history_label.setFont(QFont("Segoe UI", 10))
        self.no_history_label.setAlignment(Qt.AlignCenter)
        self.no_history_label.setVisible(False)
        layout.addWidget(self.no_history_label)

        return section

    def _build_footer(self) -> QFrame:
        """Build footer."""
        footer = QFrame()
        footer.setObjectName("footerFrame")
        footer.setFixedHeight(50)

        layout = QHBoxLayout(footer)
        layout.setContentsMargins(24, 0, 24, 0)

        text = QLabel("Chemical Equipment Visualizer © 2026")
        text.setFont(QFont("Segoe UI", 9))
        text.setAlignment(Qt.AlignCenter)
        text.setStyleSheet("color: rgba(255, 255, 255, 0.85); background: transparent;")
        layout.addWidget(text)

        return footer

    def _apply_styles(self):
        """Apply professional stylesheet."""
        self.setStyleSheet("""
            QWidget {
                background-color: #f8fafc;
                color: #1e293b;
            }
            #headerFrame {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1e3a5f, stop:0.5 #2d5a87, stop:1 #3b82f6
                );
            }
            #headerTitle {
                color: white;
                background: transparent;
            }
            #headerSubtitle {
                color: rgba(255, 255, 255, 0.8);
                background: transparent;
            }
            #logoutBtn {
                background: rgba(255, 255, 255, 0.15);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 8px;
                padding: 10px 20px;
            }
            #logoutBtn:hover {
                background: rgba(255, 255, 255, 0.25);
                border-color: rgba(255, 255, 255, 0.5);
            }
            #contentArea {
                background-color: #f8fafc;
            }
            #section {
                background-color: white;
                border-radius: 16px;
                border: 1px solid #e2e8f0;
            }
            #section:hover {
                border-color: #cbd5e1;
            }
            #sectionTitle {
                color: #1e293b;
                background: transparent;
            }
            #hintLabel {
                color: #94a3b8;
                background: transparent;
            }
            #uploadBtn {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6366f1, stop:1 #8b5cf6
                );
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px 24px;
            }
            #uploadBtn:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4f46e5, stop:1 #7c3aed
                );
            }
            #uploadBtn:disabled {
                background: #e2e8f0;
                color: #94a3b8;
            }
            #viewBtn {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3b82f6, stop:1 #60a5fa
                );
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px 24px;
            }
            #viewBtn:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2563eb, stop:1 #3b82f6
                );
            }
            #viewBtn:disabled {
                background: #e2e8f0;
                color: #94a3b8;
            }
            #exportPdfBtn {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #10b981, stop:1 #34d399
                );
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px 24px;
            }
            #exportPdfBtn:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #059669, stop:1 #10b981
                );
            }
            #exportPdfBtn:disabled {
                background: #e2e8f0;
                color: #94a3b8;
            }
            #clearHistoryBtn {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ef4444, stop:1 #f87171
                );
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
            }
            #clearHistoryBtn:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #dc2626, stop:1 #ef4444
                );
            }
            #chartContainer {
                background-color: #f8fafc;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
            }
            #historyTable {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                gridline-color: #f1f5f9;
            }
            #historyTable::item {
                padding: 8px;
                color: #475569;
            }
            #historyTable::item:selected {
                background-color: #eff6ff;
                color: #1e293b;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                padding: 10px;
                border: none;
                border-bottom: 1px solid #e2e8f0;
                font-weight: 600;
                color: #64748b;
                text-transform: uppercase;
                font-size: 11px;
            }
            #noDataLabel {
                color: #94a3b8;
                background: #f8fafc;
                padding: 30px;
                border-radius: 8px;
            }
            #footerFrame {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1e3a5f, stop:1 #2d5a87
                );
            }
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: #f1f5f9;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #cbd5e1;
                border-radius: 5px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #94a3b8;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
            }
        """)

    def _load_initial_data(self):
        """Load only history on initial load (don't show results yet)."""
        self._fetch_summary_silent()
        self._fetch_history()

    def _fetch_summary_silent(self):
        """Fetch summary from API without showing results."""
        try:
            response = api.get("/api/summary/")
            if response.status_code == 200:
                self.summary_data = response.json()
                self.view_btn.setEnabled(True)
                self.export_pdf_btn.setEnabled(True)
            elif response.status_code == 401:
                self._handle_auth_error()
        except Exception:
            pass

    def _fetch_history(self):
        """Fetch history from API."""
        try:
            response = api.get("/api/history/")
            if response.status_code == 200:
                data = response.json()
                self.history_data = data.get("datasets", [])
                self._update_history(self.history_data)
            elif response.status_code == 401:
                self._handle_auth_error()
        except Exception:
            pass

    def _toggle_results(self):
        """Toggle visibility of summary and charts sections."""
        if not self.summary_data:
            return

        self.show_results = not self.show_results
        
        if self.show_results:
            self._update_cards(self.summary_data)
            self._draw_charts(self.summary_data)
            self.summary_section.setVisible(True)
            self.charts_section.setVisible(True)
            self.view_btn.setText("🙈 Hide Results")
        else:
            self.summary_section.setVisible(False)
            self.charts_section.setVisible(False)
            self.view_btn.setText("👁️ View Results")

    def _update_cards(self, data: dict):
        """Update summary cards with data."""
        self.card_total.set_value(str(data.get("total_rows", "—")))

        averages = data.get("averages", {})
        self.card_flowrate.set_value(str(averages.get("flowrate", "—")))
        self.card_pressure.set_value(str(averages.get("pressure", "—")))
        self.card_temperature.set_value(str(averages.get("temperature", "—")))

    def _update_history(self, data: list):
        """Update history table."""
        if not data:
            self.history_table.setRowCount(0)
            self.history_table.setVisible(False)
            self.no_history_label.setVisible(True)
            self.clear_history_btn.setVisible(False)
            return

        self.history_table.setVisible(True)
        self.no_history_label.setVisible(False)
        self.clear_history_btn.setVisible(True)

        self.history_table.setRowCount(len(data))
        for row, item in enumerate(data):
            self.history_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            file_name = item.get("file_name", "")
            if "/" in file_name or "\\" in file_name:
                file_name = os.path.basename(file_name)
            self.history_table.setItem(row, 1, QTableWidgetItem(file_name))
            # Format time to IST
            uploaded_at = format_to_ist(item.get("uploaded_at", ""))
            self.history_table.setItem(row, 2, QTableWidgetItem(uploaded_at))

    def _draw_charts(self, data: dict):
        """Draw bar and pie charts."""
        # Bar chart for averages
        averages = data.get("averages", {})
        if averages:
            labels = ["Flowrate", "Pressure", "Temperature"]
            values = [
                averages.get("flowrate", 0),
                averages.get("pressure", 0),
                averages.get("temperature", 0)
            ]
            colors = ['#3b82f6', '#f59e0b', '#10b981']

            self.bar_chart.axes.clear()
            bars = self.bar_chart.axes.bar(labels, values, color=colors, width=0.6)
            self.bar_chart.axes.set_ylabel("Average Value", fontsize=9, color='#64748b')
            self.bar_chart.axes.set_facecolor('#f8fafc')
            self.bar_chart.axes.tick_params(axis='x', labelsize=9, colors='#475569')
            self.bar_chart.axes.tick_params(axis='y', labelsize=8, colors='#94a3b8')
            for spine in self.bar_chart.axes.spines.values():
                spine.set_visible(False)
            self.bar_chart.axes.yaxis.grid(True, linestyle='--', alpha=0.3, color='#cbd5e1')
            self.bar_chart.fig.tight_layout()
            self.bar_chart.draw()

        # Pie chart for equipment types
        type_counts = data.get("equipment_type_counts", {})
        if type_counts:
            labels = list(type_counts.keys())
            values = list(type_counts.values())
            colors = ['#8b5cf6', '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#ec4899']

            self.pie_chart.axes.clear()
            wedges, texts, autotexts = self.pie_chart.axes.pie(
                values, labels=labels, colors=colors[:len(labels)],
                autopct='%1.0f%%', startangle=90, textprops={'fontsize': 9, 'color': '#475569'}
            )
            for autotext in autotexts:
                autotext.set_fontsize(8)
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            self.pie_chart.axes.set_facecolor('#f8fafc')
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
        self.upload_status.setText("⏳ Uploading...")
        self.upload_status.setStyleSheet("color: #64748b;")
        QApplication.processEvents()

        try:
            with open(file_path, "rb") as f:
                files = {"file": (os.path.basename(file_path), f, "text/csv")}
                response = api.post("/api/upload/", files=files)

            if response.status_code in [200, 201]:
                self.upload_status.setText("✅ Upload successful!")
                self.upload_status.setStyleSheet("color: #10b981;")
                self._fetch_summary_silent()
                self._fetch_history()
                # Auto-show results after upload
                if self.summary_data and not self.show_results:
                    self._toggle_results()
            elif response.status_code == 401:
                self._handle_auth_error()
            else:
                self.upload_status.setText(f"❌ Failed: {response.status_code}")
                self.upload_status.setStyleSheet("color: #ef4444;")
        except Exception as e:
            self.upload_status.setText(f"❌ Error: {str(e)}")
            self.upload_status.setStyleSheet("color: #ef4444;")
        finally:
            self.upload_btn.setEnabled(True)

    def _download_pdf(self):
        """Download PDF report from the API."""
        if not self.summary_data:
            QMessageBox.warning(
                self, "No Data",
                "Please upload data first before generating a PDF report."
            )
            return

        save_path, _ = QFileDialog.getSaveFileName(
            self, "Save PDF Report", "chemical_equipment_report.pdf",
            "PDF Files (*.pdf)"
        )
        if not save_path:
            return

        self.export_pdf_btn.setEnabled(False)
        self.export_pdf_btn.setText("⏳ Generating...")
        QApplication.processEvents()

        try:
            response = api.get("/api/report/")

            if response.status_code == 200:
                content_type = response.headers.get('Content-Type', '')
                if 'application/pdf' in content_type:
                    with open(save_path, "wb") as f:
                        f.write(response.content)
                    QMessageBox.information(
                        self, "Success",
                        f"PDF report saved to:\n{save_path}"
                    )
                else:
                    try:
                        error_data = response.json()
                        error_msg = error_data.get('error', 'Unknown error')
                    except Exception:
                        error_msg = 'Server returned invalid response'
                    QMessageBox.warning(
                        self, "Failed",
                        f"Failed to generate PDF:\n{error_msg}"
                    )
            elif response.status_code == 401:
                self._handle_auth_error()
            elif response.status_code == 404:
                QMessageBox.warning(
                    self, "No Data",
                    "No data found. Please upload a CSV file first."
                )
            else:
                QMessageBox.warning(
                    self, "Failed",
                    f"Failed to generate PDF: {response.status_code}"
                )
        except requests.exceptions.ConnectionError:
            QMessageBox.critical(
                self, "Connection Error",
                "Cannot connect to server.\nPlease ensure the backend is running."
            )
        except requests.exceptions.Timeout:
            QMessageBox.critical(
                self, "Timeout",
                "Request timed out.\nPlease try again."
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Error",
                f"Error downloading PDF:\n{str(e)}"
            )
        finally:
            self.export_pdf_btn.setEnabled(True)
            self.export_pdf_btn.setText("📄 Download PDF")

    def _clear_history(self):
        """Clear all upload history."""
        reply = QMessageBox.question(
            self, "Clear History",
            "Are you sure you want to clear all upload history?\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        self.clear_history_btn.setEnabled(False)
        self.clear_history_btn.setText("⏳ Clearing...")
        QApplication.processEvents()

        try:
            response = api.delete("/api/history/")

            if response.status_code == 200:
                self.history_data = []
                self._update_history([])
                self.summary_data = None
                self.show_results = False
                self.summary_section.setVisible(False)
                self.charts_section.setVisible(False)
                self.view_btn.setText("👁️ View Results")
                self.view_btn.setEnabled(False)
                self.export_pdf_btn.setEnabled(False)
                self.upload_status.setText("✅ History cleared!")
                self.upload_status.setStyleSheet("color: #10b981;")
            elif response.status_code == 401:
                self._handle_auth_error()
            else:
                QMessageBox.warning(
                    self, "Failed",
                    f"Failed to clear history: {response.status_code}"
                )
        except Exception as e:
            QMessageBox.critical(
                self, "Error",
                f"Error clearing history:\n{str(e)}"
            )
        finally:
            self.clear_history_btn.setEnabled(True)
            self.clear_history_btn.setText("🗑️ Clear History")

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
