#!/usr/bin/env python
import os
import sys

from zasterisk.ami import TelnetAmi
from zasterisk import CommandUtility
from zasterisk import settings


if __name__ == "__main__":
    utility = CommandUtility(sys.argv)
    utility.register_path(os.path.join(os.path.dirname(__file__), "commands"))
    utility.register_path(os.path.join(os.path.dirname(__file__), "other_commands"))
    ami = TelnetAmi(settings.HOST, settings.PORT, settings.USERNAME, settings.PASSWORD)
    utility.execute(ami)
