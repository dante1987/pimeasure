import os.path
import ConfigParser
import argparse

from pimeasure import StatusDaemon, get_config_values, check_config


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

    status_demon = StatusDaemon(
        pidfile=status_pidfile,
        stdout=status_stdout,
        stderr=status_stderr,
        communication_ip=configuration['communication_ip'],
        communication_port=configuration['communication_port'],
    )

    status_demon.start()