#
# Tado Auto-Assist for Geofencing and Open Window Detection
# Crated by Sören Schröder <code@razupaltuff.eu> on Dec, 27th 2023
# Rewrite of ado_aa.py by Adrian Slabu <adrianslabu@icloud.com> on 11.02.2021
# 

from tado_auto_assist import TadoAutoAssist
from PyTado.exceptions import TadoWrongCredentialsException
import mock

username = 'user'
password = 'password'

@mock.patch("tado_auto_assist.Tado")
@mock.patch("tado_auto_assist.Logger")
def test_tado_successful_login(mock_logger, mock_tado):
    TadoAutoAssist(username, password)

    mock_tado.assert_called_with(username, password)
    mock_logger.info.assert_called()


@mock.patch("tado_auto_assist.Tado", side_effect=TadoWrongCredentialsException)
@mock.patch("tado_auto_assist.Logger")
@mock.patch("sys.exit")
def test_tado_log_error_on_wrong_credentials(mock_sys_exit, mock_logger, _):    
    TadoAutoAssist(username, 'wrong-password')

    mock_logger.error.assert_called()
    mock_sys_exit.assert_called_with(0)

@mock.patch("tado_auto_assist.Tado", side_effect=KeyboardInterrupt)
@mock.patch("tado_auto_assist.Logger")
@mock.patch("sys.exit")
def test_tado_log_warning_on_keyboard_interrupt(mock_sys_exit, mock_logger, _):    
    TadoAutoAssist(username, password)

    mock_logger.warning.assert_called()
    mock_sys_exit.assert_called_with(0)

@mock.patch("tado_auto_assist.Tado", side_effect=[Exception, None])
@mock.patch("tado_auto_assist.Logger")
@mock.patch("tado_auto_assist.time")
def test_tado_log_error_and_retry_on_other_exceptions(mock_time, mock_logger, mock_tado):    
    errorRetringInterval = 0
    TadoAutoAssist(username, password, errorRetringInterval)

    mock_logger.error.assert_called()
    assert mock_tado.call_count == 2
    mock_time.sleep.assert_called_with(errorRetringInterval)





#ToDo: Engine
#ToDo: Logger
