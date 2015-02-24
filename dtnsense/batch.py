import gzip
import os
import pathlib
import subprocess
import tempfile

class PlainFormatter:
    def format(self, records):
        return "\n".join(records).encode("utf8")

class GzipFormatter:
    def format(self, records):
        return gzip.compress("\n".join(records).encode("utf8"))

class DTN2Handler:
    def __init__(self, expiration):
        self.expiration = expiration

    def handle(self, buf):
        with tempfile.NamedTemporaryFile() as tf:
            tf.write(buf)
            tf.flush()

            self.send(tf.name)

    def send(self, path):
        return subprocess.call(["dtnsend",
            "-s", "dtn://pi.dtn",
            "-d", "dtn://yellow.dtn",
            "-t", "f",
            "-p", path,
            "-e", str(self.expiration),
        ])

class StdoutHandler:
    def handle(self, buf):
        print(buf.decode("utf8"))

class Batcher:
    BATCH_FILE = pathlib.Path(os.path.expanduser("~/.cache/batch.rec"))
    BATCH_NEW_FILE = pathlib.Path(os.path.expanduser("~/.cache/batch.rec.new"))

    def __init__(self, formatter, handler, batch_size):
        self.formatter = formatter
        self.handler = handler
        self.batch_size = batch_size

        self.records = []
        self.load()
        self.check()

    def load(self):
        if not self.BATCH_FILE.exists():
            return

        with self.BATCH_FILE.open("r") as buf:
            for line in buf:
                # Strip off the trailing newline.
                self.records.append(line[:-1])

    def check(self):
        if len(self.records) >= self.batch_size:
            self.enqueue()

    def enqueue(self):
        if not self.BATCH_NEW_FILE.exists():
            self.handler.handle(self.formatter.format(
                self.records[:self.batch_size]))

        self.records = self.records[self.batch_size:]

        with self.BATCH_NEW_FILE.open("w") as new:
            for record in self.records:
                new.write("{}\n".format(record))

        self.BATCH_NEW_FILE.rename(self.BATCH_FILE)

    def add(self, record):
        self.records.append(record)

        # It's possible to lose bundles if the pi crashes before exiting this.
        with self.BATCH_FILE.open("a") as buf:
            buf.write("{}\n".format(record))

        self.check()
