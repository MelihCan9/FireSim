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
    def __init__(self, tree_type, density):
        self.tree_type = tree_type # ? 
        self.density = density

    def get_flammability(self):
        return min(1.0, self.density * 0.8)

    def get_color(self):
        return "green"


class Water(LandType):
    """
    Represents a water area.
    """
    def __init__(self, depth, flow_rate):
        self.depth = depth # ?
        self.flow_rate = flow_rate # ?  

    def get_flammability(self):
        return 0.0 

    def get_color(self):
        return "blue"


class Unknown(LandType):
    """
    Represents an undefined or unclassified area.
    """
    def get_flammability(self):
        return 0.0  # Unknown areas have no flammability effect

    def get_color(self):
        return "white"  # Color for undefined areas is white
