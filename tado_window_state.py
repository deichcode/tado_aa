from logger import Logger


class TadoWindowState:
    def __init__(self, tado) -> None:
        self.tado = tado

    def update(self):
        zones = self.tado.get_zones()
        for zone in zones:
            open_window_detected = self.tado.get_open_window_detect(zone["id"])["openWindowDetected"]
            if open_window_detected:
                Logger.info(zone["name"] + ": open window detected, activating the OpenWindow mode.")
                self.tado.set_open_window(zone["id"])
                Logger.info("Done!")
                Logger.info("Waiting for a change in devices location or for an open window..")
