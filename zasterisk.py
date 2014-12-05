#!/usr/bin/env python
from argparse import ArgumentParser
import pexpect
import sys

USERNAME = "zabbix"
PASSWORD = "mahapharata"

if __name__ == "__main__":
    child=pexpect.spawn('telnet 93.191.8.67 5038')
    child.logfile = sys.stdout

    child.expect("Asterisk Call Manager/1.3\r\n", timeout=1)
    child.setecho(False)
    child.sendline("Action: Login")
    child.sendline("ActionID: 1")
    child.sendline("Username: %s" % USERNAME)
    child.sendline("Secret: %s\r" % PASSWORD)
    child.expect("Authentication accepted\r", timeout=1)

    child.sendline("Action: Events")
    child.sendline("EventMask: Off\r")
    child.expect("Events: Off\r")

    child.sendline("Action: Ping\r")



    #child.expect("Pong\r", timeout=1)
    child.expect_list(["Timestamp: (.*)\r",], timeout=2)

    print child.after
    #parser = ArgumentParser(usage="%prog [options] filename", version="%prog 0.1")

    #args = parser.parse_args()
