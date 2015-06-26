import hashlib
import hmac

class Record:
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

    def __str__(self):
        return "{}{}{}{}{}{}{:6.3f}{:9.2f}".format(
            self.cfg.loc,
            self.cfg.key,
            self.cfg.fmt,
            self.date.strftime("%Y-%m-%d %H:%M:%S"),
            self.tz,
            self.format_temp(self.temp),
            self.ph,
            self.cond
        )

class SignedRecord:
    __slots__ = ["record", "sig"]

    def __init__(self, cfg, record):
        self.record = str(record)
        self.sig = hmac.new(cfg.key.bytes,
            self.record.encode("ascii"), hashlib.sha256)

    def __str__(self):
        return "".join((self.record, self.sig.hexdigest()))
