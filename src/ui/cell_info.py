from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt

class CellInfoWidget(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.title = QLabel("Cell Information")
        self.title.setAlignment(Qt.AlignCenter)
        
        self.info_labels = {
            "Index": QLabel("Index: -"),
            "Coordinates": QLabel("Coordinates: -"),
            "Land Type": QLabel("Land Type: -"),
            "State": QLabel("State: -"),
            "Flammability": QLabel("Flammability: -"),
            "Temperature": QLabel("Temperature: -"),
            "Humidity": QLabel("Humidity: -"),
            "Wind Speed": QLabel("Wind Speed: -")
        }
        
        layout.addWidget(self.title)
        for label in self.info_labels.values():
            layout.addWidget(label)
        
        self.setLayout(layout)

    def update_info(self, cell, lat, lon):
        if cell:
            self.info_labels["Index"].setText(f"Index: {cell.index}")
            self.info_labels["Coordinates"].setText(f"Coordinates: ({lat:.4f}, {lon:.4f})")
            self.info_labels["Land Type"].setText(f"Land Type: {cell.land_type.__class__.__name__}")
            self.info_labels["State"].setText(f"State: {cell.state}")
            self.info_labels["Flammability"].setText(f"Flammability: {cell.flammability:.2f}")
            self.info_labels["Temperature"].setText(f"Temperature: {cell.weather.temperature}°C")
            self.info_labels["Humidity"].setText(f"Humidity: {cell.weather.humidity}%")
            self.info_labels["Wind Speed"].setText(f"Wind Speed: {cell.weather.wind_speed} km/h")