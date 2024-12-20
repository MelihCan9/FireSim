import json
import os
from src.cell import Cell
from src.weather import Weather
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QFrame, QPushButton, QButtonGroup, QFileDialog, QDialog)
from PyQt5.QtCore import Qt
from src.ui.grid_view import GridView
from src.ui.cell_info import CellInfoWidget
from src.land_types import Unknown, Forest, Water, Grassland, Urban, Highway, Recreational
from PyQt5.QtCore import pyqtSignal
from src.ui.grid_settings import GridSettingsDialog
from src.ui.resource_palette import ResourcePalette
from src.firefighting.resources import ResourceType, FireStation, Helicopter, UAV, WaterTanker, WorkMachine
from src.firefighting.routing import RoutePoint

land_types = {
    "Unknown": Unknown,
    "Forest": Forest,
    "Water": Water,
    "Grassland": Grassland,
    "Urban": Urban,
    "Highway": Highway,
    "Recreational": Recreational
}

class LandTypePalette(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setup_ui()
        self.selected_land_type = None
        self.is_ignition_mode = False
        self.is_extinguish_mode = False
        self.current_button = None
        self.is_route_mode = False
        self.selected_resource = None
        self.route_points = []

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Tools"))
        
        # Land Types Section
        land_types_label = QLabel("Land Types")
        land_types_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(land_types_label)
        
        self.button_group = QButtonGroup()
        self.button_group.setExclusive(False)  # Allow deselection
        
        self.land_types = {
            "Unknown": Unknown(),
            "Forest": Forest(tree_type="Pine", density=0.5),
            "Water": Water(),
            "Grassland": Grassland(),
            "Urban": Urban(),
            "Highway": Highway(),
            "Recreational": Recreational()
        }
        
        for name, land_type in self.land_types.items():
            btn = QPushButton(name)
            btn.setCheckable(True)
            self.button_group.addButton(btn)
            layout.addWidget(btn)
            btn.land_type = land_type
        
        # Connect button group signal
        self.button_group.buttonClicked.connect(self.on_land_type_selected)
        
        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        layout.addWidget(line)
        
        # Tool Section
        tools_label = QLabel("Tools")
        tools_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(tools_label)
        
        self.ignite_btn = QPushButton("Ignition Tool")
        self.ignite_btn.setCheckable(True)
        self.ignite_btn.clicked.connect(self.on_ignition_selected)
        layout.addWidget(self.ignite_btn)

        self.extinguish_btn = QPushButton("Extinguish Tool")
        self.extinguish_btn.setCheckable(True)
        self.extinguish_btn.clicked.connect(self.on_extinguish_selected)
        layout.addWidget(self.extinguish_btn)
        
        layout.addStretch()
        self.setLayout(layout)

    def on_extinguish_selected(self, checked):
        if checked:
            self.selected_land_type = None
            self.is_ignition_mode = False
            self.is_extinguish_mode = True
            self.ignite_btn.setChecked(False)
            if self.current_button:
                self.current_button.setChecked(False)
                self.current_button = None
        else:
            self.is_extinguish_mode = False

    def on_land_type_selected(self, clicked_button):
        # If there's a current button and it's different from the clicked one,
        # uncheck it first
        if self.current_button and self.current_button != clicked_button:
            self.current_button.setChecked(False)
        
        # Update the current button
        if clicked_button.isChecked():
            self.current_button = clicked_button
            self.selected_land_type = clicked_button.land_type
            self.is_ignition_mode = False
            self.ignite_btn.setChecked(False)
        else:
            self.current_button = None
            self.selected_land_type = None

    def on_ignition_selected(self, checked):
        if checked:
            self.selected_land_type = None
            self.is_ignition_mode = True
            # Uncheck any selected land type button
            if self.current_button:
                self.current_button.setChecked(False)
                self.current_button = None
        else:
            self.is_ignition_mode = False
class MapEditorWidget(QWidget):
    grid_updated = pyqtSignal()  # Signal for grid updates
    
    def __init__(self, grid):
        super().__init__()
        self.grid = grid
        self.setup_ui()
        self.setup_connections()
        self.is_route_mode = False
        self.selected_resource = None
        self.route_points = []

    def setup_ui(self):
        layout = QHBoxLayout()
        
        # Left panel (tools and file operations)
        left_panel = QVBoxLayout()
        
        # File operations
        file_ops = QHBoxLayout()
        self.save_button = QPushButton("Save Map")
        self.load_button = QPushButton("Load Map")
        self.settings_button = QPushButton("Grid Settings")
        file_ops.addWidget(self.save_button)
        file_ops.addWidget(self.load_button)
        file_ops.addWidget(self.settings_button)
        
        # Add file operations to left panel
        left_panel.addLayout(file_ops)
        
        # Add existing tools (land palette)
        self.land_palette = LandTypePalette()
        left_panel.addWidget(self.land_palette)
        
        # Add resource palette
        self.resource_palette = ResourcePalette()
        left_panel.addWidget(self.resource_palette)
        
        # Grid view and cell info (existing code)
        self.grid_view = GridView(self.grid)
        self.cell_info = CellInfoWidget()
        
        # Add all components to main layout
        layout.addLayout(left_panel, 1)
        layout.addWidget(self.grid_view, 4)
        layout.addWidget(self.cell_info, 1)
        
        self.setLayout(layout)

    def setup_connections(self):
        self.grid_view.scene.cell_clicked.connect(self.on_cell_clicked)
        self.grid_view.scene.area_selected.connect(self.on_area_selected)
        self.settings_button.clicked.connect(self.show_grid_settings)
        self.save_button.clicked.connect(self.save_map)
        self.load_button.clicked.connect(self.load_map)
        self.grid_view.scene.cell_right_clicked.connect(self.on_cell_right_clicked)

    def show_grid_settings(self):
        dialog = GridSettingsDialog(self.grid, self)
        if dialog.exec_() == QDialog.Accepted:
            # Force a complete refresh of the grid view
            self.grid_view.scene.clear()
            self.grid_view.scene.cell_items = {}
            self.grid_view.scene.setup_grid()
            self.update_grid_view()
            self.grid_updated.emit()

    def save_map(self):
        """Save the current map to a JSON file"""
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Save Map",
            "",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_name:
            map_data = {
                'dimensions': {
                    'rows': len(self.grid.cells),
                    'cols': len(self.grid.cells[0])
                },
                'cells': [],
                'resources': []  # Add resources array
            }
            
            for i, row in enumerate(self.grid.cells):
                for j, cell in enumerate(row):
                    land_type_name = cell.land_type.__class__.__name__
                    land_type_params = {}
                    
                    # Handle specific land type parameters
                    if land_type_name == "Forest":
                        land_type_params = {
                            'tree_type': cell.land_type.tree_type,
                            'density': cell.land_type.density
                        }
                    
                    cell_data = {
                        'position': {'row': i, 'col': j},
                        'land_type': land_type_name,
                        'land_type_params': land_type_params,
                        'state': cell.state,
                        'weather': {
                            'temperature': cell.weather.temperature,
                            'humidity': cell.weather.humidity,
                            'wind_speed': cell.weather.wind_speed
                        }
                    }
                    map_data['cells'].append(cell_data)
            
            # Save resources
            for pos, resource in self.grid.resources.items():
                resource_data = {
                    'position': {'row': pos[0], 'col': pos[1]},
                    'type': resource.resource_type.value,
                    'stats': {
                        'coverage_radius': resource.stats.coverage_radius,
                        'effectiveness': resource.stats.effectiveness,
                        'response_time': resource.stats.response_time,
                        'water_capacity': resource.stats.water_capacity,
                        'movement_speed': resource.stats.movement_speed
                    }
                }
                map_data['resources'].append(resource_data)
            
            try:
                with open(file_name, 'w') as f:
                    json.dump(map_data, f, indent=2)
                print(f"Map saved successfully to {file_name}")
            except Exception as e:
                print(f"Error saving map: {e}")

    def load_map(self):
        """Load a map from a JSON file"""
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Load Map",
            "",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_name:
            try:
                with open(file_name, 'r') as f:
                    map_data = json.load(f)
                
                # Clear existing resources
                self.grid.resources.clear()
                self.grid_view.scene.update_resources()
                
                # Load cells (existing code)
                for cell_data in map_data['cells']:
                    i = cell_data['position']['row']
                    j = cell_data['position']['col']
                    
                    # Create land type instance with parameters
                    land_type_name = cell_data['land_type']
                    land_type_class = land_types[land_type_name]
                    land_type_params = cell_data.get('land_type_params', {})

                    # Handle specific land type instantiation
                    if land_type_name == "Forest":
                        land_type = land_type_class(
                            tree_type=land_type_params.get('tree_type', 'Pine'),
                            density=land_type_params.get('density', 0.5)
                        )
                    else:
                        land_type = land_type_class()
                    
                    # Create weather instance
                    weather = Weather(
                        temperature=cell_data['weather']['temperature'],
                        humidity=cell_data['weather']['humidity'],
                        wind_speed=cell_data['weather']['wind_speed']
                    )
                    
                    # Create new cell
                    new_cell = Cell(
                        index=(i, j),
                        land_type=land_type,
                        weather=weather
                    )
                    new_cell.state = cell_data['state']
                    
                    # Update grid
                    self.grid.cells[i][j] = new_cell
                    self.grid_view.scene.update_cell(i, j, new_cell)
                
                # Load resources
                resource_types = {
                    "fire_station": FireStation,
                    "helicopter": Helicopter,
                    "uav": UAV,
                    "water_tanker": WaterTanker,
                    "work_machine": WorkMachine
                }
                
                for resource_data in map_data.get('resources', []):
                    pos = (resource_data['position']['row'], resource_data['position']['col'])
                    resource_class = resource_types[resource_data['type']]
                    resource = resource_class(position=pos)
                    self.grid.add_resource(pos, resource)
                
                self.grid_view.scene.update_resources()
                self.grid_updated.emit()
                print(f"Map loaded successfully from {file_name}")
            except Exception as e:
                print(f"Error loading map: {e}")
    def on_cell_clicked(self, i, j, event=None):
        if event and event.modifiers() & Qt.ControlModifier:
            pos = (i, j)
            # If clicking on a resource, select it for routing
            if pos in self.grid.resources:
                resource = self.grid.resources[pos]
                if resource.stats.movement_speed:  # Only mobile resources can have routes
                    self.selected_resource = resource
                    self.route_points = []
                    print(f"Selected {resource.resource_type.value} for routing")
            # If resource selected, add waypoint
            elif self.selected_resource:
                waypoint = RoutePoint(position=(i, j))
                self.route_points.append(waypoint)
                self.selected_resource.set_route(self.route_points)
                self.grid_view.scene.update_resources()
                print(f"Added waypoint at {i}, {j}")
            return
        
        cell = self.grid.cells[i][j]
        pos = (i, j)
        
        # Handle resource removal first
        if self.resource_palette.is_remove_mode and pos in self.grid.resources:
            self.grid.remove_resource(pos)
            self.grid_view.scene.update_resources()
            self.grid_updated.emit()
            return
        # Calculate real-world coordinates
        lat, lon = self.grid.get_real_coordinates(i, j)
        
        if self.land_palette.selected_land_type:
            # Change land type - use the instance directly
            cell.land_type = self.land_palette.selected_land_type
            cell.calculate_flammability()
            self.grid_view.scene.update_cell(i, j, cell)
            self.grid_updated.emit()
            
        elif self.land_palette.is_ignition_mode:
            # Try to ignite cell
            if cell.land_type.get_flammability() > 0 and cell.state == "flammable":
                cell.ignite()
                self.grid_view.scene.update_cell(i, j, cell)
                self.grid_updated.emit()
                
        elif self.land_palette.is_extinguish_mode:
            # Try to extinguish cell
            if cell.state in ["igniting", "burning"]:
                cell.state = "flammable"
                cell.burn_time = 5
                cell.delay_time = 2
                self.grid_view.scene.update_cell(i, j, cell)
                self.grid_updated.emit()
        
        # Update cell info display
        self.cell_info.update_info(cell, lat, lon)
        
        if self.resource_palette.resource_class:
            # Create resource with position
            resource = self.resource_palette.resource_class(position=(i, j))
            self.grid.add_resource(resource, (i, j))
            self.grid_view.scene.update_resources()
            self.grid_updated.emit()

    def on_area_selected(self, selected_cells):
        for i, j in selected_cells:
            cell = self.grid.cells[i][j]
            if self.land_palette.selected_land_type:
                cell.land_type = self.land_palette.selected_land_type  # Removed ()
                cell.calculate_flammability()
                self.grid_view.scene.update_cell(i, j, cell)
            elif self.land_palette.is_ignition_mode:
                if cell.land_type.get_flammability() > 0 and cell.state == "flammable":
                    cell.ignite()
                    self.grid_view.scene.update_cell(i, j, cell)
            elif self.land_palette.is_extinguish_mode:
                if cell.state in ["igniting", "burning"]:
                    cell.state = "flammable"
                    cell.burn_time = 5
                    cell.delay_time = 2
                    self.grid_view.scene.update_cell(i, j, cell)
        
        self.grid_updated.emit()

    def update_grid_view(self):
        """Update the visual representation of the grid"""
        for i, row in enumerate(self.grid.cells):
            for j, cell in enumerate(row):
                self.grid_view.scene.update_cell(i, j, cell)

    def on_cell_right_clicked(self, i, j):
        pos = (i, j)
        # If clicking on a resource, select it for routing
        if pos in self.grid.resources:
            resource = self.grid.resources[pos]
            if hasattr(resource.stats, 'movement_speed') and resource.stats.movement_speed > 0:  # Check if mobile
                self.selected_resource = resource
                self.route_points = []
                print(f"Selected {resource.resource_type.value} for routing")
                return
            
        # If resource is selected, add waypoint
        if self.selected_resource and hasattr(self.selected_resource.stats, 'movement_speed') and self.selected_resource.stats.movement_speed > 0:
            waypoint = RoutePoint(position=(i, j))
            self.route_points.append(waypoint)
            self.selected_resource.set_route(self.route_points)
            self.grid_view.scene.update_resources()
            print(f"Added waypoint at {i}, {j}")