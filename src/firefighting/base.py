from enum import Enum
from dataclasses import dataclass
from typing import Tuple, Optional, List
from .routing import Route, RoutePoint, RouteStatus

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
        self.route: Optional[Route] = None
        
    def set_route(self, waypoints: List[RoutePoint]) -> bool:
        """Set a new route for the resource"""
        if not self.stats.movement_speed:
            return False
        self.route = Route(waypoints)
        self.route.status = RouteStatus.IN_PROGRESS
        return True
        
    def update_position(self) -> bool:
        """
        Update position based on current route and movement speed
        Returns True if action needed at current position
        """
        if not self.route or not self.stats.movement_speed:
            return False
            
        current_waypoint = self.route.current_waypoint()
        if not current_waypoint:
            return False
            
        # If we have an action timer, handle it first
        if self.route.action_timer > 0:
            self.route.action_timer -= 1
            return True
            
        # Calculate movement vector
        current_i, current_j = self.position
        target_i, target_j = current_waypoint.position
        
        # If we've reached the waypoint
        if (current_i, current_j) == (target_i, target_j):
            if current_waypoint.action:
                return True  # Signal that an action is needed
            return self.route.advance()
            
        # Calculate distance and movement
        distance = ((current_i - target_i) ** 2 + (current_j - target_j) ** 2) ** 0.5
        
        # If we can reach the waypoint in this step
        if distance <= self.stats.movement_speed:
            self.position = current_waypoint.position
            if current_waypoint.action:
                return True
            return self.route.advance()
            
        # Move towards target
        direction_i = (target_i - current_i) / distance
        direction_j = (target_j - current_j) / distance
        
        new_i = int(current_i + direction_i * self.stats.movement_speed)
        new_j = int(current_j + direction_j * self.stats.movement_speed)
        
        self.position = (new_i, new_j)
        return False
        
    def can_reach(self, target_pos: Tuple[int, int]) -> bool:
        """Check if resource can reach the target position"""
        i, j = self.position
        target_i, target_j = target_pos
        distance = ((i - target_i) ** 2 + (j - target_j) ** 2) ** 0.5
        return distance <= self.stats.coverage_radius