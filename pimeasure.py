import argparse
import ConfigParser
import os.path
import sys
import datetime

import time

from demon.demon import Daemon

PID_FILE = '/users/krzysztofskarupa/Desktop/pimeasure_logs/pidfile.pid'
WORKDIR = '/users/krzysztofskarupa/Desktop/pimeasure_logs/'
STDOUT = '/users/krzysztofskarupa/Desktop/pimeasure_logs/stdout.txt'
STDERR = '/users/krzysztofskarupa/Desktop/pimeasure_logs/stderr.txt'
CONFIG_SECTION_NAME = 'general'
EXPECTED_CONFIG_KEYS = ('pidfile', 'workdir', 'stdout', 'stderr', 'communication_ip', 'communication_port',
                        'output_file')  # output file is only for test purpose


class PiMeasureDaemon(Daemon):
    def __init__(self, **kwargs):
        self.output_file = kwargs['output_file']
        self.communication_ip = kwargs['communication_ip']
        self.communication_port = kwargs['communication_port']
        del kwargs['output_file']
        del kwargs['communication_ip']
        del kwargs['communication_port']
        super(PiMeasureDaemon, self).__init__(**kwargs)

    def run(self):
        while True:
            time.sleep(2)
            today = datetime.datetime.today()
            with open(self.output_file, 'a') as the_file:
                the_file.write(today.strftime('%D %H:%M:%S\n'))


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
    for key in EXPECTED_CONFIG_KEYS:
        result.append((key, config.get(CONFIG_SECTION_NAME, key)))
    return dict(result)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Process config file path and command")
    parser.add_argument('--config', '-c', dest='config_path', help="Path to the config file", required=True)
    parser.add_argument('--command', '-d', dest='command', choices=['start', 'stop', 'restart'],
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

    if command == 'start':
        demon.start()
    elif command == 'stop':
        demon.stop()
    else:
        demon.restart()
