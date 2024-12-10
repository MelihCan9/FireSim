from .base import FirefightingResource, ResourceType, ResourceStats

class FireStation(FirefightingResource):
    def __init__(self, position):
        stats = ResourceStats(
            coverage_radius=5.0,
            effectiveness=0.8,
            response_time=2,
            water_capacity=1000.0
        )
        super().__init__(ResourceType.FIRE_STATION, position, stats)

class Helicopter(FirefightingResource):
    def __init__(self, position):
        stats = ResourceStats(
            coverage_radius=8.0,
            effectiveness=0.9,
            response_time=1,
            water_capacity=500.0,
            movement_speed=2.0
        )
        super().__init__(ResourceType.HELICOPTER, position, stats)

class UAV(FirefightingResource):
    def __init__(self, position):
        stats = ResourceStats(
            coverage_radius=3.0,
            effectiveness=0.4,
            response_time=1,
            movement_speed=3.0
        )
        super().__init__(ResourceType.UAV, position, stats)

class WaterTanker(FirefightingResource):
    def __init__(self, position):
        stats = ResourceStats(
            coverage_radius=2.0,
            effectiveness=0.7,
            response_time=3,
            water_capacity=2000.0,
            movement_speed=0.5
        )
        super().__init__(ResourceType.WATER_TANKER, position, stats)

class WorkMachine(FirefightingResource):
    def __init__(self, position):
        stats = ResourceStats(
            coverage_radius=1.5,
            effectiveness=0.6,
            response_time=2,
            movement_speed=0.8
        )
        super().__init__(ResourceType.WORK_MACHINE, position, stats) 