import ConfigParser
import argparse
import datetime
import os.path
import itertools
import socket
import sys
import time
from multiprocessing import Process

from demon.demon import Daemon
from rangefinder import rangefinder

CONFIG_SECTION_NAME = 'general'
EXPECTED_CONFIG_KEYS = ('pidfile', 'workdir', 'stdout', 'stderr', 'communication_ip', 'communication_port',
                        'time_intervals')
OPTIONAL_CONFIG_KEYS = ('log_file', 'logging_enabled', 'output_file')

STATUS_FILE = '/home/pi/status/statusfile.txt'


def send_values(to_send, communication_socket, communication_ip, communication_port):
    message = ';'.join(to_send)
    communication_socket.sendto(message, (communication_ip, communication_port))


def send_status_working(communication_socket, communication_ip, communication_port):
    to_send = ['state', '0', '1']
    send_values(to_send, communication_socket, communication_ip, communication_port)


def send_status_idle(communication_socket, communication_ip, communication_port):
    to_send = ['state', '0', '0']
    send_values(to_send, communication_socket, communication_ip, communication_port)


def set_status_working():
    with open(STATUS_FILE, 'w') as fil:
        fil.write('1')


def set_status_idle():
    with open(STATUS_FILE, 'w') as fil:
        fil.write('0')


def status_working(communication_socket, communication_ip, communication_port):
    set_status_working()
    send_status_working(communication_socket, communication_ip, communication_port)


def status_idle(communication_socket, communication_ip, communication_port):
    set_status_idle()
    send_status_idle(communication_socket, communication_ip, communication_port)


def get_time_intervals():
    return [1, 2, 3, 4, 5]


def continuous_measure(time_intervals, checksum, communication_data):
    # this method needs its own sender class to not have to communicate with the main process
    communication_socket = communication_data['socket']
    communication_ip = communication_data['ip']
    communication_port = communication_data['port']
    status_working(communication_socket, communication_ip, communication_port)

    results = rangefinder.get_all_distances()

    # while not any(result is not None for result in results):
    while all(result == 0 for result in results):
        time.sleep(0.1)
        results = rangefinder.get_all_distances()

    counter = 1

    for interval in time_intervals:
        counter += 1
        time.sleep(interval)
        results = ["%.3f" % result for result in rangefinder.get_all_distances()]
        to_send = ['1'] + list(results) + [checksum]
        send_values(to_send, communication_socket, communication_ip, communication_port)
    status_idle(communication_socket, communication_ip, communication_port)


class PiMeasureDaemon(Daemon):
    def __init__(self, **kwargs):
        self.output_file = kwargs['output_file']
        self.communication_ip = kwargs['communication_ip']
        self.communication_port = int(kwargs['communication_port'])
        self.time_intervals = [int(interval) for interval in kwargs['time_intervals'].split(',')]
        self.log_file = kwargs.get('log_file')
        self.logging_enabled = self.log_file is not None and bool(int(kwargs.get('logging_enabled', '0')))
        del kwargs['output_file']
        del kwargs['communication_ip']
        del kwargs['communication_port']
        del kwargs['time_intervals']
        del kwargs['logging_enabled']
        del kwargs['log_file']
        super(PiMeasureDaemon, self).__init__(**kwargs)

        # this and other pieces of code related to udp communication could go to separate mixin - for consideration
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.running_process = None

    def log(self, message):
        if not self.logging_enabled:
            return

        if not message.endswith('\n'):
            message = ''.join([message, '\n'])
        with open(self.log_file, 'a') as log_file:
            log_file.write(message)

    def send_values(self, to_send):
        message = ';'.join(to_send)
        self.socket.sendto(message, (self.communication_ip, self.communication_port))

    def action_single(self, checksum):
        self.log('Starting single')
        values = ["%.3f" % value for value in rangefinder.get_all_distances()]
        to_send = ['0'] + list(values) + [checksum]
        self.log('Sending values for single')
        self.send_values(to_send)

    # continuous?
    def action_continous(self, checksum):
        self.log('Starting continuous')
        if self.running_process is not None and self.running_process.is_alive():
            self.log('A process is already running - terminating it')
            self.running_process.terminate()
        communication_data = {
            'socket': self.socket,
            'ip': self.communication_ip,
            'port': self.communication_port,
        }
        process = Process(target=continuous_measure, args=(self.time_intervals, checksum, communication_data))
        self.log('Starting the process')
        process.start()

        self.running_process = process

    def dispatch(self, data):
        """
        :param string data:
        :return:
        """
        arguments = data.split(';')
        action_name = 'action_{}'.format(arguments[0])
        action_args = arguments[1:]

        if hasattr(self, action_name):
            return getattr(self, action_name)(*action_args)
        sys.stderr.write('Wrong method passed on the network: {}'.format(arguments[0]))

    def run(self):
        self.socket.bind(("", self.communication_port))
        self.log("Listening on port {port}".format(port=self.communication_port))
        # change to do here:
        # continuous measure should return process object here
        # do not join immediately - instead listen for data from network
        # if anything comes from the network, check if the process is alive - if it's still working, terminate
        # a sender class should be separated from this daemon and measuring functions should create their own senders
        self.log('Started')
        while True:
            self.log('iteration begins')
            data, host = self.socket.recvfrom(1024)
            self.log('Received a message: host: {host}, data: {data}'.format(host=host, data=data))
            self.dispatch(data)
            today = datetime.datetime.today()
            with open(self.output_file, 'a') as the_file:
                message = '{time} - {msg} - {host}'.format(time=today.strftime('%D %H:%M:%S\n'), msg=data, host=host)
                the_file.write(message)


