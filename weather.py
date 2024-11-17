class Weather:
    """
    Represents weather conditions affecting a cell's flammability.
    """
    def __init__(self, temperature, humidity, wind_speed):
        self.temperature = temperature 
        self.humidity = humidity  
        self.wind_speed = wind_speed  

    def modify_flammability(self, cell):
        """
        Burasının citation ile olması gerekyor.
        """
        temperature_effect = max(0, (self.temperature - 20) * 0.01)
        humidity_effect = max(0, (50 - self.humidity) * 0.005)
        wind_effect = self.wind_speed * 0.02
        cell.flammability += temperature_effect + humidity_effect + wind_effect
        cell.flammability = min(1.0, cell.flammability)
