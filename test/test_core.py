import sys
import os
import io
import re
import pytest
from yadupe import core

FILEPATH_1 = 'test-data/A/2.txt'
FILEPATH_1EQ = 'test-data/A/3.txt'
FILEPATH_1NEQ = 'test-data/A/a/4.txt'

TESTDATA_PATH = 'test-data'
SOURCE_1 = 'test-data/A'
SOURCE_2 = 'test-data/B'
SOURCE_3 = 'test-data/C'
SOURCE_4 = 'test-data/D'
RESULT_DIR = 'test-data/res'

DUPLICATE_NAME_1 = 'Filename: 2.txt'
DUPLICATE_NAME_2 = 'Filename: 6.txt'
DUPLICATE_NAME_3 = 'Filename: 7.txt'

DUPLICATE_METADATA_1 = 'Size: 3432 byte, last modified: 2019-08-08T09:59:19ZGMT'
DUPLICATE_METADATA_2 = 'Size: 758 byte, last modified: 2019-08-08T10:05:43ZGMT'
DUPLICATE_METADATA_3 = 'Size: 29483 byte, last modified: 2019-08-08T10:30:11ZGMT'

DUPLICATE_MOVE_TEMPLATE_1 = r'A/3.txt\s->\s(.+)/2.txt/3.txt'
DUPLICATE_MOVE_TEMPLATE_2 = r'C/a/b/d/g/10.txt\s->\s(.+)/2.txt/a/b/d/g/10.txt'
DUPLICATE_MOVE_TEMPLATE_3 = r'C/a/b/d/e/8.txt\s->\s(.+)/2.txt/a/b/d/e/8.txt'
DUPLICATE_MOVE_TEMPLATE_4 = r'B/a/c/4.txt\s->\s(.+)/6.txt/a/c/4.txt'
DUPLICATE_MOVE_TEMPLATE_5 = r'B/a/c/e/f/8.txt\s->\s(.+)/6.txt/a/c/e/f/8.txt'
DUPLICATE_MOVE_TEMPLATE_6 = r'B/a/d/3.txt\s->\s(.+)/6.txt/a/d/3.txt'
DUPLICATE_MOVE_TEMPLATE_7 = r'C/a/b/d/f/9.txt\s->\s(.+)/6.txt/a/b/d/f/9.txt'
DUPLICATE_MOVE_TEMPLATE_8 = r'C/5.txt\s->\s(.+)/7.txt/5.txt'
DUPLICATE_MOVE_TEMPLATE_9 = r'C/3.txt\s->\s(.+)/7.txt/3.txt'
DUPLICATE_MOVE_TEMPLATE_10 = r'C/a/b/d/7.txt\s->\s(.+)/7.txt/a/b/d/7.txt'
DUPLICATE_MOVE_TEMPLATE_11 = r'D/a/b/1.txt\s->\s(.+)/7.txt/a/b/1.txt'

SHOW_FIRSTLINE = 'Duplicate list:'
SHOW_NAMELINE = 'Filename: 2.txt'
SHOW_ATTRLINE = 'Size: 3432 byte, last modified: 2019-08-08T09:59:19ZGMT'
SHOW_DUPNAME_1 = '2.txt'
SHOW_DUPNAME_2 = '3.txt'
SHOW_LASTLINE = 'End of list.'


@pytest.fixture
def namedpath_1():
    return core.NamedPath('keystring1', ['first_path', 'second_path', 'third_path'])


@pytest.fixture
def namedpath_1eq():
    return core.NamedPath('keystring1', ['first_path', 'second_path', 'third_path'])


@pytest.fixture
def namedpath_2():
    return core.NamedPath('keystring2', ['first_path', 'second_path', 'third_path'])


@pytest.fixture
def namedpath_3():
    return core.NamedPath('keystring1', ['first_path', 'second_path', ])


@pytest.fixture
def namedpath_4():
    return core.NamedPath('keystring1', ['first_path', 'second_path', 'another_third_path'])


