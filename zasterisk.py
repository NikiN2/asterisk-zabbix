#!/usr/bin/python
import pexpect
import time
import sys
import posix_ipc
from optparse import OptionParser, OptionGroup

parser = OptionParser("usage=%prog [options] filename", version="%prog 0.1")
parser.add_option("--channelsactive", action="store_true", dest="channelsactive", help="Print the total number of channels active.")
parser.add_option("--callsactive", action="store_true", dest="callsactive", help="Print the total number of active calls.")
parser.add_option("--agents", action="store_true", dest="agents", help="Lists agents and their status.")
parser.add_option("--coresettings", action="store_true", dest="coresettings", help="Show PBX core settings (version etc)")
parser.add_option("--coreshowchannels", action="store_true", dest="coreshowchannels", help="List currently defined channels and some information about them.")
parser.add_option("--corestatus", action="store_true", dest="corestatus", help="Query for Core PBX status.")
parser.add_option("--dahdishowchannels", action="store_true", dest="dahdishowchannels", help="Show status of DAHDI channels.")
parser.add_option("--iaxregistry", action="store_true", dest="iaxregistry", help="Show IAX registrations.")
parser.add_option("--iaxpeers", action="store_true", dest="iaxpeers", help="List IAX peers.")
parser.add_option("--mailboxcount", action="store_true", dest="mailboxcount", help="Checks a voicemail account for new messages. Returns number of urgent, new and old messages. Need Mailbox specified.")
parser.add_option("--mailboxstatus", action="store_true", dest="mailboxstatus", help="Checks a voicemail account for status.")
parser.add_option("--meetmelist", action="store_true", dest="meetmelist", help="Lists all users in a particular MeetMe conference.")
parser.add_option("--parkedcalls", action="store_true", dest="parkedcalls", help="List parked calls.")
parser.add_option("--queuerule", action="store_true", dest="queuerule", help="Print the Queue Rules")
parser.add_option("--queuesummary", action="store_true", dest="queuesummary", help="Show queue summary.")
parser.add_option("--queuestatus", action="store_true", dest="queuestatus", help="Show queue status")
parser.add_option("--showdialplan", action="store_true", dest="showdialplan", help="Show dialplan contexts and extensions. Be aware that showing the full dialplan may take a lot of capacity.")
parser.add_option("--sippeers", action="store_true", dest="sippeers", help="Lists SIP peers in text format with details on current status.")
parser.add_option("--sipqualifypeer", action="store_true", dest="sipqualifypeer", help="Qualify a SIP peer.")
parser.add_option("--sipshowpeer", action="store_true", dest="sipshowpeer", help="Show one SIP peer with details on current status.")
parser.add_option("--sipshowregistry", action="store_true", dest="sipshowregistry", help="Lists all registration requests and status.")
parser.add_option("--voicemailuserslist", action="store_true", dest="voicemailuserslist", help="List All Voicemail User Information.")
parser.add_option("--confbridgelistrooms", action="store_true", dest="confbridgelistrooms", help="Lists data about all active conferences.")
parser.add_option("--confbridgelist", action="store_true", dest="confbridgelist", help="Lists all users in a particular ConfBridge conference.")
parser.add_option("--devicestatelist", action="store_true", dest="devicestatelist", help="This will list out all known device states in a sequence of DeviceStateChange events.")
parser.add_option("--extensionstatelist", action="store_true", dest="extensionstatelist", help="This will list out all known extension states in a sequence of ExtensionStatus events.")
parser.add_option("--faxstats", action="store_true", dest="faxstats", help="Responds with fax statistics")
parser.add_option("--pjsipqualify", action="store_true", dest="pjsipqualify", help="Qualify a chan_pjsip endpoint.")
parser.add_option("--pjsipshowendpoint", action="store_true", dest="pjsipshowendpoint", help="Detail listing of an endpoint and its objects.")
parser.add_option("--pjsipshowendpoints", action="store_true", dest="pjsipshowendpoints", help="Lists PJSIP endpoints.")
parser.add_option("--pjsipshowregistrationsinbound", action="store_true", dest="pjsipshowregistrationsinbound", help="Lists PJSIP inbound registrations.")
parser.add_option("--pjsipshowregistrationsoutbound", action="store_true", dest="pjsipshowregistrationsoutbound", help="Lists PJSIP outbound registrations.")
parser.add_option("--pjsipshowresourcelists", action="store_true", dest="pjsipshowresourcelists", help="Displays settings for configured resource lists.")
parser.add_option("--pjsipshowsubscriptionsinbound", action="store_true", dest="pjsipshowsubscriptionsinbound", help="Lists subscriptions.")
parser.add_option("--pjsipshowsubscriptionsoutbound", action="store_true", dest="pjsipshowsubscriptionsoutbound", help="Lists subscriptions.")
parser.add_option("--presencestate", action="store_true", dest="presencestate", help="Check Presence State.")
parser.add_option("--presencestatelist", action="store_true", dest="presencestatelist", help="List the current known presence states.")
parser.add_option("--prishowspans", action="store_true", dest="prishowspans", help="Show status of PRI spans.")

