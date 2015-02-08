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
        return "{:>3}{:>4}".format(self.params.loc[0],
                                   "{:03}".format(self.params.loc[1]))

    def __str__(self):
        return "{}{:03}{:04}{}{}{:6.3f}{:9.2f}".format(
            self.format_loc(),
            self.params.key,
            self.params.format,
            # The spec calls for a timezone offset, but python doesn't come with
            # timezone support and we will always use UTC, so this offset is
            # just hard-coded.
            self.date.strftime("%Y-%m-%d %H:%M:%S+0000"),
            self.format_temp(self.temp),
            self.ph,
            self.cond
        )

class SignedRecord:
    __slots__ = ("record", "sig")

    def __init__(self, record, key):
        self.record = str(record)
        self.sig = hmac.new(key, self.record.encode("ascii"), hashlib.sha256)

    def __str__(self):
        return "".join((self.record, self.sig.hexdigest()))

if __name__ == "__main__":
    import datetime
    params = Params(("HF", 95), 1, 1)
    record = Record(params, datetime.datetime(2014,10,27,13,0,0), 20.20, 4.123, 359.0)
    signed = SignedRecord(record, b'\xa8\x89z3!\xce\xd5~\x84W\xaf\xb7')
    assert str(signed) == " HF 09500100012014-10-27 13:00:00+0000+ 20.20 4.123   359.0086f61764d68c2ce234fe436bd9eb6a71c5817894f89647ef45e385086fe872ec"
