import sys
import os
import pytest
from yadupe import hashutils

NO_FILE = 'aaaaaaaa'
SIMPLE_HASH_FILE = 'test-data/A/1.png'
SIMPLE_HASH_VALUE = "SimpleKey(size=175132, lmtime='2019-08-08T10:00:21ZGMT')"
SMALL_FILE = 'test-data/A/a/4.txt'
SMALL_FILE_SIZE = 325
SMALL_FILE_HASH = 'e6763eaf9633ef7d4e0e4f8206acabe846a71db1eaaa0a84b3b'\
                  'f591fead46b3da1f191e7cfd830eddd4e02a0e09962897cf7a5'\
                  '4db3cbd2726193500090e0b310'
EMPTY_FILE = 'test-data/A/a/4e.txt'


def test_simplekey_parameters():
    with pytest.raises(FileNotFoundError):
        hashutils.get_simple_key(os.path.abspath(NO_FILE))


def test_simplekey_value():
    sk = hashutils.get_simple_key(os.path.abspath(SIMPLE_HASH_FILE))
    assert str(sk) == SIMPLE_HASH_VALUE


def test_simplekey_creating():
    sk1 = hashutils.get_simple_key(os.path.abspath(SIMPLE_HASH_FILE))
    sk2 = hashutils.SimpleKey.create(sk1.size, sk1.lmtime)
    assert sk1 == sk2


def test_chunkreading_empty():
    total = 0
    for chunk in hashutils.file_chunks(os.path.abspath(EMPTY_FILE)):
        total += len(chunk)
    assert total == 0


def test_chunkreading():
    total = 0
    for chunk in hashutils.file_chunks(os.path.abspath(SMALL_FILE)):
        total += len(chunk)
    assert total == SMALL_FILE_SIZE


def test_hashing_invalid():
    with pytest.raises(FileNotFoundError):
        hashutils.hash_file(os.path.abspath(NO_FILE))


def test_hashing_value():
    h = hashutils.hash_file(os.path.abspath(SMALL_FILE))
    assert h == SMALL_FILE_HASH
