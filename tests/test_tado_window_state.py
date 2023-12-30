from tado_window_state import TadoWindowState
from PyTado.interface import Tado
import mock

first_call_index = 0
first_argument_index = 0


@mock.patch("test_tado_window_state.Tado")
@mock.patch("tado_window_state.Logger")
def test_update_set_open_window_state_for_zone_with_detected_open_window(logger_mock, tado_mock):
    open_window_zone = {
        "id": 0,
        "name": "zone 0"
    }
    tado_mock.get_zones.return_value = [open_window_zone]
    tado_mock.get_open_window_detect.return_value = {"openWindowDetected": True}
    ws = TadoWindowState(tado_mock)

    ws.update()

    tado_mock.set_open_window.assert_called_with(open_window_zone["id"])
    logger_mock.info.assert_called()
    assert open_window_zone["name"] in logger_mock.info.call_args_list[first_call_index].args[first_argument_index]


@mock.patch("test_tado_window_state.Tado")
@mock.patch("tado_window_state.Logger")
def test_update_do_not_set_open_window_state_for_zone_with_no_detected_open_window(logger_mock, tado_mock):
    closed_window_zone = {
        "id": 1,
        "name": "zone 1"
    }
    tado_mock.get_zones.return_value = [closed_window_zone]
    tado_mock.get_open_window_detect.return_value = {"openWindowDetected": False}
    ws = TadoWindowState(tado_mock)

    ws.update()

    tado_mock.set_open_window.assert_not_called()


@mock.patch("test_tado_window_state.Tado")
@mock.patch("tado_window_state.Logger")
def test_update_only_set_open_window_for_zones_with_detected_open_window(logger_mock, tado_mock):
    open_window_zone = {
        "id": 0,
        "name": "zone 0"
    }
    closed_window_zone = {
        "id": 1,
        "name": "zone 1"
    }
    tado_mock.get_zones.return_value = [closed_window_zone, open_window_zone]
    tado_mock.get_open_window_detect.side_effect = [{"openWindowDetected": False}, {"openWindowDetected": True}]
    ws = TadoWindowState(tado_mock)

    ws.update()

    tado_mock.set_open_window.assert_called_once()
    assert tado_mock.set_open_window.call_args_list[first_call_index].args[first_argument_index] == 0


