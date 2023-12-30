#
# Tado Auto-Assist for Geofencing and Open Window Detection
# Crated by Sören Schröder <code@razupaltuff.eu> on Dec, 27th 2023
# Rewrite of ado_aa.py by Adrian Slabu <adrianslabu@icloud.com> on 11.02.2021
# 

from PyTado.interface import Tado
from PyTado.exceptions import TadoWrongCredentialsException
from logger import Logger
import sys
import time

class TadoAutoAssist():
    errorRetringCounter = 0
    apiErrorRetringInterval = 30

    def __init__(self, username, password, apiErrorRetringInterval=30):
        self.apiErrorRetringInterval = apiErrorRetringInterval
        self.login(username, password)

    def login(self, username, password):
        try:
            self.tado = Tado(username, password)
            Logger.info("Connection established, everything looks good now, continuing...\n")
        
        except TadoWrongCredentialsException as e:
            Logger.error(str(e))
            sys.exit(0)

        except KeyboardInterrupt:
            Logger.warning("Interrupted by user")
            sys.exit(0)

        except Exception as e:
            self._processConnectionError(e, username, password)

    def _processConnectionError(self, e, username, password):
        Logger.error(f"{str(e)}\nConnection Error, retrying in {str(self.apiErrorRetringInterval)} sec...")
        time.sleep(self.apiErrorRetringInterval)
        self.login(username, password)


    
