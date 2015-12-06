import socket

from constants import PORT


class Listener(object):

    def __init__(self, port):
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def listen(self):
        self.socket.bind(("", PORT))
        print("Listening (class)")
        while True:
            data, host = self.socket.recvfrom(1024)
            print('{data} - {host}'.format(data=data, host=host))


if __name__ == '__main__':
    listener = Listener(PORT)
    listener.listen()
