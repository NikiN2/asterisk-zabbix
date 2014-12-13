# coding=utf-8
from zasterisk.base import BaseCommand


class Command(BaseCommand):
    help = '''
        SIP registrations
    '''

    def add_arguments(self, parser):
        parser.add_argument("--all", "-a", dest='discovery', action='store_true', help="Discovery trunks.")
        BaseCommand.add_arguments(self, parser)

    def discovery(self, ami):
        def callback(connect, timeout):
            events = self.parse_events(connect, "RegistryEntry")
            discovery = self.get_discovery(events, "{#TRUNKNAME}", "Username")
            self.stdout.write(discovery)

        ami.execute("SIPshowregistry", {}, callback)

    def handle(self, ami, *args, **options):
        discovery = options.get('discovery')
        if discovery:
            return self.discovery(ami)
