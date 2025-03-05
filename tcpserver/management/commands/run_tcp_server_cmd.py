# tcpserver/management/commands/runtcpserver.py
from django.core.management.base import BaseCommand
from tcpserver.tcp_server import start_tcp_server

class Command(BaseCommand):
    help = 'Starts the TCP server'

    def handle(self, *args, **options):
        start_tcp_server('103.252.136.73', 9999)
