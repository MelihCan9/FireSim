from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QSlider, QStyle)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from src.ui.grid_view import GridView
from src.simulation_history import SimulationHistory
from src.cell import Cell
from src.weather import Weather
from src.land_types import Unknown

class SimulationWidget(QWidget):
    grid_updated = pyqtSignal()  # Signal for grid updates

    def __init__(self, grid):
        super().__init__()
        self.grid = grid
        self.simulation_speed = 1000
        self.is_running = False
        self.history = SimulationHistory()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.run_simulation_step)
        
        self.setup_ui()
        self.setup_connections()

    def update_grid_view(self):
        """Update the entire grid view"""
        for i, row in enumerate(self.grid.cells):
            for j, cell in enumerate(row):
                self.grid_view.scene.update_cell(i, j, cell)

    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Simulation controls
        sim_controls = QHBoxLayout()
        self.play_pause_button = QPushButton("Play")
        self.step_button = QPushButton("Step")
        self.reset_button = QPushButton("Reset Map")  # Add reset button
        
        # Speed control
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("Speed:"))
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(100, 2000)
        self.speed_slider.setValue(self.simulation_speed)
        self.speed_slider.setInvertedAppearance(True)
        speed_layout.addWidget(self.speed_slider)
        
        sim_controls.addWidget(self.play_pause_button)
        sim_controls.addWidget(self.step_button)
        sim_controls.addWidget(self.reset_button)
        sim_controls.addLayout(speed_layout)
        
        # Timeline controls
        timeline_controls = QHBoxLayout()
        self.back_button = QPushButton()
        self.back_button.setIcon(self.style().standardIcon(QStyle.SP_MediaSkipBackward))
        self.forward_button = QPushButton()
        self.forward_button.setIcon(self.style().standardIcon(QStyle.SP_MediaSkipForward))
        
        self.timeline_slider = QSlider(Qt.Horizontal)
        self.timeline_slider.setEnabled(False)  # Disabled until we have history
        
        timeline_controls.addWidget(self.back_button)
        timeline_controls.addWidget(self.timeline_slider)
        timeline_controls.addWidget(self.forward_button)
        
        # Main simulation view
        self.grid_view = GridView(self.grid)
        
        layout.addLayout(sim_controls)
        layout.addLayout(timeline_controls)
        layout.addWidget(self.grid_view)
        self.setLayout(layout)
    
    def toggle_simulation(self):
        """Toggle between play and pause states"""
        if self.is_running:
            self.pause_simulation()
        else:
            self.start_simulation()    

    def setup_connections(self):
        self.play_pause_button.clicked.connect(self.toggle_simulation)
        self.step_button.clicked.connect(self.run_simulation_step)
        self.reset_button.clicked.connect(self.reset_map)
        self.speed_slider.valueChanged.connect(self.update_simulation_speed)
        self.back_button.clicked.connect(self.step_backward)
        self.forward_button.clicked.connect(self.step_forward)
        self.timeline_slider.valueChanged.connect(self.on_timeline_changed)    

    def start_simulation(self):
        """Start the simulation"""
        self.is_running = True
        self.play_pause_button.setText("Pause")
        self.step_button.setEnabled(False)
        
        # Clear future history states if we're starting from a rewound position
        if self.history.current_index < len(self.history.states) - 1:
            self.history.states = self.history.states[:self.history.current_index + 1]
        
        self.timer.start(self.simulation_speed)

    def pause_simulation(self):
        """Pause the simulation"""
        self.is_running = False
        self.play_pause_button.setText("Play")
        self.step_button.setEnabled(True)
        self.timer.stop()

    def reset_map(self):
        """Reset the map to all Unknown cells with proper initialization"""
        # Stop simulation if running
        if self.is_running:
            self.pause_simulation()
        
        # Reset history
        self.history = SimulationHistory()
        self.timeline_slider.setEnabled(False)
        
        # Reset all cells with proper initialization
        for i, row in enumerate(self.grid.cells):
            for j, cell in enumerate(row):
                # Create new cell with all parameters
                new_cell = Cell(
                    index=(i, j),
                    land_type=Unknown(),
                    weather=Weather(temperature=21, humidity=50, wind_speed=5)
                )
                self.grid.cells[i][j] = new_cell
                self.grid_view.scene.update_cell(i, j, new_cell)
        
        self.grid_updated.emit()

    def run_simulation_step(self):
        has_active_fires = False
        for row in self.grid.cells:
            for cell in row:
                if cell.state in ["igniting", "burning"]:
                    has_active_fires = True
                    break
        
        if not has_active_fires:
            self.pause_simulation()
            print("Simulation ended: No active fires")
            return

        # Record current state before making changes
        self.history.add_state(self.grid)
        
        # Update timeline slider
        self.timeline_slider.setRange(0, len(self.history.states) - 1)
        self.timeline_slider.setValue(self.history.current_index)
        self.timeline_slider.setEnabled(True)
        
        # Run simulation step
        self.grid.spread_fire()
        self.update_grid_view()
        self.grid_updated.emit()
        
        # Update timeline controls
        self.update_timeline_controls()

    def update_simulation_speed(self, value):
        self.simulation_speed = value
        if self.timer.isActive():
            self.timer.start(self.simulation_speed)

    def update_grid_view(self):
        for i, row in enumerate(self.grid.cells):
            for j, cell in enumerate(row):
                self.grid_view.scene.update_cell(i, j, cell)

    def step_backward(self):
        if self.history.can_go_back():
            self.history.restore_state(self.grid, self.history.current_index - 1)
            self.timeline_slider.setValue(self.history.current_index)
            self.update_grid_view()
            self.grid_updated.emit()
            self.update_timeline_controls()

    def step_forward(self):
        if self.history.can_go_forward():
            self.history.restore_state(self.grid, self.history.current_index + 1)
            self.timeline_slider.setValue(self.history.current_index)
            self.update_grid_view()
            self.grid_updated.emit()
            self.update_timeline_controls()

    def on_timeline_changed(self, value):
        if not self.timeline_slider.isSliderDown():  # Only respond to user input
            return
        self.history.restore_state(self.grid, value)
        self.update_grid_view()
        self.grid_updated.emit()
        self.update_timeline_controls()

    def update_timeline_controls(self):
        self.back_button.setEnabled(self.history.can_go_back())
        self.forward_button.setEnabled(self.history.can_go_forward())