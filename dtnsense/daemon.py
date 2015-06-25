import argparse
import datetime
import os
import os.path
import socket
import stat
import sys
import time
import traceback

from dtnsense import batch, util

class Reader:
    def read(self):
        raise NotImplementedError

class Daemon:
    FLUSH_MSG = b"F"
    ACK_MSG = b"A"

    def __init__(self, sock_path, batcher, reader):
        self.sock_path = sock_path
        self.batcher = batcher
        self.reader = reader

    def read(self):
        self.batcher.add(str(self.reader.read()))

    def __enter__(self):
        try:
            os.unlink(self.sock_path)
        except FileNotFoundError:
            pass

        self.sock = socket.socket(socket.AF_UNIX)
        self.sock.bind(self.sock_path)

        mode = stat.S_IMODE(os.stat(self.sock_path).st_mode)
        os.chmod(self.sock_path, mode | stat.S_IWOTH)

        self.sock.listen(1)

        return self

    def __exit__(self, *args):
        self.sock.close()
        os.unlink(self.sock_path)

    def run(self, delay):
        # Read before sleeping.
        self.read()

        stop = time.time() + delay

        while True:
            remain = stop - time.time()

            if remain <= 0:
                break

            self.sock.settimeout(remain)

            try:
                conn, _ = self.sock.accept()
            except socket.timeout:
                break

            self.sock.settimeout(None)

            # Our messages are only one byte long at this point, so discard
            # any extra bytes.
            self.handle(conn, conn.recv(1))
            conn.close()

    def loop(self, delay):
        while True:
            try:
                self.run(delay)
            except KeyboardInterrupt:
                return
            except:
                traceback.print_exc()

    def ack(self, conn):
        conn.send(self.ACK_MSG)

    def handle(self, conn, msg):
        if msg == self.FLUSH_MSG:
            return self.batcher.flush()

        raise ValueError("invalid message {}".format(msg))

class Client:
    def __init__(self, sock_path):
        self.sock_path = sock_path

    def __enter__(self):
        self.sock = socket.socket(socket.AF_UNIX)
        self.sock.connect(self.sock_path)

        return self

    def __exit__(self, *args):
        self.sock.close()

    def send(self, msg):
        assert self.sock.send(msg) == len(msg)

    def wait(self):
        assert self.sock.recv(1) == Daemon.ACK_MSG

class Main:
    def __init__(self, argv, sock_path):
        self.sock_path = sock_path
        self.args = self.parse(argv)

        if self.args.no_gzip:
            formatter = batch.PlainFormatter()
        else:
            formatter = batch.GzipFormatter()

        if self.args.dry_run:
            handler = batch.StdoutHandler()
        else:
            handler = batch.DTN2Handler(self.args.expiration)

        self.batcher = batch.Batcher(formatter, handler, self.args.batch_size)

    def run(self):
        if self.args.flush:
            return self.flush()

        with util.GPIOGuard():
            self.batcher.check()
            self.daemonize()

    def daemon(self):
        raise NotImplementedError

    def daemonize(self):
        with self.daemon() as daemon:
            if self.args.delay is None:
                daemon.read()
            else:
                daemon.loop(self.args.delay)

    def flush(self):
        with Client(self.sock_path) as client:
            client.send(Daemon.FLUSH_MSG)

    def add_args(self, ap):
        ap.add_argument("-d", "--delay", action="store", type=int,
            help="seconds between readings (default: only read once)")
        ap.add_argument("-z", "--no-gzip", action="store_true",
            help="disable gzip compression of records batches (default: enabled)")
        ap.add_argument("-n", "--dry-run", action="store_true",
            help="don't send over DTN2, just print on stdout (default: no)")
        ap.add_argument("-e", "--expiration", action="store", default=90 * 24 * 60 * 60,
            help="set bundle expiration in seconds (default: %(default)s)")
        ap.add_argument("-b", "--batch-size", action="store", type=int, default=75,
            help="number of bundles to put in a batch (default: %(default)s)")
        ap.add_argument("-f", "--flush", action="store_true",
            help="flush any queued records")

    def parse(self, argv):
        ap = argparse.ArgumentParser()
        self.add_args(ap)

        return ap.parse_args(argv[1:])
