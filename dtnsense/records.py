import hashlib
import hmac

class Record:
    def fields(self):
        raise NotImplementedError

    def __str__(self):
        return "".join(self.fields())

class RecordFormat0001(Record):
    __slots__ = ["cfg", "date", "temp", "ph", "cond", "tz"]

    def __init__(self, cfg, date, temp, ph, cond, tz="+0000"):
        assert -999.995 < temp < 999.995
        assert 0 <= ph < 99.9995
        assert 0 <= cond < 999999.995

        self.cfg = cfg
        self.date = date
        self.temp = temp
        self.ph = ph
        self.cond = cond
        self.tz = tz

    def format_temp(self, temp):
        # This has to be done this way because python's format strings include
        # the +/- in the width of the field, where in the spec it says only the
        # number should be padded.
        return "{}{:6.2f}".format("-" if temp < 0 else "+", abs(temp))

    def fields(self):
        yield str(self.cfg.loc)
        yield str(self.cfg.key)
        yield str(self.cfg.fmt)
        yield self.date.strftime("%Y-%m-%d %H:%M:%S")
        yield self.tz
        yield self.format_temp(self.temp)
        yield "{:6.3f}".format(self.ph)
        yield "{:9.2f}".format(self.cond)

class RecordFormat0002(RecordFormat0001):
    def __init__(self, voltage, *args):
        super().__init__(*args)

        assert 0 <= voltage < 99.95
        self.voltage = voltage

    def fields(self):
        for field in super().fields():
            yield field

        yield "{:4.1f}".format(self.voltage)

class SignedRecord:
    __slots__ = ["record", "sig"]

    def __init__(self, cfg, record):
        self.record = str(record)
        self.sig = hmac.new(cfg.key.bytes,
            self.record.encode("ascii"), hashlib.sha256)

    def __str__(self):
        return "".join((self.record, self.sig.hexdigest()))
