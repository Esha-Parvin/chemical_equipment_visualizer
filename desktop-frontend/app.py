import sys
import requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QFileDialog, QLabel, QMessageBox
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

API_BASE_URL = "http://127.0.0.1:8000/api"


class ChartCanvas(FigureCanvas):
    def __init__(self):
        self.fig = Figure(figsize=(5, 4))
        self.ax = self.fig.add_subplot(111)
        super().__init__(self.fig)


class DesktopApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Chemical Equipment Parameter Visualizer")
        self.setGeometry(200, 200, 800, 600)

        self.layout = QVBoxLayout()

        self.upload_btn = QPushButton("Upload CSV")
        self.upload_btn.clicked.connect(self.upload_csv)

        self.summary_label = QLabel("Upload a CSV file to view summary")
        self.summary_label.setWordWrap(True)

        self.chart = ChartCanvas()

        self.layout.addWidget(self.upload_btn)
        self.layout.addWidget(self.summary_label)
        self.layout.addWidget(self.chart)

        self.setLayout(self.layout)

        self.fetch_summary()

    def upload_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select CSV File", "", "CSV Files (*.csv)"
        )

        if not file_path:
            return

        try:
            with open(file_path, 'rb') as f:
                response = requests.post(
                    f"{API_BASE_URL}/upload/",
                    files={"file": f}
                )

            if response.status_code == 200:
                QMessageBox.information(self, "Success", "CSV uploaded successfully")
                self.fetch_summary()
            else:
                QMessageBox.warning(self, "Error", response.text)

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def fetch_summary(self):
        try:
            response = requests.get(f"{API_BASE_URL}/summary/")
            data = response.json()

            self.summary_label.setText(
                f"Total Records: {data['total_rows']}\n"
                f"Avg Flowrate: {data['averages']['flowrate']}\n"
                f"Avg Pressure: {data['averages']['pressure']}\n"
                f"Avg Temperature: {data['averages']['temperature']}"
            )

            self.draw_chart(data["equipment_type_counts"])

        except Exception:
            self.summary_label.setText("Failed to fetch summary from backend")

    def draw_chart(self, counts):
        self.chart.ax.clear()
        names = list(counts.keys())
        values = list(counts.values())

        self.chart.ax.bar(names, values)
        self.chart.ax.set_title("Equipment Type Distribution")
        self.chart.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DesktopApp()
    window.show()
    sys.exit(app.exec_())
