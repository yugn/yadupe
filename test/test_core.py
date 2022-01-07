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

DUPLICATE_NAME_1 = 'Filename: 3.txt'
DUPLICATE_NAME_2 = 'Filename: 6.txt'
DUPLICATE_NAME_3 = 'Filename: 7.txt'

DUPLICATE_METADATA_1 = 'Size: 3432 byte'
DUPLICATE_METADATA_2 = 'Size: 758 byte'
DUPLICATE_METADATA_3 = 'Size: 29483 byte'

DUPLICATE_MOVE_TEMPLATE_1 = r'A/2.txt\s->\s(.+)/3.txt/2.txt'
DUPLICATE_MOVE_TEMPLATE_2 = r'C/a/b/d/g/10.txt\s->\s(.+)/3.txt/a/b/d/g/10.txt'
DUPLICATE_MOVE_TEMPLATE_3 = r'C/a/b/d/e/8.txt\s->\s(.+)/3.txt/a/b/d/e/8.txt'
DUPLICATE_MOVE_TEMPLATE_4 = r'B/a/c/4.txt\s->\s(.+)/6.txt/a/c/4.txt'
DUPLICATE_MOVE_TEMPLATE_5 = r'B/a/c/e/f/8.txt\s->\s(.+)/6.txt/a/c/e/f/8.txt'
DUPLICATE_MOVE_TEMPLATE_6 = r'B/a/d/3.txt\s->\s(.+)/6.txt/a/d/3.txt'
DUPLICATE_MOVE_TEMPLATE_7 = r'C/a/b/d/f/9.txt\s->\s(.+)/6.txt/a/b/d/f/9.txt'
DUPLICATE_MOVE_TEMPLATE_8 = r'C/5.txt\s->\s(.+)/7.txt/5.txt'
DUPLICATE_MOVE_TEMPLATE_9 = r'C/3.txt\s->\s(.+)/7.txt/3.txt'
DUPLICATE_MOVE_TEMPLATE_10 = r'C/a/b/d/7.txt\s->\s(.+)/7.txt/a/b/d/7.txt'
DUPLICATE_MOVE_TEMPLATE_11 = r'D/a/b/1.txt\s->\s(.+)/7.txt/a/b/1.txt'

SHOW_DUPLICATE_REPORT_FIRSTLINE = 'Duplicate list:'
SHOW_DUPLICATE_REPORT_NAMELINE = 'Filename: 3.txt'
SHOW_DUPLICATE_REPORT_ATTRLINE = 'Size: 3432 byte'
SHOW_DUPLICATE_REPORT_DUPNAME_1 = '2.txt'
SHOW_DUPLICATE_REPORT_DUPNAME_2 = '3.txt'
SHOW_DUPLICATE_REPORT_LASTLINE = 'End of list.'

SHOW_UNIQUE_REPORT = ['Unique list:', 'Filename: 1.png', 'Size: 175132 byte',
                        'A/1.png', 'Filename: 3.txt', 'Size: 3432 byte', 'A/3.txt',
                        'Filename: 8.txt', 'Size: 3432 byte', '/A/a/b/8.txt',
                        'Filename: 4.txt', 'Size: 325 byte', '/A/a/4.txt',
                        'Filename: 4e.txt', 'Size: 0 byte', '/A/a/4e.txt',
                        'Filename: 7.txt', 'Size: 1558 byte', '/A/a/b/7.txt',
                        'Filename: 5.txt', 'Size: 2172 byte', '/A/a/b/5.txt', 
                        'Filename: 6.txt', 'Size: 758 byte', '/A/a/b/6.txt', 'End of list.']


UNIQUE_ENUM_TEMPLATE = r'.+(A/1.png).+\s.+(A/3.txt).+\s.+(A/a/b/8.txt).+\s.+(A/a/4.txt).+\s.+(A/a/4e.txt).+\s.+(A/a/b/7.txt).+\s.+(A/a/b/5.txt).+\s.+(A/a/b/6.txt)'
DUPLICATE_ENUM_TEMPLATE = r'(.?)(3.txt)\s(.+)(A/2.txt)'

UNIQUE_NAME_1 = 'Filename: 1.png'
UNIQUE_NAME_2 = 'Filename: 3.txt'
UNIQUE_NAME_3 = 'Filename: 8.txt'
UNIQUE_NAME_4 = 'Filename: 4.txt'
UNIQUE_NAME_5 = 'Filename: 4e.txt'
UNIQUE_NAME_6 = 'Filename: 7.txt'
UNIQUE_NAME_7 = 'Filename: 5.txt'
UNIQUE_NAME_8 = 'Filename: 6.txt'

