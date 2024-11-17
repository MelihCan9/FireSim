class Cell:
    """
    Represents a grid cell.
    """
    def __init__(self, index, land_type, weather):
        self.index = index  
        self.land_type = land_type  #(e.g., Forest, Water)
        self.weather = weather  
        self.flammability = 0.0  # Initial flammability

    def get_coords(self, min_lon, min_lat, resolution):
        """
        Calculate the corner coordinates of the cell. (For grid map)
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

    def calculate_flammability(self):
        """
        f(p,t) 
        """
        self.flammability = self.land_type.get_flammability()
        self.weather.modify_flammability(self)
