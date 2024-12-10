from enum import Enum
from dataclasses import dataclass
from typing import Tuple, Optional

class ResourceType(Enum):
    FIRE_STATION = "fire_station"
    HELICOPTER = "helicopter"
    UAV = "uav"
    WATER_TANKER = "water_tanker"
    WORK_MACHINE = "work_machine"

@dataclass
class ResourceStats:
    coverage_radius: float  # In grid cells
    effectiveness: float    # 0-1 scale
    response_time: int     # In simulation steps
    water_capacity: Optional[float] = None  # For water-based resources
    movement_speed: Optional[float] = None  # For mobile resources

class FirefightingResource:
    def __init__(self, 
                 resource_type: ResourceType,
                 position: Tuple[int, int],
                 stats: ResourceStats):
        self.resource_type = resource_type
        self.position = position
        self.stats = stats
        self.is_active = False
        self.remaining_water = stats.water_capacity if stats.water_capacity else 0
        
    def can_reach(self, target_pos: Tuple[int, int]) -> bool:
        """Check if resource can reach the target position"""
        i, j = self.position
        target_i, target_j = target_pos
        distance = ((i - target_i) ** 2 + (j - target_j) ** 2) ** 0.5
        return distance <= self.stats.coverage_radius
    
    def calculate_response_time(self, target_pos: Tuple[int, int]) -> float:
        """Calculate time to respond to target position"""
        if not self.can_reach(target_pos):
            return float('inf')
        
        i, j = self.position
        target_i, target_j = target_pos
        distance = ((i - target_i) ** 2 + (j - target_j) ** 2) ** 0.5
        
        if self.stats.movement_speed:
            return distance / self.stats.movement_speed
        return self.stats.response_time 