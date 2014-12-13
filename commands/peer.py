# coding=utf-8
from zasterisk.base import BaseCommand


class Command(BaseCommand):
    help = '''
        SIP peers
    '''

    def add_arguments(self, parser):
        parser.add_argument("--all", "-a", dest='discovery', action='store_true', help="Discovery users.")
        parser.add_argument("--field", "-f", dest='field', help="Return the name of the field")
        parser.add_argument("--name", "-n", dest='name', help="User name")
        BaseCommand.add_arguments(self, parser)

    def discovery(self, ami):
        def callback(connect, timeout):
            events = self.parse_events(connect, "PeerEntry")
            return self.get_discovery(events, "{#USERNAME}", "ObjectName")

        return ami.execute("SIPpeers", {}, callback)

    def get_field(self, ami, field_name, peer):
        return ami.execute("SIPshowpeer", {"Peer": peer},
                           lambda connect, timeout: self.expect_field(connect, field_name, timeout))

    def handle(self, ami, *args, **options):
        discovery = options.get('discovery')
        if discovery:
            self.stdout.write(self.discovery(ami))

        field = options.get('field')
        username = options.get("name")

        if field and username:
            self.stdout.write(self.get_field(ami, field, username))

'''
    Channeltype: SIP
    ObjectName: 103
    ChanObjectType: peer
    SecretExist: Y
    RemoteSecretExist: N
    MD5SecretExist: N
    Context: from-users
    Language: ru
    ToneZone: ru
    AMAflags: Unknown
    CID-CallingPres: Presentation Allowed, Not Screened
    Callgroup:
    Pickupgroup:
    Named Callgroup:
    Named Pickupgroup:
    MOHSuggest:
    VoiceMailbox: 103@users
    TransferMode: open
    LastMsgsSent: 0
    Maxforwards: 0
    Call-limit: 2
    Busy-level: 0
    MaxCallBR: 384 kbps
    Dynamic: Y
    Callerid: "" <103>
    RegExpire: 820 seconds
    SIP-AuthInsecure: port
    SIP-Forcerport: a
    SIP-Comedia: N
    ACL: Y
    SIP-CanReinvite: Y
    SIP-DirectMedia: Y
    SIP-PromiscRedir: N
    SIP-UserPhone: N
    SIP-VideoSupport: Y
    SIP-TextSupport: N
    SIP-T.38Support: N
    SIP-T.38EC: Unknown
    SIP-T.38MaxDtgrm: 4294967295
    SIP-Sess-Timers: Accept
    SIP-Sess-Refresh: uas
    SIP-Sess-Expires: 1800
    SIP-Sess-Min: 90
    SIP-RTP-Engine: asterisk
    SIP-Encryption: N
    SIP-DTMFmode: rfc2833
    ToHost:
    Address-IP: 192.168.30.174
    Address-Port: 5060
    Default-addr-IP: (null)
    Default-addr-port: 0
    Default-Username: 103
    Codecs: (ulaw|alaw|g729|g722)
    CodecOrder: g722,ulaw,alaw,g729
    Status: OK (19 ms)
    SIP-Useragent: Cisco/SPA504G-7.5.2
    Reg-Contact: sip:103@192.168.30.174:5060
    QualifyFreq: 60000 ms
    Parkinglot:
    SIP-Use-Reason-Header: N
    Description:
'''