def test_namedpath_eq(namedpath_1,
                      namedpath_1eq,
                      namedpath_2,
                      namedpath_3,
                      namedpath_4):

    assert namedpath_1 == namedpath_1eq
    assert namedpath_1 != namedpath_2
    assert namedpath_1 != namedpath_3
    assert namedpath_1 != namedpath_4


def test_similarfiles_eq():
    simfile_1 = core._SimilarFiles(FILEPATH_1)
    simfile_2 = core._SimilarFiles(FILEPATH_1)

    assert simfile_1 == simfile_2

    simfile_1.add(FILEPATH_1EQ)
    simfile_2.add(FILEPATH_1EQ)

    assert simfile_1 == simfile_2

    simfile_2.add(FILEPATH_1NEQ)
    assert simfile_1 != simfile_2


def test_filedict_eq():
    fd1 = core.FilepathDict()
    core._scan_duplicates(SOURCE_1, fd1)
    fd2 = core.FilepathDict()
    core._scan_duplicates(SOURCE_1, fd2)
    assert fd1 == fd2
    fd3 = core.FilepathDict()
    core._scan_duplicates(SOURCE_2, fd3)
    assert fd1 != fd3

    n1 = fd1.duplicateslist_count()
    n2 = fd2.duplicateslist_count()
    n3 = fd3.duplicateslist_count()

    assert n1 == n2
    assert n1 == n3


def test_print(capfd):
    fd1 = core.FilepathDict()
    core._scan_duplicates(SOURCE_1, fd1)
    fd1.print_duplicates()
    out = [line for line in capfd.readouterr()[0].split('\n') if line.strip()]

    assert out[0] == SHOW_FIRSTLINE
    assert out[1] == SHOW_NAMELINE
    assert out[2] == SHOW_ATTRLINE
    assert out[3].endswith(SHOW_DUPNAME_1)
    assert out[4].endswith(SHOW_DUPNAME_2)
    assert out[-1] == SHOW_LASTLINE


def test_duplicatemove():
    settings = core.Settings(True,
                             os.path.abspath(RESULT_DIR),
                             [os.path.abspath(path) for path in [
                                 SOURCE_1, SOURCE_2, SOURCE_3, SOURCE_4]],
                             False,
                             True)
    fd = core.FilepathDict()
    for el in settings.source:
        core._scan_duplicates(os.path.abspath(el), fd)
    fd = core._move_duplicates(fd,
                               settings.source,
                               settings.dest_path,
                               settings.op_test)
    report_buffer = io.StringIO()
    fd._save_duplicates_(target=report_buffer)
    report = report_buffer.getvalue()
    report_buffer.close()

    fulltext_templates = [DUPLICATE_NAME_1, DUPLICATE_NAME_2, DUPLICATE_NAME_3,
                          DUPLICATE_METADATA_1, DUPLICATE_METADATA_2, DUPLICATE_METADATA_3]
    for template in fulltext_templates:
        if template in report:
            continue
        else:
            assert False, f'{template} not found.'

    re_templates = [DUPLICATE_MOVE_TEMPLATE_1, DUPLICATE_MOVE_TEMPLATE_2,
                    DUPLICATE_MOVE_TEMPLATE_3, DUPLICATE_MOVE_TEMPLATE_4,
                    DUPLICATE_MOVE_TEMPLATE_5, DUPLICATE_MOVE_TEMPLATE_6,
                    DUPLICATE_MOVE_TEMPLATE_7, DUPLICATE_MOVE_TEMPLATE_8,
                    DUPLICATE_MOVE_TEMPLATE_9, DUPLICATE_MOVE_TEMPLATE_10,
                    DUPLICATE_MOVE_TEMPLATE_11]
    for template in re_templates:
        if re.search(template, report):
            continue
        else:
            assert False, f'{template} not found.'


def test_purgeempty():
    path = os.path.join(os.path.abspath(TESTDATA_PATH), 'emptytest/subdir')
    os.makedirs(path, exist_ok=True)
    assert os.access(path, os.F_OK)

    core._remove_empty_subdirs([path])
    assert not os.access(path, os.F_OK)