class StatusDaemon(Daemon):
    time_interval = 10

    def __init__(self, **kwargs):
        self.communication_ip = kwargs['communication_ip']
        self.communication_port = kwargs['communication_port']
        del kwargs['communication_ip']
        del kwargs['communication_port']
        super(StatusDaemon, self).__init__(**kwargs)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def is_working(self):
        with open(STATUS_FILE, 'r') as fil:
            val = fil.read()
        if val == '0':
            return False
        elif val == '1':
            return True
        else:
            raise ValueError('The value is neither 0 nor 1 - {}'.format(val))

    def run(self):
        while True:
            time.sleep(self.time_interval)
            if self.is_working():
                send_status_working(self.socket, self.communication_ip, self.communication_port)
            else:
                send_status_idle(self.socket, self.communication_ip, self.communication_port)


def check_config(config):
    # check if there is required section in the config
    if not config.has_section(CONFIG_SECTION_NAME):
        raise ValueError('Given config file does not have "general" section!')

    # check if keys are present in the config
    expected_keys = set(EXPECTED_CONFIG_KEYS)
    config_keys = {item[0] for item in config.items(CONFIG_SECTION_NAME)}
    if not expected_keys.issubset(config_keys):
        missing_keys = expected_keys - config_keys
        raise AttributeError('Missing keys in config file: {}'.format(', '.join(missing_keys)))

    # check if paths in the config exist
    for key in ('pidfile', 'stdout', 'stderr'):
        path = os.path.split(config.get(CONFIG_SECTION_NAME, key))[0]
        if not os.path.exists(path):
            raise AttributeError('Path for {key} does not exist! Given path: {path}'.format(key=key, path=path))

    workdir_path = config.get(CONFIG_SECTION_NAME, 'workdir')
    if not os.path.exists(workdir_path):
        raise AttributeError('Path to workdir does not exist! Given path: {}'.format(workdir_path))

    # todo: validation of ip address


def get_config_values(config):
    """
    :param config: Config object
    :rtype: dict
    """
    result = []
    for key in itertools.chain(EXPECTED_CONFIG_KEYS, OPTIONAL_CONFIG_KEYS):
        result.append((key, config.get(CONFIG_SECTION_NAME, key)))
    return dict(result)


if __name__ == '__main__':

    status_dir = '/home/pi/status'
    status_pidfile = os.path.join(status_dir, 'pidfile.pid')
    status_stderr = os.path.join(status_dir, 'stderr.txt')
    status_stdout = os.path.join(status_dir, 'stdout.txt')

    parser = argparse.ArgumentParser(description="Process config file path and command")
    parser.add_argument('--config', '-c', dest='config_path', help="Path to the config file", required=True)
    parser.add_argument('--command', '-d', dest='command', choices=['start', 'stop', 'restart', 'status'],
                        help='Command: start, stop or restart', required=True)

    args = parser.parse_args()

    config_file_path = args.config_path
    command = args.command

    absolute_path = os.path.abspath(config_file_path)
    if not os.path.exists(absolute_path):
        print("Given config file does not exist! Provide valid file path.")
        sys.exit(1)

    configuration = ConfigParser.RawConfigParser()
    configuration.read(absolute_path)

    check_config(configuration)
    configuration = get_config_values(configuration)

    demon = PiMeasureDaemon(**configuration)
    status_demon = StatusDaemon(
        pidfile=status_pidfile,
        stdout=status_stdout,
        stderr=status_stderr,
        communication_ip=configuration['communication_ip'],
        communication_port=configuration['communication_port'],
    )

    if command == 'start':
        demon.start()
        status_demon.start()
    elif command == 'stop':
        demon.stop()
        status_demon.stop()
    elif command == 'status':
        is_running = demon.get_status()
        if is_running:
            print('The daemon is running')
        else:
            print('The daemon is not running')

        status_is_running = status_demon.get_status()
        if status_is_running:
            print('The status daemon is running')
        else:
            print('The status daemon is not running')
    else:
        demon.restart()
