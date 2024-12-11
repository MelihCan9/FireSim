import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from src.cell import Cell
from src.weather import Weather
from src.land_types import Unknown
from src.firefighting.routing import RouteStatus

class Grid:
    """
    Manages the grid and its cells.
    """
    def __init__(self, min_lat, max_lat, min_lon, max_lon, resolution):
        self.min_lat = min_lat
        self.max_lat = max_lat
        self.min_lon = min_lon
        self.max_lon = max_lon
        self.resolution = resolution
        self.cells = []
        self.resources = {}  # Dictionary to store resources: {(i,j): resource}

    def generate_grid(self):
        """
        Creates the grid with 'Unknown' land type by default.
        """
        latitudes = np.arange(self.min_lat, self.max_lat, self.resolution)
        longitudes = np.arange(self.min_lon, self.max_lon, self.resolution)

        for i, lat in enumerate(latitudes):
            row = []
            for j, lon in enumerate(longitudes):
                # row.append(Cell(index=(i, j), land_type=Unknown(), weather=Weather(temperature=21, humidity=50, wind_speed=5)))
                cell = Cell(index=(i,j), land_type=Unknown(), weather=Weather(temperature=21, humidity=50, wind_speed=5))
                cell.calculate_flammability()
                row.append(cell)
            self.cells.append(row)
        for row in self.cells:
            for cell in row:
                print(f"Cell: {cell.index}, Flammability: {cell.flammability}")

    def get_real_coordinates(self, i, j):
        """
        Calculate the real-world coordinates (latitude, longitude) for a given cell index.
        """
        lat_range = self.max_lat - self.min_lat
        lon_range = self.max_lon - self.min_lon

        lat = self.min_lat + (i * self.resolution)
        lon = self.min_lon + (j * self.resolution)

        return lat, lon
    def set_area_type(self, start_index, end_index, land_type):
        """
        Sets the land type for a specified area of the grid.
        """
        start_row, start_col = start_index
        end_row, end_col = end_index

        for i in range(start_row, end_row + 1):
            for j in range(start_col, end_col + 1):
                self.cells[i][j].land_type = land_type

    def get_neighbors(self, cell):
        """
        Returns the neighboring cells of a given cell.
        """
        i, j = cell.index
        neighbors = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        for di, dj in directions:
            ni, nj = i + di, j + dj
            if 0 <= ni < len(self.cells) and 0 <= nj < len(self.cells[0]):
                neighbors.append(self.cells[ni][nj])
        return neighbors

    def add_resource(self, resource, position):
        """Add a firefighting resource to the grid"""
        if hasattr(resource, 'resource_type'):  # Only add if it's a firefighting resource
            self.resources[position] = resource
        
    def remove_resource(self, position):
        """Remove a firefighting resource from the grid"""
        if position in self.resources:
            del self.resources[position]

    def get_active_resources(self, cell_position):
        """Get all resources that can reach a given cell"""
        active_resources = []
        for pos, resource in self.resources.items():
            if resource.can_reach(cell_position):
                active_resources.append(resource)
        return active_resources

    def spread_fire(self):
        """Modified spread_fire to consider firefighting resources"""
        burning_cells = []

        for row in self.cells:
            for cell in row:
                if cell.state == "igniting":
                    # Check if any resources can prevent ignition
                    active_resources = self.get_active_resources(cell.index)
                    water_resources = [r for r in active_resources if r.stats.water_capacity is not None and r.remaining_water > 0]
                    total_water_effectiveness = sum(r.stats.effectiveness for r in water_resources)
                    other_resources = [r for r in active_resources if r.stats.water_capacity is None]
                    total_other_effectiveness = sum(r.stats.effectiveness for r in other_resources)
                    
                    total_effectiveness = total_water_effectiveness + total_other_effectiveness
                    
                    if total_effectiveness >= 0.6:  # Lower threshold for preventing ignition
                        cell.state = "flammable"
                        # Reduce water in water-based resources that were used
                        for resource in water_resources:
                            resource.remaining_water = max(0, resource.remaining_water - 50)
                        print(f"Cell {cell.index} ignition prevented by firefighting resources")
                    else:
                        cell.burn()

                elif cell.state == "burning":
                    # Check if resources can extinguish the fire
                    active_resources = self.get_active_resources(cell.index)
                    water_resources = [r for r in active_resources if r.stats.water_capacity is not None and r.remaining_water > 0]
                    total_water_effectiveness = sum(r.stats.effectiveness for r in water_resources)
                    other_resources = [r for r in active_resources if r.stats.water_capacity is None]
                    total_other_effectiveness = sum(r.stats.effectiveness for r in other_resources)
                    
                    total_effectiveness = total_water_effectiveness + total_other_effectiveness
                    
                    if total_effectiveness >= 0.7:  # Threshold for extinguishing
                        cell.state = "flammable"
                        cell.burn_time = 5
                        print(f"Cell {cell.index} fire extinguished by firefighting resources")
                        for resource in water_resources:
                            resource.remaining_water = max(0, resource.remaining_water - 75)
                    else:
                        # If can't extinguish, try to prevent spread
                        neighbors = self.get_neighbors(cell)
                        for neighbor in neighbors:
                            neighbor.calculate_flammability()
                            threshold = 0.4 * (1 - min(total_effectiveness, 0.8))
                            if neighbor.state == "flammable" and neighbor.flammability > threshold:
                                neighbor.ignite()
                        burning_cells.append(cell)

        for cell in burning_cells:
            cell.burn_out()
    def visualize_dynamic(self):
        """
        Visualizes the grid dynamically with fire spread.
        """
        fig, ax = plt.subplots(figsize=(10, 8))

        def update(frame):
            ax.clear()
            # Draw cells
            for row in self.cells:
                for cell in row:
                    coords = cell.get_coords(self.min_lon, self.min_lat, self.resolution)
                    x = [point[0] for point in coords] + [coords[0][0]]
                    y = [point[1] for point in coords] + [coords[0][1]]
                    color = (
                        "orange" if cell.state == "igniting" else
                        "red" if cell.state == "burning" else
                        "gray" if cell.state == "burnt" else
                        cell.land_type.get_color()
                    )
                    ax.fill(x, y, color=color, edgecolor="black", linewidth=0.5)
            
            # Draw resources
            for pos, resource in self.resources.items():
                i, j = pos
                lat, lon = self.get_real_coordinates(i, j)
                
                # Different markers for different resource types
                marker = {
                    'fire_station': '^',
                    'helicopter': 'H',
                    'uav': 'D',
                    'water_tanker': 's',
                    'work_machine': 'P'
                }.get(resource.resource_type.value, 'o')
                
                ax.plot(lon, lat, marker=marker, markersize=10, 
                       color='blue', markeredgecolor='black')
                
                # Draw coverage radius
                circle = plt.Circle((lon, lat), 
                                  resource.stats.coverage_radius * self.resolution,
                                  color='blue', alpha=0.1)
                ax.add_artist(circle)

            self.spread_fire()
            
            ax.set_xlim(self.min_lon, self.max_lon)
            ax.set_ylim(self.min_lat, self.max_lat)
            ax.set_aspect('equal')
            plt.title(f"Fire Spread Simulation (Step: {frame})", fontsize=14, weight="bold")
            plt.xlabel("Longitude", fontsize=12)
            plt.ylabel("Latitude", fontsize=12)

        ani = animation.FuncAnimation(fig, update, frames=50, repeat=False)
        plt.show()

    def update_resources(self):
        """Update all resources positions and states"""
        resources_to_update = {}  # Store position updates
        
        for pos, resource in list(self.resources.items()):
            if resource.route and resource.route.status == RouteStatus.IN_PROGRESS:
                old_pos = pos
                action_needed = resource.update_position()
                new_pos = resource.position
                
                # If position changed, update the resource's location in the grid
                if old_pos != new_pos:
                    resources_to_update[old_pos] = (new_pos, resource)
                
                if action_needed:
                    # Handle resource actions (extinguish, survey, refill)
                    current_waypoint = resource.route.current_waypoint()
                    if current_waypoint.action == "extinguish":
                        cells = self.get_cells_in_radius(current_waypoint.position, 
                                                    resource.stats.coverage_radius)
                        for cell in cells:
                            if cell.state in ["igniting", "burning"]:
                                cell.state = "flammable"
                                resource.remaining_water -= 50
                    elif current_waypoint.action == "refill":
                        resource.remaining_water = resource.stats.water_capacity
                    
                    resource.route.advance()
        
        # Update resource positions in the grid
        for old_pos, (new_pos, resource) in resources_to_update.items():
            del self.resources[old_pos]
            self.resources[new_pos] = resource