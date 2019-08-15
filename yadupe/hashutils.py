import typing
import os
import time
import io
import hashlib


_LAST_MTIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ%Z"


class SimpleKey(typing.NamedTuple):
    """ Simple key to associate with each file. """

    size: int
    lmtime: str

    def __eq__(self, other):
        return self.size == other.size and self.lmtime == other.lmtime

    @staticmethod
    def create(size: int, strtime: str):
        return SimpleKey(size, strtime)


def get_simple_key(filepath: str) -> SimpleKey:
    """ Return simple key for file based on size and latest modification time. """

    file_stat = os.stat(filepath)
    return SimpleKey(file_stat.st_size,
                     time.strftime(_LAST_MTIME_FORMAT, time.gmtime(file_stat.st_mtime)))


def file_chunks(filepath, chunksize=io.DEFAULT_BUFFER_SIZE) -> bytes:
    """ Read file by chunk """

    with open(filepath, 'rb') as openedfile:
        while True:
            data = openedfile.read(chunksize)
            if not data:
                break
            yield data


def hash_file(filepath: str) -> str:
    hash_obj = hashlib.blake2b()
    for chunk in file_chunks(filepath):
        hash_obj.update(chunk)
    return hash_obj.hexdigest()
