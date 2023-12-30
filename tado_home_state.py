#
# Tado Auto-Assist for Geofencing and Open Window Detection
# Crated by Sören Schröder <code@razupaltuff.eu> on Dec, 27th 2023
# Rewrite of ado_aa.py by Adrian Slabu <adrianslabu@icloud.com> on 11.02.2021
# 

from logger import Logger

import time

class TadoHomeState():
    def __init__(self, tado, apiErrorRetringInterval = 30):
        self.tado = tado
        self.currentState = 'UNKNOWN'
        self.anyoneIsHome = None
        self.apiErrorRetringInterval = apiErrorRetringInterval
        self._intiate_state()

    def _intiate_state(self):
        self.updateHomeState()

    def updateHomeState(self):
        try:
            self.currentState = self.tado.get_home_state()["presence"]
            devices = self.tado.get_mobile_devices()
            locationEnabledDevices = self._getLocationEnabledDevices(devices)
            devicesAtHome = self._getDevicesAtHome(locationEnabledDevices)
            self.anyoneIsHome = len(devicesAtHome) > 0

            if (self.anyoneIsHome):
                if (self.currentState == 'AWAY'):
                    self._setStateToHome(devicesAtHome)
                else:
                    Logger.info("Your home is in HOME 🏠 Mode since the following devices are at home:")
                    for device in devicesAtHome:
                        Logger.info(f"• {device}")

            elif (not self.anyoneIsHome):
                if (self.currentState == 'HOME'):
                    self._setStateToAway()
                    pass
                else:
                    Logger.info("Your home is in AWAY 🚶 Mode and are no devices at home.")

        except Exception as e:
            if (str(e).find("location") != -1):
                Logger.warning("I cannot get the location of one of the devices because the Geofencing is off or the user signed out from tado app.\nWaiting for the device location, until then the Geofencing Assist is NOT active.\nWaiting for an open window..")
            else:
                self._processConnectionError(e)

        # devicesAtHome.clear()

    def _processConnectionError(self, e):
        Logger.error(f"{str(e)}\nConnection Error, retrying in {str(self.apiErrorRetringInterval)} sec...")
        time.sleep(self.apiErrorRetringInterval)
        self.updateHomeState()

    def _getLocationEnabledDevices(self, devices):
        deviceHasLocation = lambda device: device["settings"]["geoTrackingEnabled"] == True
        locationEnabledDevices = list(filter(deviceHasLocation, devices))
        return locationEnabledDevices

    def _getDevicesAtHome(self, locationEnabledDevices):
        deviceIsAtHome = lambda d: d["location"]["atHome"] == True
        devicesAtHome = list(filter(deviceIsAtHome, locationEnabledDevices))
        return devicesAtHome

    def _setStateToAway(self):
        Logger.info("Your home is in HOME 🏠 Mode but are no devices at home.")
        Logger.info("Activating AWAY mode 🚶🏠")
        self.tado.set_away()
        Logger.info("Done ✅")

    def _setStateToHome(self, devicesAtHome):
        Logger.info("Your home is in AWAY 🚶 Mode but the fllowing devices are at home:")
        for device in devicesAtHome:
            Logger.info(f"• {device}")
        Logger.info("Activating HOME mode 🏠🚶")
        self.tado.set_home()
        Logger.info("Done ✅")