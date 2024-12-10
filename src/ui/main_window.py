from PyQt5.QtWidgets import QMainWindow, QTabWidget
from src.ui.map_editor import MapEditorWidget
from src.ui.simulation import SimulationWidget

class MainWindow(QMainWindow):
    def __init__(self, grid):
        super().__init__()
        self.grid = grid
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Fire Simulation")
        self.setGeometry(100, 100, 1200, 800)

        # Create tab widget
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # Create map editor widget
        self.map_editor = MapEditorWidget(self.grid)
        self.tab_widget.addTab(self.map_editor, "Map Generation")

        # Create simulation widget with the same grid instance
        self.simulation = SimulationWidget(self.grid)
        self.tab_widget.addTab(self.simulation, "Simulation")

        # Connect tab change signal
        self.tab_widget.currentChanged.connect(self.on_tab_changed)

    def on_tab_changed(self, index):
        # Update the grid view in both tabs when switching
        if index == 0:  # Map Generation tab
            self.map_editor.grid_view.scene.update_resources()
            self.map_editor.update_grid_view()
        else:  # Simulation tab
            self.simulation.grid_view.scene.update_resources()
            self.simulation.update_grid_view()