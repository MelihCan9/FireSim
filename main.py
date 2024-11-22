from grid import Grid
from land_types import Forest, Water, Grassland, Urban, Highway, Recreational
from weather import Weather

# Grid parameters
min_lat, max_lat = 39.6, 40.0
min_lon, max_lon = 32.5, 33.0
resolution = 0.015

# Create the grid
grid = Grid(min_lat, max_lat, min_lon, max_lon, resolution)
grid.generate_grid()

# Define land types with a balanced layout
# Forest patches
grid.set_area_type((0, 0), (5, 5), Forest(tree_type="Pine", density=0.9))
grid.set_area_type((10, 10), (15, 15), Forest(tree_type="Oak", density=0.8))

# Grassland patches
grid.set_area_type((6, 6), (8, 8), Grassland())
grid.set_area_type((18, 18), (20, 20), Grassland())

# Water barriers
grid.set_area_type((5, 10), (7, 12), Water())
grid.set_area_type((15, 5), (16, 7), Water())

# Urban areas
grid.set_area_type((22, 22), (25, 25), Urban())
grid.set_area_type((0, 15), (2, 18), Urban())

# Recreational area (park)
grid.set_area_type((8, 18), (10, 20), Recreational())

# Highway (barrier to fire spread)
grid.set_area_type((12, 0), (12, 25), Highway())

# Ignite fire in specific cells
grid.cells[3][3].ignite()  # Start in forest
grid.cells[19][19].ignite()  # Grassland fire
grid.cells[15][15].ignite()  # Grassland fire

# Run the simulation
grid.visualize_dynamic()
