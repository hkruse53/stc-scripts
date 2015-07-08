import codecs
import configparser

class Location:
    __slots__ = ["name", "id"]

    def __init__(self, name, id):
        assert len(name) <= 3
        assert len(id) <= 4

        self.name = name
        self.id = id

    def __str__(self):
        return "{:>3}{:>4}".format(self.name, self.id)

class Key:
    __slots__ = ["id", "bytes"]

    def __init__(self, id, bytes):
        assert id <= 999

        self.id = id
        self.bytes = bytes

    def __str__(self):
        return "{:03}".format(self.id)

class Config:
    __slots__ = ["path", "loc", "key"]

    def __init__(self, path):
        self.path = path
        self.reload()

    def reload(self):
        parser = configparser.ConfigParser()
        parser.read(self.path)

        self.loc = Location(parser["location"]["name"], parser["location"]["site"])
        self.key = Key(int(parser["signing"]["key_id"]),
                       codecs.decode(parser["signing"]["key"], "hex_codec"))
