from grid import Grid
from land_types import Forest, Water
from weather import Weather

# grid parameters
min_lat, max_lat = 39.6, 40.0
min_lon, max_lon = 32.5, 33.0
resolution = 0.01

# Create the grid
grid = Grid(min_lat, max_lat, min_lon, max_lon, resolution)
grid.generate_grid()

# Define cells
grid.set_area_type((0, 0), (2, 2), Forest(tree_type="Pine", density=0.8))
grid.set_area_type((8, 8), (10, 10), Water(depth=10, flow_rate=3))
grid.cells[15][15].land_type = Forest(tree_type="Pine", density=0.8)
grid.cells[26][25].land_type = Forest(tree_type="Pine", density=0.7)
grid.cells[37][37].land_type = Water(depth=10, flow_rate=3)
grid.cells[38][38].land_type = Water(depth=8, flow_rate=2)

# Visualize the grid
grid.visualize()
