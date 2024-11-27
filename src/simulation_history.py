from src.cell import Cell
from src.weather import Weather
from src.land_types import Unknown

class SimulationHistory:
    def __init__(self):
        self.states = []  # List to store grid states
        self.current_index = -1  # Current position in history

    def add_state(self, grid):
        """Record a new grid state"""
        # Create a deep copy of the current grid state
        state = [[(cell.land_type, cell.state) for cell in row] 
                for row in grid.cells]
        
        # If we're not at the end of history, truncate future states
        if self.current_index < len(self.states) - 1:
            self.states = self.states[:self.current_index + 1]
        
        self.states.append(state)
        self.current_index += 1

    def restore_state(self, grid, index):
        """Restore grid to a specific state"""
        if 0 <= index < len(self.states):
            state = self.states[index]
            for i, row in enumerate(state):
                for j, (land_type, cell_state) in enumerate(row):
                    grid.cells[i][j].land_type = land_type
                    grid.cells[i][j].state = cell_state
            self.current_index = index

    def can_go_back(self):
        return self.current_index > 0

    def can_go_forward(self):
        return self.current_index < len(self.states) - 1