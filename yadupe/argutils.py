import sys
import os
import typing
import argparse
from configparser import ConfigParser
import shlex
from .core import Settings


def parse_arguments(parameter_list: str = '') -> Settings:
    """ Parse argument list, return parameters.
    """

    arg_parser = argparse.ArgumentParser(
        prog='yadupe',
        description=sys.modules['yadupe.core'].__doc__)
    arg_parser.add_argument('source', nargs='+',
                            help='Source path to search duplicated files.',
                            metavar='PATH')
    arg_parser.add_argument('-d', '--deduplicate',
                            help='Scan and remove mode. Duplicates will be moved into given \
                                directory.',
                            action='store_true', dest='deduplicate')
    arg_parser.add_argument('-u', '--unique',
                            help='Scan and move mode. Unique files will be moved into given \
                                directory.',
                            action='store_true', dest='unique')
    arg_parser.add_argument('-p', '--purge',
                            help='Remove empty subdirs after duplicates move.',
                            action='store_true', dest='rem_empty')
    arg_parser.add_argument('-r', '--result',
                            help='Path to report dir (optional for default search mode) OR \
                                directory to move duplicated files into.',
                            metavar='PATH')
    args = arg_parser.parse_args(
        parameter_list if len(parameter_list) else None)

    return Settings(args.deduplicate,
                    args.unique,
                    args.result,
                    args.source,
                    args.rem_empty,
                    False)


def verify_settings(arguments: Settings, make_abs_path: bool = True) -> Settings:
    """ Check parameters integrity. Load arguments from config file, if exist.
    Return valid argument set or raise exception.
    """

    if not arguments.dest_path is None:
        abspath = os.path.abspath(arguments.dest_path)

    if arguments.op_dedup and arguments.op_unique:
        raise  ValueError(
                f'Select exactly one mode: remove duplicates or move unique files.')

    if arguments.op_dedup or arguments.op_unique:
        # Arguments.dest_path must be directory path
        if arguments.dest_path is None or not os.path.isdir(abspath):
            raise ValueError(
                f'{arguments.dest_path}: must be valid path to directory.')
    else:
        if not arguments.dest_path is None:
            # Arguments.dest_path must be valid filepath for new file.
            rootname, _ = os.path.split(abspath)
            if not os.access(rootname, os.F_OK):
                raise ValueError(
                    f'{arguments.dest_path} must be valid path to file to create.')

    isrelative = False
    for source in arguments.source:
        if not os.path.isdir(os.path.abspath(source)):
            raise ValueError(f'{source}: must be valid path to directory.')
        elif not os.path.isabs(source):
            isrelative = True

    if arguments.dest_path and not os.path.isabs(arguments.dest_path):
        isrelative = True

    resargs = None
    if isrelative and make_abs_path:
        sources = [src if os.path.isabs(src) else os.path.abspath(src)
                   for src in arguments.source]
        if arguments.dest_path:
            dest = os.path.abspath(arguments.dest_path)
        else:
            dest = None
        resargs = Settings(arguments.op_dedup,
                           arguments.op_unique,
                           dest,
                           sources,
                           arguments.remove_empty,
                           arguments.op_test)
    else:
        resargs = arguments

    return resargs
