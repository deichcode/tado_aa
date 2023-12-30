#
# Tado Auto-Assist for Geofencing and Open Window Detection
# Crated by Sören Schröder <code@razupaltuff.eu> on Dec, 27th 2023
# Rewrite of ado_aa.py by Adrian Slabu <adrianslabu@icloud.com> on 11.02.2021
# 

from tado_home_state import TadoHomeState
from PyTado.interface import Tado
import mock

@mock.patch("test_tado_home_state.Tado")
@mock.patch("tado_home_state.Logger")
def test_home_state_set_HOME_if_device_is_present_and_was_AWAY(mock_logger, mock_tado):
    mobile1 = {
        "settings": {
            "geoTrackingEnabled": True
        },
        "location": {
            "atHome": True
        }
    }
    mock_tado.get_mobile_devices.return_value = [mobile1]
    mock_tado.get_home_state.return_value = {"presence": "AWAY"}
    
    TadoHomeState(mock_tado)

    mock_tado.set_home.assert_called()

    
@mock.patch("test_tado_home_state.Tado")
@mock.patch("tado_home_state.Logger")
def test_home_state_set_AWAY_if_device_is_not_present_and_was_HOME(mock_logger, mock_tado):
    mobile1 = {
        "settings": {
            "geoTrackingEnabled": True
        },
        "location": {
            "atHome": False
        }
    }
    mock_tado.get_mobile_devices.return_value = [mobile1]
    mock_tado.get_home_state.return_value = {"presence": "HOME"}
    
    TadoHomeState(mock_tado)

    mock_tado.set_away.assert_called()

@mock.patch("test_tado_home_state.Tado")
@mock.patch("tado_home_state.Logger")
def test_home_state_do_nothing_if_device_is_is_not_present_and_state_is_AWAY(mock_logger, mock_tado):
    mobile1 = {
        "settings": {
            "geoTrackingEnabled": True
        },
        "location": {
            "atHome": False
        }
    }
    mock_tado.get_mobile_devices.return_value = [mobile1]
    mock_tado.get_home_state.return_value = {"presence": "AWAY"}
    
    TadoHomeState(mock_tado)

    mock_tado.set_away.assert_not_called()
    mock_tado.set_home.assert_not_called()

@mock.patch("test_tado_home_state.Tado")
@mock.patch("tado_home_state.Logger")
def test_home_state_do_nothing_if_device_is_is__present_and_state_is_HOME(mock_logger, mock_tado):
    mobile1 = {
        "settings": {
            "geoTrackingEnabled": True
        },
        "location": {
            "atHome": True
        }
    }
    mock_tado.get_mobile_devices.return_value = [mobile1]
    mock_tado.get_home_state.return_value = {"presence": "HOME"}
    
    TadoHomeState(mock_tado)

    mock_tado.set_away.assert_not_called()
    mock_tado.set_home.assert_not_called()

@mock.patch("test_tado_home_state.Tado")
@mock.patch("tado_home_state.Logger")
def test_home_state_set_away_if_none_device_is_present(mock_logger, mock_tado):
    mobile1 = {
        "settings": {
            "geoTrackingEnabled": True
        },
        "location": {
            "atHome": False
        }
    }
    mobile2 = {
        "settings": {
            "geoTrackingEnabled": True
        },
        "location": {
            "atHome": False
        }
    }
    mock_tado.get_mobile_devices.return_value = [mobile1, mobile2]
    mock_tado.get_home_state.return_value = {"presence": "HOME"}
    
    TadoHomeState(mock_tado)

    mock_tado.set_away.assert_called()

@mock.patch("test_tado_home_state.Tado")
@mock.patch("tado_home_state.Logger")
def test_home_state_set_HOME_if_at_least_one_device_is_present(mock_logger, mock_tado):
    mobile1 = {
        "settings": {
            "geoTrackingEnabled": True
        },
        "location": {
            "atHome": False
        }
    }
    mobile2 = {
        "settings": {
            "geoTrackingEnabled": True
        },
        "location": {
            "atHome": True
        }
    }
    mock_tado.get_mobile_devices.return_value = [mobile1, mobile2]
    mock_tado.get_home_state.return_value = {"presence": "AWAY"}
    
    TadoHomeState(mock_tado)

    mock_tado.set_home.assert_called()

@mock.patch("test_tado_home_state.Tado")
@mock.patch("tado_home_state.Logger")
def test_home_state_ignore_devices_with_disabled_location(mock_logger, mock_tado):
    mobile1 = {
        "settings": {
            "geoTrackingEnabled": True
        },
        "location": {
            "atHome": False
        }
    }
    mobile2 = {
        "settings": {
            "geoTrackingEnabled": False
        },
    }
    mock_tado.get_mobile_devices.return_value = [mobile1, mobile2]
    mock_tado.get_home_state.return_value = {"presence": "AWAY"}
    
    TadoHomeState(mock_tado)

    mock_tado.set_away.assert_not_called()
    mock_tado.set_home.assert_not_called()

@mock.patch("test_tado_home_state.Tado")
@mock.patch("tado_home_state.Logger")
def test_home_state_log_warning_when_not_mobile_device_with_location(mock_logger, mock_tado):
    mock_tado.get_mobile_devices.side_effect = Exception('location')
    
    TadoHomeState(mock_tado)

    mock_logger.warning.assert_called()

@mock.patch("test_tado_home_state.Tado")
@mock.patch("tado_home_state.Logger")
@mock.patch("tado_home_state.time")
def test_home_state_log_error_and_retry_on_other_exceptions(mock_time, mock_logger, mock_tado):    
    errorRetringInterval = 0
    mock_tado.get_home_state.side_effect = [
        Exception("something else"),
        {
            "presence": "HOME"
        }
    ]
    
    TadoHomeState(mock_tado, errorRetringInterval)

    mock_logger.error.assert_called()
    mock_time.sleep.assert_called_with(errorRetringInterval)
    assert mock_tado.get_home_state.call_count == 2