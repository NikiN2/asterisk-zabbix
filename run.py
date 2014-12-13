#!/usr/bin/env python
import os
import sys

from zasterisk.ami import TelnetAmi
from zasterisk import CommandUtility
from settings import *


if __name__ == "__main__":
    utility = CommandUtility(sys.argv)
    utility.register_path(os.path.join(os.path.dirname(__file__), "commands"))
    utility.register_path(os.path.join(os.path.dirname(__file__), "other_commands"))
    ami = TelnetAmi(HOST, PORT, USERNAME, PASSWORD)
    utility.execute(ami)
