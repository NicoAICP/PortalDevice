class Toy(object):
    def __init__(self, path):
        self.path = path

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path: str):
        with open(path, 'rb') as fp:
            self._data = fp.read()
        self._path = path

    @property
    def data(self):
        return self._data

    def readBlock(self, index: int):
        offset = index * 0x10
        length = offset + 0x10
        return self._data[offset:length]

    def writeBlock(self, index: int, block: bytes):
        offset = index * 0x10
        length = offset + len(block)
        self._data = self._data[0:offset] + block + self._data[length:]

    def save(self):
        with open(self.path, 'wb') as fp:
            fp.write(self._data)


class Slot(object):
    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, status: bool):
        self._active = status

    @property
    def toy(self):
        return self._toy

    @toy.setter
    def toy(self, toy: Toy):
        self._toy = toy

    def __init__(self, toy: Toy = None, active=False):
        self.toy = toy
        self.active = active
