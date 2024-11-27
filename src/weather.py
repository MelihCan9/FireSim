class Weather:
    """
    Represents weather conditions affecting a cell's flammability.
    """
    def __init__(self, temperature, humidity, wind_speed):
        self.temperature = temperature  # Temperature (°C)
        self.humidity = humidity  # Humidity (%)
        self.wind_speed = wind_speed  # Wind speed (km/h)

    def modify_flammability(self, cell):
        """
        Adjust flammability based on weather parameters.
        """
        temperature_effect = max(0, (self.temperature - 20) * 0.01)
        humidity_effect = max(0, (50 - self.humidity) * 0.005)
        wind_effect = self.wind_speed * 0.02
        cell.flammability += temperature_effect + humidity_effect + wind_effect
        cell.flammability = min(1.0, cell.flammability)
