class Cell:
    """
    Represents a grid cell.
    """
    def __init__(self, index, land_type, weather):
        self.index = index  # Cell position (i, j)
        self.land_type = land_type  # Land type (e.g., Forest, Water)
        self.weather = weather  # Weather conditions
        self.flammability = 0.0  # Initial flammability value
        self.state = "flammable"  # flammable, igniting, burning, burnt
        self.burn_time = 5  # Number of steps the cell burns before becoming burnt
        self.delay_time = 2  # Delay before burning after ignite

    def get_coords(self, min_lon, min_lat, resolution):
        """
        Calculate the corner coordinates of the cell.
        """
        i, j = self.index
        lon = min_lon + j * resolution
        lat = min_lat + i * resolution
        return [
            (lon, lat),
            (lon + resolution, lat),
            (lon + resolution, lat + resolution),
            (lon, lat + resolution)
        ]

    def ignite(self):
        """
        Sets the cell to 'igniting' if it's flammable.
        """
        if self.state == "flammable":
            self.state = "igniting"
            print(f"Cell {self.index} ignited!")

    def burn(self):
        """
        Handles the transition from igniting to burning.
        """
        if self.state == "igniting":
            if self.delay_time > 0:
                self.delay_time -= 1
            if self.delay_time == 0:
                self.state = "burning"
                print(f"Cell {self.index} started burning!")

    def burn_out(self):
        """
        Reduces burn time and transitions the cell to 'burnt'.
        """
        if self.state == "burning":
            if self.burn_time > 0:
                self.burn_time -= 1
            if self.burn_time == 0:
                self.state = "burnt"
                print(f"Cell {self.index} burnt out!")

    def calculate_flammability(self):
        """
        Calculates flammability using land type and weather properties.
        """
        self.flammability = self.land_type.get_flammability()
        if self.flammability > 0:
            self.weather.modify_flammability(self)