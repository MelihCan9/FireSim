from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QPushButton, QMessageBox)
from PyQt5.QtCore import Qt

class GridSettingsDialog(QDialog):
    def __init__(self, grid, parent=None):
        super().__init__(parent)
        self.grid = grid
        self.setWindowTitle("Grid Settings")
        self.setup_ui()
        
    def setup_ui(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)  # Set the layout first
        
        # Create input fields
        self.min_lat_input = self.create_input_field("Min Latitude:", str(self.grid.min_lat))
        self.max_lat_input = self.create_input_field("Max Latitude:", str(self.grid.max_lat))
        self.min_lon_input = self.create_input_field("Min Longitude:", str(self.grid.min_lon))
        self.max_lon_input = self.create_input_field("Max Longitude:", str(self.grid.max_lon))
        self.resolution_input = self.create_input_field("Resolution:", str(self.grid.resolution))
        
        # Add buttons
        button_layout = QHBoxLayout()
        apply_button = QPushButton("Apply")
        cancel_button = QPushButton("Cancel")
        
        apply_button.clicked.connect(self.apply_settings)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(apply_button)
        button_layout.addWidget(cancel_button)
        
        main_layout.addLayout(button_layout)
    
    def create_input_field(self, label_text, default_value):
        layout = QHBoxLayout()
        label = QLabel(label_text)
        input_field = QLineEdit(default_value)
        layout.addWidget(label)
        layout.addWidget(input_field)
        self.layout().addLayout(layout)
        return input_field
    
    def apply_settings(self):
        try:
            min_lat = float(self.min_lat_input.text())
            max_lat = float(self.max_lat_input.text())
            min_lon = float(self.min_lon_input.text())
            max_lon = float(self.max_lon_input.text())
            resolution = float(self.resolution_input.text())
            
            # Validate values
            if min_lat >= max_lat or min_lon >= max_lon:
                raise ValueError("Min values must be less than max values")
            if resolution <= 0:
                raise ValueError("Resolution must be greater than 0")
            
            # Update grid parameters
            self.grid.min_lat = min_lat
            self.grid.max_lat = max_lat
            self.grid.min_lon = min_lon
            self.grid.max_lon = max_lon
            self.grid.resolution = resolution
            
            # Clear the existing scene completely
            if hasattr(self.parent(), 'grid_view'):
                scene = self.parent().grid_view.scene
                scene.selected_cell = None
                scene.clear()  # Clear all items from scene
                scene.cell_items = {}  # Clear the cell items dictionary
            
            # Generate new grid
            self.grid.cells = []  # Clear existing cells
            self.grid.generate_grid()  # Generate new grid
            
            # Setup the new grid view
            if hasattr(self.parent(), 'grid_view'):
                self.parent().grid_view.scene.setup_grid()
                self.parent().grid_view.center_view()
            
            self.accept()
            
        except ValueError as e:
            QMessageBox.warning(self, "Invalid Input", str(e))