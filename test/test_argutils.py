import sys
import os
import pytest
from yadupe import argutils


CL_CORRECT_1 = '-d -p test-data/A test-data/B test-data/C test-data/D '\
    '-r test-data/res'

CORRECT_VALUE_1 = "True, test-data/res, ['test-data/A', 'test-data/B', "\
    "'test-data/C', 'test-data/D'], True, False"

CL_CORRECT_2 = '-d test-data/A test-data/B test-data/C test-data/D '\
    '-r test-data/res'

CORRECT_VALUE_2 = "True, test-data/res, ['test-data/A', 'test-data/B', "\
    "'test-data/C', 'test-data/D'], False, False"

CL_CORRECT_3 = 'test-data/A test-data/B test-data/C test-data/D '\
    '-r test-data/res/duplicates.txt'

CORRECT_VALUE_3 = "False, test-data/res/duplicates.txt, ['test-data/A', "\
    "'test-data/B', 'test-data/C', 'test-data/D'], False, False"

CL_CORRECT_4 = 'test-data/A test-data/B test-data/C test-data/D '

CORRECT_VALUE_4 = "False, None, ['test-data/A', 'test-data/B', 'test-data/C', "\
    "'test-data/D', ''], False, False"

CL_INCORRECT_1 = '-d -p test-data/A/1.png test-data/D '\
    '-r test-data/res'

ERROR_VALUE_1 = 'test-data/A/1.png: must be valid path to directory.'

CL_INCORRECT_2 = '-d -p test-data/E -r test-data/res'

ERROR_VALUE_2 = 'test-data/E: must be valid path to directory.'

CL_INCORRECT_3 = '-d -p test-data/A test-data/B test-data/C test-data/D '\
    '-r test-data/A/2.txt'

ERROR_VALUE_3 = 'test-data/A/2.txt: must be valid path to directory.'

CL_INCORRECT_4 = '-d -p test-data/A test-data/B test-data/C test-data/D '\
    '-r test-data/ress'

ERROR_VALUE_4 = 'test-data/ress: must be valid path to directory.'


def test_empty():
    with pytest.raises(SystemExit):
        argutils.parse_arguments('')


def parse_and_validate(input: str):
    args = input.split(' ')
    settings = argutils.parse_arguments(args)
    settings = argutils.verify_settings(settings)
    return settings


def test_incorrect_args():
    for i, o in zip([CL_INCORRECT_1, CL_INCORRECT_2, CL_INCORRECT_3, CL_INCORRECT_4],
                    [ERROR_VALUE_1, ERROR_VALUE_2, ERROR_VALUE_3, ERROR_VALUE_4]):
        with pytest.raises(ValueError) as exinfo:
            parse_and_validate(i)
        assert str(exinfo.value) == o


def test_correct_args():
    for i, o in zip([CL_CORRECT_1, CL_CORRECT_2, CL_CORRECT_3, CL_CORRECT_4],
                    [CORRECT_VALUE_1, CORRECT_VALUE_2, CORRECT_VALUE_3, CORRECT_VALUE_4]):
        settings = parse_and_validate(i)
        str_settings = f'{settings.op_dedup}, {settings.dest_path}, '\
            f'{settings.source}, {settings.remove_empty}, {settings.op_test}'
        assert str_settings == o
