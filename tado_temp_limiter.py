from PyTado.interface import Tado


def _to_celsius(fahrenheit_temperature):
    return (fahrenheit_temperature - 32) * 5 / 9


class TadoTempLimiter:
    def __init__(self, tado: Tado, temperature_limit):
        self.tado = tado
        if 'celsius' not in temperature_limit['min']:
            temperature_limit['min']['celsius'] = _to_celsius(temperature_limit['min']['fahrenheit'])
        if 'celsius' not in temperature_limit['max']:
            temperature_limit['max']['celsius'] = _to_celsius(temperature_limit['max']['fahrenheit'])
        self.temperature_limit = temperature_limit

    def limit(self):
        zones = self.tado.get_zones()
        for zone in zones:
            set_temperature = zone['setting']['temperature']['celsius']
            clamped_temperature = self._clamp(set_temperature, self.temperature_limit['min']['celsius'],
                                              self.temperature_limit['max']['celsius'])
            if clamped_temperature != set_temperature:
                overlay_mode = self.get_default_overlay_mode()
                self.set_zone_temperature(zone["id"], overlay_mode, clamped_temperature)

    def _clamp(self, value, min_value, max_value):
        return min(max(min_value, value), max_value)

    def get_default_overlay_mode(self):
        default_overlay = self.tado.get_zone_overlay_default(0)
        overlay_mode = default_overlay['terminationCondition']['type']
        return overlay_mode

    def set_zone_temperature(self, zone_id, overlay_mode, temperature):
        self.tado.set_zone_overlay(zone_id, overlay_mode, temperature)
