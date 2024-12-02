class LandType:
    """
    Abstract class representing a type of land.
    """
    def get_flammability(self):
        raise NotImplementedError("Subclass must implement this method.")

    def get_color(self):
        raise NotImplementedError("Subclass must implement this method.")

class Forest(LandType):
    """
    Represents a forest area.
    """
    def __init__(self, tree_type, density, fuel_density=0.8, ignition_energy=180, efficiency=0.9):
        self.tree_type = tree_type  # Tree type (e.g., Pine, Oak)
        self.density = density  # Forest density (0.0 - 1.0)
        self.fuel_density = fuel_density  # Fuel density (kg/m³)
        self.ignition_energy = ignition_energy  # Ignition energy (kJ/kg)
        self.efficiency = efficiency  # Energy efficiency (0.0 - 1.0)

    def get_flammability(self):
        """
        Flammability calculation based on forest properties.
        """
        return self.fuel_density * self.efficiency * self.ignition_energy * self.density
    
    def get_color(self):
        return "green"
# Water
class Water(LandType):
    def get_flammability(self):
        return 0.0  # Water is not flammable

    def get_color(self):
        return "blue"

# Unknown
class Unknown(LandType):
    def get_flammability(self):
        return 0.0  # Unknown areas are not flammable

    def get_color(self):
        return "white"

# Urban
class Urban(LandType):
    def get_flammability(self):
        return 0.1  # Very low flammability due to concrete and infrastructure

    def get_color(self):
        return "yellow"

# Agricultural
class Agricultural(LandType):
    def get_flammability(self):
        return 0.5  # Medium flammability due to dry crops

    def get_color(self):
        return "tan"

# Grassland
class Grassland(LandType):
    def get_flammability(self):
        return 0.7  # High flammability due to dry grass

    def get_color(self):
        return "lightgreen"

# Industrial
class Industrial(LandType):
    def get_flammability(self):
        return 0.05  # Very low flammability

    def get_color(self):
        return "darkgrey"

# Highway
class Highway(LandType):
    def get_flammability(self):
        return 0.0  # Non-flammable

    def get_color(self):
        return "black"
    
# Recreational
class Recreational(LandType):
    def get_flammability(self):
        return 0.4  # Parks are moderately flammable

    def get_color(self):
        return "darkgreen"