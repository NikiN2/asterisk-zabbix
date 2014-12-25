# coding=utf-8
from zasterisk.base import DiscoveryFieldCommand


class Command(DiscoveryFieldCommand):
    help = '''
        SIP queue
    '''

    def discovery(self, ami):
        def callback(connect, timeout):
            events = self.parse_events(connect, "Event: QueueStatusComplete")
            return self.create_discovery(events.get("QueueParams"), "{#QUEUENAME}", "Queue")

        return ami.execute("QueueStatus", {}, callback, False)

    def get_field(self, ami, field_name, param):
        def callback(connect, timeout):
            events = self.parse_events(connect, "Event: QueueStatusComplete").get("QueueParams")
            for event in events:
                if event.get("Queue") == param:
                    return event.get(field_name)

        result = ami.execute("QueueStatus", {}, callback)
        if not result:
            return "Field '%s' not found" % field_name
        return result

    def count(self, ami):
        return 0
