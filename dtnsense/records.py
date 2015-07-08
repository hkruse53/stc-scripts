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
        self.verify_temp(temp)
        self.verify_readings(ph, cond)

        self.cfg = cfg
        self.date = date
        self.temp = temp
        self.ph = ph
        self.cond = cond
        self.tz = tz

    def format_id(self):
        return 1

    def verify_temp(self, temp):
        assert -999.995 < temp < 999.995

    def verify_readings(self, ph, cond):
        assert 0 <= ph < 99.9995
        assert 0 <= cond < 999999.995

    def format_signed(self, fmt, num):
        # This has to be done this way because python's format strings include
        # the +/- in the width of the field, where in the spec it says only the
        # number should be padded.
        return "{}{}".format("-" if num < 0 else "+", fmt.format(abs(num)))

    def fields(self):
        yield str(self.cfg.loc)
        yield str(self.cfg.key)
        yield "{:04}".format(self.format_id())
        yield self.date.strftime("%Y-%m-%d %H:%M:%S")
        yield self.tz

        for field in self.reading_fields():
            yield field

    def temp_field(self):
        return self.format_signed("{:6.2f}", self.temp)

    def reading_fields(self):
        yield self.temp_field()
        yield "{:6.3f}".format(self.ph)
        yield "{:9.2f}".format(self.cond)

class RecordFormat0002(RecordFormat0001):
    def __init__(self, *args):
        super().__init__(*args)

    def verify_readings(self, ph, cond):
        assert -99.9995 < ph < 99.9995
        assert -999999.995 < cond < 999999.995

    def reading_fields(self):
        yield self.temp_field()
        yield self.format_signed("{:6.3f}", self.ph)
        yield self.format_signed("{:9.2f}", self.cond)

    def format_id(self):
        return 2

class RecordFormat0003(RecordFormat0002):
    def __init__(self, voltage, *args):
        super().__init__(*args)

        assert 0 <= voltage < 99.95
        self.voltage = voltage

    def format_id(self):
        return 3

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
