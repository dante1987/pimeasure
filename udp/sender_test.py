import sys
import socket

from constants import HOST, PORT


class AnotherSender(object):

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, data):
        self.socket.sendto(data, (self.host, self.port))


if __name__ == '__main__':
    if len(sys.argv) > 1:
        data_to_send = sys.argv[1]
    else:
        data_to_send = 'HELLO'

    sender = AnotherSender(HOST, PORT)
    sender.send(data_to_send)