# Channel lists include up or down Skype channels

# Calls is not nearly as easy as it is in the CLI - show channels shows the number of calls, but the AMI doesn't show the number of calls, nor can it be discerned from the CoreShowChannels data. There's a workaround below, where the Channel has to be up to be considered live, and if two calls are bridged to each other, they are considered one call, but it's ugly.


USERNAME = 'zabbix'
PASSWORD = 'mahapharata'

(options, args) = parser.parse_args()

def connect_ami(semaphore):
    #TODO : Support astmanproxy or build own proxy to handle multiple simultaneous requests.
    semaphore.acquire()
    child=pexpect.spawn('telnet localhost 5038')
    child.logfile = sys.stdout
    child.expect("Asterisk Call Manager/1.3\r\n",timeout=1)
    child.setecho(False)
    child.sendline("Action: Login")
    child.sendline("ActionID: 1")
    child.sendline("Username: %s" % USERNAME)
    child.sendline("Secret: %s\r" % PASSWORD)
    child.expect("accepted\r",timeout=1)
    child.sendline("Action: Events")
    child.sendline("EventMask: Off\r")
    child.expect("Events: Off\r")
    return child

#def check_module(child,modulename):
#    modules = { 
#            "Skype" : 'chan_skype.so',
#            "G729" : 'codec_g729a.so',
#            }

#    module = modules[modulename]

#    child.sendline("Action: ModuleCheck")
#    child.sendline("Module: %s\r" % module)
#    i = child.expect(["Success\r","Error\r"])
#    if i == 0:
#        child.expect("Version: .+")
#        return True
#    else :
#        child.expect("Message: Module not loaded\r")
#        return False
#child = connect_ami(semaphore)
#child.interact()

semaphore=posix_ipc.Semaphore("/zasterisk",initial_value=1, flags=posix_ipc.O_CREAT)
try:

    if options.channelsactive:
        child = connect_ami(semaphore)
        child.sendline("Action: CoreShowChannels\r")
        child.expect('ListItems: \d+\r',timeout=1)
        result = child.after.split(' ')[1]

    elif options.agents:
        child = connect_ami(semaphore)
        child.sendline("Action: Agents\r")
        child.expect('Message: Agents will follow\r',timeout=1)
        child.expect('Event: AgentsComplete\r',timeout=1)
        child.expect('ListItems: \d+\r',timeout=1)
        result = child.after.split(' ')[1]

    elif options.coresettings:
        child = connect_ami(semaphore)
        child.sendline("Action: CoreSettings\r")
        child.expect('AsteriskVersion: \d+\r',timeout=1)
#        child.expect('AsteriskVersion: \d+\r',timeout=1)
        result = (child"")[1]


    elif options.callsactive:
        child = connect_ami(semaphore)
        child.sendline("Action: CoreShowChannels\r")
        child.expect('Message: Channels will follow\r',timeout=1)
        child.expect('Event: CoreShowChannelsComplete\r',timeout=1)
        to_parse = child.before[3:-3]
        child.expect('ListItems: \d+\r',timeout=1)
        if child.after.split(' ')[1] != "0\r":
            channels = to_parse.split('\n\r\n')
            callslist = []
            for c in channels:
                callslist.append([ e.split(': ') for e in c.split('\n') ])
    
            #This is crappy and I know it. Fix next time
            calls=[]
            for c in callslist:
                call = {}
                for v in c :
                    call[v[0]]=v[1].strip()
                calls.append(call)
    
            count = 0
            bridges=[]
    
            for c in calls:
                if c['ChannelStateDesc'] == 'Up' and c['BridgedChannel'] == '':
                    count = count + 1
                elif c['ChannelStateDesc'] == 'Down':
                    pass
                else :
                    id = c['UniqueID']
                    bid = c['BridgedUniqueID']
                    if bridges.count(id):
                        #ID already in here. Remove it and call it a call.
                        bridges.remove(id)
                        count = count + 1
                    else :
                        bridges.append(bid)
            result = count
        else:
            result = 0
        child.sendline("Action: Logoff\r")
        child.expect(pexpect.EOF,timeout=1)
        child.close
    else :
        parser.print_help() #Zabbix won't like this at all.
    semaphore.release()
    print result
except:
    print "Unexpected error:", sys.exc_info()
    semaphore.release()

#TODO:

