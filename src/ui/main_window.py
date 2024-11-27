from PyQt5.QtWidgets import QMainWindow, QTabWidget
from src.ui.map_editor import MapEditorWidget
from src.ui.simulation import SimulationWidget

class MainWindow(QMainWindow):
    def __init__(self, grid):
        super().__init__()
        self.setWindowTitle("Fire Simulation")
        self.setGeometry(100, 100, 1200, 800)
        
        self.grid = grid  # Store grid reference
        
        # Create tab widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Create our main widgets with the same grid instance
        self.map_editor = MapEditorWidget(self.grid)
        self.simulation = SimulationWidget(self.grid)
        
        # Connect the tabs to update each other
        self.simulation.grid_updated.connect(self.map_editor.update_grid_view)
        self.map_editor.grid_updated.connect(self.simulation.update_grid_view)
        
        # Connect to tab change event
        self.tabs.currentChanged.connect(self.on_tab_changed)
        
        # Add tabs
        self.tabs.addTab(self.map_editor, "Map Generation")
        self.tabs.addTab(self.simulation, "Simulation")

    def on_tab_changed(self, index):
        # Update the view of the newly selected tab
        if index == 0:  # Map Generation
            self.map_editor.update_grid_view()
        else:  # Simulation
            self.simulation.update_grid_view()