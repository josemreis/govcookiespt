""" This file aims to demonstrate how to write custom commands in OpenWPM

Steps to have a custom command run as part of a CommandSequence

1. Create a class that derives from BaseCommand
2. Implement the execute method
3. Append it to the CommandSequence
4. Execute the CommandSequence

"""
import logging
import time
from datetime import datetime
from .constants import PATH_TO_OPENWPM, ACTIVE_STATUS_STOP, ACTIVE_STATUS_START
from selenium.webdriver import Firefox
import sys

sys.path.insert(0, PATH_TO_OPENWPM)
from openwpm.commands.types import BaseCommand
from openwpm.config import BrowserParams, ManagerParams
from openwpm.socket_interface import ClientSocket


class ScheduleManager(BaseCommand):
    """
    This command checks the current time of day, if below active status start time or above active status stop time,
    it will sleep until active time start
    """

    def __init__(self, active_time_start: int = ACTIVE_STATUS_START, active_time_stop: int = ACTIVE_STATUS_STOP) -> None:
        self.logger = logging.getLogger("openwpm")
        self.active_time_start = active_time_start
        self.active_time_stop = active_time_stop

    # While this is not strictly necessary, we use the repr of a command for logging
    # So not having a proper repr will make your logs a lot less useful
    def __repr__(self) -> str:
        return "ScheduleManager"

    # Have a look at openwpm.commands.types.BaseCommand.execute to see
    # an explanation of each parameter
    def execute(
        self,
        webdriver: Firefox,
        browser_params: BrowserParams,
        manager_params: ManagerParams,
        extension_socket: ClientSocket,
    ) -> None:
        hour_now = datetime.now().hour
        if hour_now < self.active_time_start or hour_now > self.active_time_stop:
            print(f"[!] It is {hour_now} o'clock. Will sleep until the next active start time at {self.active_time_start}")
            while abs(datetime.now().hour - self.active_time_start) != 0:
                time.sleep(1)
                print('...', end='', flush=True)