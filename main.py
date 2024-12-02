from PyQt5.QtWidgets import QApplication
import sys
from src.grid import Grid
from src.ui.main_window import MainWindow
from src.weather import Weather

def main():
    # Grid parameters
    min_lat, max_lat = 39.6, 40.0
    min_lon, max_lon = 32.5, 33.0
    resolution = 0.03

    # Create the grid
    grid = Grid(min_lat, max_lat, min_lon, max_lon, resolution)
    grid.generate_grid()

    app = QApplication(sys.argv)
    window = MainWindow(grid)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
