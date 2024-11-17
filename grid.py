import matplotlib.pyplot as plt
import numpy as np
from cell import Cell
from land_types import Unknown
from weather import Weather

class Grid:
    """
    Manages the grid and its cells.
    """
    def __init__(self, min_lat, max_lat, min_lon, max_lon, resolution):
        self.min_lat = min_lat 
        self.max_lat = max_lat 
        self.min_lon = min_lon  
        self.max_lon = max_lon  
        self.resolution = resolution  # cell size
        self.cells = []  # stores the grid cells

    def generate_grid(self):
        """
        Creates the grid with 'Unknown' land type by default.
        """
        latitudes = np.arange(self.min_lat, self.max_lat, self.resolution)
        longitudes = np.arange(self.min_lon, self.max_lon, self.resolution)

        for i, lat in enumerate(latitudes):
            row = []
            for j, lon in enumerate(longitudes):
                row.append(Cell(index=(i, j), land_type=Unknown(), weather=Weather(temperature=21, humidity=50, wind_speed=5)))
            self.cells.append(row)

    def set_area_type(self, start_index, end_index, land_type):
        """
        Sets the land type for a specified area of the grid.
        """
        start_row, start_col = start_index
        end_row, end_col = end_index

        for i in range(start_row, end_row + 1):
            for j in range(start_col, end_col + 1):
                self.cells[i][j].land_type = land_type

    def visualize(self):
        """
        Visualizes the grid using matplotlib.
        """
        fig, ax = plt.subplots(figsize=(10, 8))

        for row in self.cells:
            for cell in row:
                coords = cell.get_coords(self.min_lon, self.min_lat, self.resolution)
                x = [point[0] for point in coords] + [coords[0][0]]
                y = [point[1] for point in coords] + [coords[0][1]]
                color = cell.land_type.get_color()
                ax.fill(x, y, color=color, edgecolor="black", linewidth=0.5)

        ax.set_xlim(self.min_lon, self.max_lon)
        ax.set_ylim(self.min_lat, self.max_lat)
        ax.set_aspect('equal')
        plt.title("Grid Visualization", fontsize=14, weight="bold")
        plt.xlabel("Longitude", fontsize=12)
        plt.ylabel("Latitude", fontsize=12)
        plt.tight_layout()
        plt.show()
