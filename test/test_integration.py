import sys
import os
import re
import pytest
from yadupe import core

SOURCE_1 = 'test-data/A'
SOURCE_2 = 'test-data/B'
SOURCE_3 = 'test-data/C'
SOURCE_4 = 'test-data/D'
SOURCE_5 = 'test-data/E'
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
DUPLICATE_MOVE_TEMPLATE_8 = r'C/5.txt\s->\s(.+)/7_1.txt/5.txt'
DUPLICATE_MOVE_TEMPLATE_9 = r'C/3.txt\s->\s(.+)/7_1.txt/3.txt'
DUPLICATE_MOVE_TEMPLATE_10 = r'C/a/b/d/7.txt\s->\s(.+)/7_1.txt/a/b/d/7.txt'
DUPLICATE_MOVE_TEMPLATE_11 = r'D/a/b/1.txt\s->\s(.+)/7_1.txt/a/b/1.txt'
DUPLICATE_MOVE_TEMPLATE_12 = r'E/7.txt\s->\s(.+)/7_1.txt/7.txt'

FAKE_DUPLICATE_PATH_1 = r'A/b/8.txt'
FAKE_DUPLICATE_PATH_2 = r'C/11.txt'


UNIQUE_NAMES = ['Filename: 1.png','Filename: 3.txt','Filename: 8.txt',
                'Filename: 4.txt','Filename: 4e.txt','Filename: 7.txt',
                'Filename: 5.txt','Filename: 6.txt','Filename: 1.txt',
                'Filename: 11.txt','Filename: 2.txt', 'Filename: 5.txt',
                'Filename: 6.txt','Filename: 7.txt', 'Filename: 6.txt',
                'Filename: 2.txt', 'Filename: 1.txt', 'Filename: 4.txt']

UNIQUE_MOVE_TEMPLATES = [r'(A/1.png)(?:.|\s)*?->(?:.|\s)*?(res/1.png)', r'(A/3.txt)(?:.|\s)*?->(?:.|\s)*?(res/3.txt)',
                            r'(A/a/b/8.txt)(?:.|\s)*?->(?:.|\s)*?(res/8.txt)', r'(A/a/4.txt)(?:.|\s)*?->(?:.|\s)*?(res/4.txt)',
                            r'(A/a/4e.txt)(?:.|\s)*?->(?:.|\s)*?(res/4e.txt)', r'(A/a/b/7.txt)(?:.|\s)*?->(?:.|\s)*?(res/7.txt)',
                            r'(A/a/b/5.txt)(?:.|\s)*?->(?:.|\s)*?(res/5.txt)', r'(A/a/b/6.txt)(?:.|\s)*?->(?:.|\s)*?(res/6.txt)',
                            r'(B/1.txt)(?:.|\s)*?->(?:.|\s)*?(res/1.txt)', r'(C/11.txt)(?:.|\s)*?->(?:.|\s)*?(res/11.txt)',
                            r'(B/a/d/2.txt)(?:.|\s)*?->(?:.|\s)*?(res/2.txt)', r'(B/a/c/e/5.txt)(?:.|\s)*?->(?:.|\s)*?(res/5_1.txt)',
                            r'(B/a/c/e/6.txt)(?:.|\s)*?->(?:.|\s)*?(res/6_1.txt)', r'(B/a/c/e/f/7.txt)(?:.|\s)*?->(?:.|\s)*?(res/7_1.txt)',
                            r'(C/6.txt)(?:.|\s)*?->(?:.|\s)*?(res/6_2.txt)', r'(C/2.txt)(?:.|\s)*?->(?:.|\s)*?(res/2_1.txt)',
                            r'(C/1.txt)(?:.|\s)*?->(?:.|\s)*?(res/1_1.txt)', r'(C/4.txt)(?:.|\s)*?->(?:.|\s)*?(res/4_1.txt)']

FAKE_UNIQUE_NAMES = ['Filename: 9.txt','Filename: 42.txt','Filename: 10.txt']


def test_duplicatemove():
    settings = core.Settings(True,
                            False,
                             os.path.abspath(RESULT_DIR),
                             [os.path.abspath(path) for path in [
                                 SOURCE_1, SOURCE_2, SOURCE_3, SOURCE_4, SOURCE_5]],
                             False,
                             True)

    core.deduplicate(settings)

    report = ''
    with open(os.path.abspath(os.path.join(RESULT_DIR, 'report.txt')), 'r') as file:
        report = file.read()

    # check duplicate names 
    fulltext_templates = [DUPLICATE_NAME_1, DUPLICATE_NAME_2, DUPLICATE_NAME_3,
                          DUPLICATE_METADATA_1, DUPLICATE_METADATA_2, DUPLICATE_METADATA_3]
    for template in fulltext_templates:
        if template in report:
            continue
        else:
            assert False, f'{template} not found.'

    # check duplicate move
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

    # check fake duplicates
    fake_templates = [FAKE_DUPLICATE_PATH_1, FAKE_DUPLICATE_PATH_2]
    for template in fake_templates:
        if re.search(template, report):
            assert False, f'{template} found.'


def test_uniquemove():
    settings = core.Settings(False,
                            True,
                             os.path.abspath(RESULT_DIR),
                             [os.path.abspath(path) for path in [
                                 SOURCE_1, SOURCE_2, SOURCE_3, SOURCE_4, SOURCE_5]],
                             False,
                             True)

    core.deduplicate(settings)

    report = ''
    with open(os.path.abspath(os.path.join(RESULT_DIR, 'report.txt')), 'r') as file:
        report = file.read()

    # check unique names 
    for template in UNIQUE_NAMES:
        if template in report:
            continue
        else:
            assert False, f'{template} not found.'

    # check unique move
    for template in UNIQUE_MOVE_TEMPLATES:
        if re.search(template, report):
            continue
        else:
            assert False, f'{template} not found.'

    # check fake uniques
    for template in FAKE_UNIQUE_NAMES:
        if not template in report:
            continue
        else:
            assert False, f'{template} found.'