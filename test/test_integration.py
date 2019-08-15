import sys
import os
import re
import pytest
from yadupe import core

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


def test_duplicatemove():
    settings = core.Settings(True,
                             os.path.abspath(RESULT_DIR),
                             [os.path.abspath(path) for path in [
                                 SOURCE_1, SOURCE_2, SOURCE_3, SOURCE_4]],
                             False,
                             True)

    core.deduplicate(settings)

    report = ''
    with open(os.path.abspath(os.path.join(RESULT_DIR, 'report.txt')), 'r') as file:
        report = file.read()

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
