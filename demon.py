import os
import sys
import atexit
import time
from signal import SIGTERM


class Daemon(object):

    def __init__(
            self,
            pidfile,
            umask=0,
            workdir='/',
            stdin='/dev/null',
            stdout='/dev/null',
            stderr='/dev/null'
    ):

        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile
        self.umask = umask
        self.workdir = workdir

    def demonize(self):
        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0)
        except OSError, e:
            sys.stderr.write('Fork #1 failed: {} ({})'.format(e.errno, e.strerror))
            sys.exit(1)

        # decouple from parent environment
        os.chdir(self.workdir)
        os.setsid()
        os.umask(self.umask)

        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # exit second parent
                sys.exit(0)
        except OSError, e:
            sys.stderr.write('Fork #2 failed: {} ({})'.format(e.errno, e.strerror))
            sys.exit(1)

        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = open(self.stdin, 'r')
        so = open(self.stdout, 'a')
        se = open(self.stderr, 'a')
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        # write pidfile
        atexit.register(self.delete_pid_file)
        pid = str(os.getpid())

        with open(self.pidfile, 'w+') as pidfile:
            pidfile.write('{}\n'.format(pid))

    def delete_pid_file(self):
        if os.path.exists(self.pidfile):
            os.remove(self.pidfile)

    def _get_pid(self):
        """
        Open pidfile, if exists, read the PID and return it
        If no pidfile, return None
        :return: None if no pidfile, else PID
        """

        try:
            pf = open(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        return pid

    def start(self):
        pid = self._get_pid()

        if pid:
            message = 'pidfile {} already exists. Daemon is already running?'.format(self.pidfile)
            sys.stderr.write(message)
            sys.exit(1)

        self.demonize()
        self.run()

    def stop(self):
        pid = self._get_pid()

        if not pid:
            message = 'pidfile {} does not exist. The daemon is not running?'.format(self.pidfile)
            sys.stderr.write(message)
            return

        # kill the daemon process
        try:
            while True:
                os.kill(pid, SIGTERM)
                time.sleep(0.1)
        except OSError, err:
            err = str(err)
            if "No such process" in err:
                self.delete_pid_file()
            else:
                print(str(err))
                sys.exit(1)

    def restart(self):
        self.stop()
        self.start()

    def run(self):
        """
        Do the actual task of the daemon. This should be overridden by
        :return:
        """
        raise NotImplementedError
