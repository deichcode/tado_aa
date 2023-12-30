import unittest
from unittest.mock import MagicMock

import mock
from PyTado.interface import Tado
from PyTado.const import CONST_OVERLAY_TIMER

from tado_temp_limiter import TadoTempLimiter

CONST_OVERLAY_TADO_MODE = "TADO_MODE"


class TestTadoTempLimit(unittest.TestCase):
    @mock.patch("test_tado_temp_limiter.Tado")
    def setUp(self, tado_mock: MagicMock(Tado)):
        self.tado_mock = tado_mock

        self.temperature_limit = {
            'max': {
                'celsius': 24.0
            },
            'min': {
                'celsius': 16.0
            }
        }
        self.setUp_zones()
        self.setUp_default_overlay()

        self.temp_limit = TadoTempLimiter(tado_mock, self.temperature_limit)

    def setUp_zones(self):
        to_high_temperature = self.temperature_limit['max']['celsius'] + 0.5
        to_low_temperature = self.temperature_limit['min']['celsius'] - 0.5
        self.above_max_zone = {
            "id": 123,
            "name": 'zone 123',
            "setting": {
                "temperature": {
                    "celsius": to_high_temperature}
            }
        }
        self.below_min_zone = {
            "id": 456,
            "name": 'zone 456',
            "setting": {
                "temperature": {
                    "celsius": to_low_temperature
                }
            }
        }
        self.in_bounds_zone = {
            "id": 789,
            "name": 'zone 789',
            "setting": {
                "temperature": self.temperature_limit['max']
            }
        }

    def setUp_default_overlay(self):
        tado_mode_default_overlay = {
            "terminationCondition": {
                "type": CONST_OVERLAY_TADO_MODE
            }
        }
        self.tado_mock.get_zone_overlay_default.return_value = tado_mode_default_overlay

    def test_set_temperature_to_max_if_above(self):
        self.tado_mock.get_zones.return_value = [self.above_max_zone]

        self.temp_limit.limit()

        self.tado_mock.set_zone_overlay.assert_called_with(self.above_max_zone["id"], CONST_OVERLAY_TADO_MODE,
                                                           self.temperature_limit["max"]['celsius'])

    def test_set_temperature_to_min_if_below(self):
        self.tado_mock.get_zones.return_value = [self.below_min_zone]

        self.temp_limit.limit()

        self.tado_mock.set_zone_overlay.assert_called_with(self.below_min_zone["id"], CONST_OVERLAY_TADO_MODE,
                                                           self.temperature_limit["min"]['celsius'])

    def test_unchanged_if_in_bounds(self):
        self.tado_mock.get_zones.return_value = [self.in_bounds_zone]

        self.temp_limit.limit()

        self.tado_mock.set_zone_overlay.assert_not_called()

    def test_only_limit_out_of_bounds_zone(self):
        self.tado_mock.get_zones.return_value = [self.in_bounds_zone, self.above_max_zone, self.below_min_zone]

        self.temp_limit.limit()

        assert self.tado_mock.set_zone_overlay.call_count == 2
        first_set_overlay_call = self.tado_mock.set_zone_overlay.call_args_list[0]
        assert first_set_overlay_call.args == (
            self.above_max_zone["id"], CONST_OVERLAY_TADO_MODE, self.temperature_limit["max"]['celsius'])
        second_set_overlay_call = self.tado_mock.set_zone_overlay.call_args_list[1]
        assert second_set_overlay_call.args == (
            self.below_min_zone["id"], CONST_OVERLAY_TADO_MODE, self.temperature_limit["min"]['celsius'])

    def test_limit_should_use_default_overlay_mode_of_zone(self):
        timer_default_overlay = {
            "terminationCondition": {
                "type": CONST_OVERLAY_TIMER
            }
        }
        self.tado_mock.get_zone_overlay_default.return_value = timer_default_overlay
        self.tado_mock.get_zones.return_value = [self.below_min_zone]

        self.temp_limit.limit()

        self.tado_mock.set_zone_overlay.assert_called_with(self.below_min_zone["id"], CONST_OVERLAY_TIMER,
                                                           self.temperature_limit["min"]['celsius'])

    def test_handle_fahrenheit(self):
        max_celsius = 24
        min_celsius = 16
        self.temperature_limit = {
            'max': {
                'fahrenheit': 75.2  # 24 ºC
            },
            'min': {
                'fahrenheit': 60.8  # 16 ºC
            }
        }
        self.tado_mock.get_zones.return_value = [self.in_bounds_zone, self.above_max_zone, self.below_min_zone]
        self.temp_limit = TadoTempLimiter(self.tado_mock, self.temperature_limit)

        self.temp_limit.limit()

        assert self.tado_mock.set_zone_overlay.call_count == 2
        first_set_overlay_call = self.tado_mock.set_zone_overlay.call_args_list[0]
        assert first_set_overlay_call.args == (
            self.above_max_zone["id"], CONST_OVERLAY_TADO_MODE, max_celsius)
        second_set_overlay_call = self.tado_mock.set_zone_overlay.call_args_list[1]
        assert second_set_overlay_call.args == (
            self.below_min_zone["id"], CONST_OVERLAY_TADO_MODE, min_celsius)
