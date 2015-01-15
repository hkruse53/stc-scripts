import hashlib
import hmac

class Params:
    __slots__ = ("loc", "key", "format")

    def __init__(self, loc, key, format):
        assert len(loc[0]) <= 3
        assert loc[1] <= 9999
        assert key <= 999
        assert format <= 9999

        self.loc = loc
        self.key = key
        self.format = format

class Record:
    __slots__ = ("params", "date", "temp", "ph", "cond")

    def __init__(self, params, date, temp, ph, cond):
        assert -999.995 < temp < 999.995
        assert 0 < ph < 99.9995
        assert 0 < cond < 999999.995

        self.params = params
        self.date = date
        self.temp = temp
        self.ph = ph
        self.cond = cond

    def format_temp(self, temp):
        # This has to be done this way because python's format strings include
        # the +/- in the width of the field, where in the spec it says only the
        # number should be padded.
        return "{}{:6.2f}".format("-" if temp < 0 else "+", abs(temp))

    def format_loc(self):
        return "{:>3}{:>4}".format(*self.params.loc)

    def format_key(self):
        return "{:03}".format(self.params.key)

    def __str__(self):
        return "{}{}{:04}{}{}{:6.3f}{:9.2f}".format(
            self.format_loc(),
            self.format_key(),
            self.params.format,
            self.date.strftime("%Y-%m-%d %H:%M:%S+0000"),
            self.format_temp(self.temp),
            self.ph,
            self.cond
        )

class SignedRecord:
    __slots__ = ("record", "sig")

    def __init__(self, record, password):
        salt = "".join((record.format_loc(), record.format_key()))
        key = hashlib.pbkdf2_hmac("sha256", password.encode("ascii"),
            salt.encode("ascii"), 10000, 12)

        self.record = str(record)
        self.sig = hmac.new(key, self.record.encode("ascii"), hashlib.sha256)

    def __str__(self):
        return "".join((self.record, self.sig.hexdigest()))
