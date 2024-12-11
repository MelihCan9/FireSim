from dataclasses import dataclass
from typing import List, Tuple, Optional
from enum import Enum

class RouteStatus(Enum):
    IDLE = "idle"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class RoutePoint:
    position: Tuple[int, int]
    action: Optional[str] = None  # e.g., "extinguish", "survey", "refill"
    duration: int = 0  # How many steps to spend at this point

class Route:
    def __init__(self, waypoints: List[RoutePoint]):
        self.waypoints = waypoints
        self.current_index = 0
        self.status = RouteStatus.IDLE
        self.action_timer = 0
    
    def current_waypoint(self) -> Optional[RoutePoint]:
        if self.current_index < len(self.waypoints):
            return self.waypoints[self.current_index]
        return None
    
    def next_waypoint(self) -> Optional[RoutePoint]:
        if self.current_index + 1 < len(self.waypoints):
            return self.waypoints[self.current_index + 1]
        return None
    
    def advance(self) -> bool:
        """
        Advances to next waypoint.
        Returns True if there are more waypoints, False if route is complete.
        """
        if self.current_index < len(self.waypoints) - 1:
            self.current_index += 1
            self.action_timer = self.waypoints[self.current_index].duration
            return True
        self.status = RouteStatus.COMPLETED
        return False 