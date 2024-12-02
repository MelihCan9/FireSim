import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from src.cell import Cell
from src.weather import Weather
from src.land_types import Unknown

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

    def spread_fire(self):
        """
        Spreads fire from burning cells to flammable neighbors.
        """
        burning_cells = []

        for row in self.cells:
            for cell in row:
                if cell.state == "igniting":
                    cell.burn()

                if cell.state == "burning":
                    neighbors = self.get_neighbors(cell)
                    for neighbor in neighbors:
                        neighbor.calculate_flammability()
                        if neighbor.state == "flammable" and neighbor.flammability > 0.3:
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

            self.spread_fire()

            ax.set_xlim(self.min_lon, self.max_lon)
            ax.set_ylim(self.min_lat, self.max_lat)
            ax.set_aspect('equal')
            plt.title(f"Fire Spread Simulation (Step: {frame})", fontsize=14, weight="bold")
            plt.xlabel("Longitude", fontsize=12)
            plt.ylabel("Latitude", fontsize=12)

        ani = animation.FuncAnimation(fig, update, frames=50, repeat=False)
        plt.show()