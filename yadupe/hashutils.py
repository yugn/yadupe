import typing
import os
import io
import hashlib


class SimpleKey(typing.NamedTuple):
    """ Simple key to associate with each file. """

    size: int

    def __eq__(self, other):
        return self.size == other.size

    @staticmethod
    def create(size: int):
        return SimpleKey(size)


def get_simple_key(filepath: str) -> SimpleKey:
    """ Return simple key for file based on size. """

    file_stat = os.stat(filepath)
    return SimpleKey(file_stat.st_size)


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