UNIQUE_MOVE_TEMPLATE = r'(A/1.png)(?:.|\s)*?(A/3.txt)(?:.|\s)*?(A/a/b/8.txt)(?:.|\s)*?(A/a/4.txt)(?:.|\s)*?(A/a/4e.txt)(?:.|\s)*?(A/a/b/7.txt)(?:.|\s)*?(A/a/b/5.txt)(?:.|\s)*?(A/a/b/6.txt)'

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


def test_print_duplicates(capfd):
    fd1 = core.FilepathDict()
    core._scan_duplicates(SOURCE_1, fd1)
    fd1.print_duplicates()
    out = [line for line in capfd.readouterr()[0].split('\n') if line.strip()]

    assert out[0] == SHOW_DUPLICATE_REPORT_FIRSTLINE
    assert out[1] == SHOW_DUPLICATE_REPORT_NAMELINE
    assert out[2] == SHOW_DUPLICATE_REPORT_ATTRLINE
    assert out[3].endswith(SHOW_DUPLICATE_REPORT_DUPNAME_2)
    assert out[4].endswith(SHOW_DUPLICATE_REPORT_DUPNAME_1)
    assert out[-1] == SHOW_DUPLICATE_REPORT_LASTLINE


def test_print_uniques(capfd):
    fd1 = core.FilepathDict()
    core._scan_duplicates(SOURCE_1, fd1)
    fd1.print_uniques()
    out = [line for line in capfd.readouterr()[0].split('\n') if line.strip()]

    i = 0
    for s in out:
        if i in [3, 6, 9, 12, 15, 18, 21, 24]:
            assert s.endswith(SHOW_UNIQUE_REPORT[i])
        else:
            assert s == SHOW_UNIQUE_REPORT[i]
        i += 1


def test_duplucates_enamerator():
    settings = core.Settings(True,
                            False,
                            os.path.abspath(RESULT_DIR),
                            [os.path.abspath(path) for path in [SOURCE_1]],
                            False,
                            True)
    fd = core.FilepathDict()
    for el in settings.source:
        core._scan_duplicates(os.path.abspath(el), fd)

    report_buffer = io.StringIO()
    for sk in fd.keys():
        for duplicate in fd[sk].duplicates():
            print(f'{duplicate.name}', file=report_buffer)
            print(f'{duplicate.path}', file=report_buffer)
    report = report_buffer.getvalue()
    report_buffer.close()

    re_templates = [DUPLICATE_ENUM_TEMPLATE]
    for template in re_templates:
        if re.search(template, report):
            continue
        else:
            assert False, f'{template} not found.'


def test_unique_enamerator():
    settings = core.Settings(False,
                            True,
                            os.path.abspath(RESULT_DIR),
                            [os.path.abspath(path) for path in [SOURCE_1]],
                            False,
                            True)
    fd = core.FilepathDict()
    for el in settings.source:
        core._scan_duplicates(os.path.abspath(el), fd)

    report_buffer = io.StringIO()
    for sk in fd.keys():
        for unique in fd[sk].uniques():
            print(f'{unique}', file = report_buffer)
    report = report_buffer.getvalue()
    report_buffer.close()

    re_templates = [UNIQUE_ENUM_TEMPLATE]
    for template in re_templates:
        if re.search(template, report):
            continue
        else:
            assert False, f'{template} not found.'


def test_duplicatemove():
    settings = core.Settings(True,
                             False,
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


def test_uniquemove():
    settings = core.Settings(False,
                            True,
                            os.path.abspath(RESULT_DIR),
                            [os.path.abspath(path) for path in [
                                SOURCE_1]],
                            False,
                            True)
    fd = core.FilepathDict()
    for el in settings.source:
        core._scan_duplicates(os.path.abspath(el), fd)
    fd = core._move_uniques(fd,
                            settings.source,
                            settings.dest_path,
                            settings.op_test)
    report_buffer = io.StringIO()
    fd._save_uniques_(target=report_buffer)
    report = report_buffer.getvalue()
    report_buffer.close()

    fulltext_templates = [UNIQUE_NAME_1, UNIQUE_NAME_2, 
                        UNIQUE_NAME_3, UNIQUE_NAME_4,
                        UNIQUE_NAME_5, UNIQUE_NAME_6,
                        UNIQUE_NAME_7, UNIQUE_NAME_8]
    for template in fulltext_templates:
        if template in report:
            continue
        else:
            assert False, f'{template} not found.'

    re_templates = [UNIQUE_MOVE_TEMPLATE]
    for template in re_templates:
        if re.search(template, report):
            continue
        else:
            assert False, f'{template} not found.'
