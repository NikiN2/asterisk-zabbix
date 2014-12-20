# coding=utf-8
from zasterisk.base import DiscoveryFieldCommand


class Command(DiscoveryFieldCommand):
    help = '''
        SIP registrations
    '''

    def discovery(self, ami):
        def callback(connect, timeout):
            events = self.parse_events(connect, "RegistryEntry")
            return self.create_discovery(events, "{#TRUNKNAME}", "Username")

        return ami.execute("SIPshowregistry", {}, callback)

    def get_field(self, ami, field_name, param):
        def callback(connect, timeout):
            events = self.parse_events(connect, "RegistryEntry")
            for event in events:
                if event.get("Username") == param:
                    return event.get(field_name)
        result = ami.execute("SIPshowregistry", {}, callback)
        if not result:
            return "Field '%s' not found" % field_name
        return result
