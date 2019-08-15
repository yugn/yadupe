"""
Recursively scan one or more given directories for duplicate files. 
Found duplicates list could be saved into report or printed out in console.

Also, duplicates could be moved into destination directory in safe way, 
preserving it relative path. In this case file name is written in the report, 
as well as new path for the file.
If empty sub-directories turn up after duplicates removal, the could be 
deleted as well.

"""

import sys
import os
import typing
from .hashutils import SimpleKey, get_simple_key, hash_file
from collections import deque
from itertools import count


__all__ = ['Settings', 'NamedPath',
           'FilepathDict', 'HookWrapper', 'deduplicate']

_STUB_KEY_STRING = 'stub-key-string'


class Settings(typing.NamedTuple):
    op_dedup: bool            # do deduplication
    dest_path: str            # path to destination dir, or report file
    source: typing.List[str]  # path to scan
    remove_empty: bool        # remove empty sub folders after deduplication
    op_test: bool             # test mode: only report, no real file moving


class HookWrapper(object):
    """ Wrapper class for some useful hook function, available for progress measuring. 

    beforescanhook    - callable that will be called once at the beginning of duplicate search
                        in given source paths. The callable will be passed one argument: total 
                        number of source paths.

    pathscannedhook   - callable that will be called each time when another source path scanned.
                        The callable will be passed no arguments.

    beforemovehook    - callable that will be called once at the beginning of duplicate 
                        file moving.
                        The callable will be passed one arguments: total number of found 
                        groups of duplicates.

    groupmovedhook    - callable that will be called each time when group of duplicates
                        will be moved into destination.
                        The callable will be passed no arguments.

    beforepurgehook   - callable that will be called once before starting purge of 
                        source paths.
                        The callable will be passed no arguments.

    afterpurgedhook   - callable that will be called once after finishing purge of 
                        source paths.
                        The callable will be passed no arguments.

    beforereporthook  - callable that will be called once at the beginning of report save.
                        The callable will be passed one arguments: total number of found 
                        groups of duplicates.

    groupreportedhook - callable that wil be called each time after report another
                        group of duplicates into file.
                        The callable will be passed no arguments.
    """

    def __init__(self):
        self.beforescanhook: typing.Callable = None
        self.pathscannedhook: typing.Callable = None
        self.beforemovehook: typing.Callable = None
        self.groupmovedhook: typing.Callable = None
        self.beforepurgehook: typing.Callable = None
        self.afterpurgedhook: typing.Callable = None
        self.beforereporthook: typing.Callable = None
        self.groupreportedhook: typing.Callable = None
        self.groups_count_cache: int = 0


class NamedPath(typing.NamedTuple):
    """ File name and it's duplicate path list. """
    name: str
    path: typing.List[str]

    def __eq__(self, other):
        if self.name != other.name:
            return False
        elif len(self.path) != len(other.path):
            return False
        elif self.path != other.path:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)


class _SimilarFiles(object):
    """ File path dictionary-based container, indexed by file content hash. 
    First added path stored w/o hashing.
    It will be hashed only on adding second path.
    """

    def __init__(self, first_path: str):
        self._pathes_ = {_STUB_KEY_STRING: first_path}
        self._length_ = 1

    def _add_(self, key: str, value: str):
        if key in self._pathes_.keys():
            self._pathes_[key].path.append(value)
        else:
            self._pathes_[key] = NamedPath(os.path.basename(value), [value])

    def add(self, extra_path: str) -> None:
        if self._length_ == 1:
            first_path = self._pathes_.pop(_STUB_KEY_STRING)
            new_key = hash_file(first_path)
            self._add_(new_key, first_path)
            self._length_ += 1

        new_key = hash_file(extra_path)
        self._add_(new_key, extra_path)

    def duplicates(self) -> typing.Iterator[NamedPath]:
        """ Iterator, return each list of file path with equivalent hash values."""

        for key in self._pathes_.keys():
            if key == _STUB_KEY_STRING:
                continue
            if len(self._pathes_[key]) > 1:
                yield self._pathes_[key]

    def __eq__(self, other):
        if not len(self._pathes_.keys()) == len(other._pathes_.keys()):
            return False
        return self._pathes_ == other._pathes_

    def __ne__(self, other):
        return not self.__eq__(other)


class FilepathDict(dict):
    """ Customized dictionary contains pairs {file-key : file-path-info}. 
    file-key - simple file key (size + last modification time)
    file-path-info - object with multiply appropriate file path
    """

    def __setitem__(self, key, value):
        """ The very first value with associated key must be added, 
        subsequent values will be appened to exist value. """

        if not key in self:
            super().__setitem__(key, _SimilarFiles(value))
        else:
            super().__getitem__(key).add(value)

    def _save_duplicates_(self, target, hooks=HookWrapper()):
        if hooks.beforereporthook:
            hooks.beforereporthook(hooks.groups_count_cache)
        print('Duplicate list:', file=target)
        for sk in self.keys():
            for duplicates in self[sk].duplicates():
                print(f'Filename: {duplicates.name}', file=target)
                print(f'Size: {sk.size} byte, last modified: {sk.lmtime}',
                      file=target)
                for filepath in duplicates.path:
                    print(f'{filepath}', file=target)
                print('', file=target)
                if hooks.groupreportedhook:
                    hooks.groupreportedhook()
        print('End of list.', file=target)

    def print_duplicates(self, hooks=HookWrapper()):
        self._save_duplicates_(target=sys.stdout, hooks=hooks)

    def save_duplicates(self, filepath: str, hooks=HookWrapper()):
        with open(filepath, 'wt') as fileout:
            self._save_duplicates_(target=fileout, hooks=hooks)

    @staticmethod
    def _iter_len(it):
        """ Fast method to count iterable elements. """
        cnt = count()
        deque(zip(it, cnt), 0)
        return next(cnt)

    def duplicateslist_count(self):
        """ Count number of duplicate groups in files_dict """
        total_cnt = 0
        for sk in self.keys():
            total_cnt += FilepathDict._iter_len(self[sk].duplicates())
        return total_cnt


def _scan_duplicates(rootpath: str, files_dict: dict):
    """ Scan rootpath for duplicates. """

    if not os.path.isabs(rootpath):
        rootpath = os.path.abspath(rootpath)
    for dirpath, _, filenames in os.walk(rootpath):
        for filename in filenames:
            absfilename = os.path.join(dirpath, filename)
            key = get_simple_key(absfilename)
            files_dict[key] = absfilename


def _move_duplicates(files_dict: dict,
                     sources: typing.List[str],
                     dest: str,
                     testmode=False,
                     hooks=HookWrapper()):
    """ Move duplicates into new location, log operation."""

    name_check_dict = {}

    if hooks.beforemovehook:
        hooks.beforemovehook(hooks.groups_count_cache)

    for sk in files_dict.keys():
        for duplicates in files_dict[sk].duplicates():

            if duplicates.name in name_check_dict.keys():
                idx = name_check_dict[duplicates.name]
                shortname = f'{duplicates.name}_{idx}'
                name_check_dict[duplicates.name] += 1
            else:
                name_check_dict[duplicates.name] = 1
                shortname = duplicates.name
            shortname = os.path.join(dest, shortname)
            if not testmode:
                os.mkdir(shortname)

            idx = 1
            iters = iter(duplicates.path[1:])
            for filepath in iters:
                for src in sources:
                    if src == os.path.commonpath([src, filepath]):
                        destpath = os.path.relpath(filepath, src)
                        destpath = os.path.join(shortname, destpath)
                        if not testmode:
                            os.makedirs(os.path.dirname(
                                destpath), exist_ok=True)
                        # log file move operation
                        duplicates.path[idx] = f'{duplicates.path[idx]} -> {destpath}'
                        idx += 1
                        # move file
                        if not testmode:
                            os.replace(filepath, destpath)
                        break
            if hooks.groupmovedhook:
                hooks.groupmovedhook()
    return files_dict


def _remove_empty_subdirs(root=typing.List[str]):
    """ Remove empty subdirs recursively. """

    for dir in root:
        for dirpath, dirnames, files in os.walk(dir):
            if not (files or dirnames):
                os.removedirs(dirpath)


def deduplicate(settings: Settings, hooks=HookWrapper()):
    file_data_dict = FilepathDict()

    # search for duplicates
    if hooks.beforescanhook:
        hooks.beforescanhook(len(settings.source))

    for el in settings.source:
        _scan_duplicates(os.path.abspath(el), file_data_dict)
        if hooks.pathscannedhook:
            hooks.pathscannedhook()

    if hooks.beforereporthook or hooks.beforemovehook:
        hooks.groups_count_cache = file_data_dict.duplicateslist_count()

    if not settings.op_dedup:
        # report result
        if settings.dest_path:
            file_data_dict.save_duplicates(filepath=os.path.join(settings.dest_path,
                                                                 'report.txt'),
                                           hooks=hooks)
        else:
            file_data_dict.print_duplicates(hooks=hooks)
    else:
        file_data_dict = _move_duplicates(file_data_dict,
                                          settings.source,
                                          settings.dest_path,
                                          settings.op_test,
                                          hooks=hooks)

        # clean up empty sub-dirs in source
        if settings.remove_empty and not settings.op_test:
            if hooks.beforepurgehook:
                hooks.beforepurgehook()
            _remove_empty_subdirs(settings.source)
            if hooks.afterpurgedhook:
                hooks.afterpurgedhook()

        # save report
        file_data_dict.save_duplicates(filepath=os.path.join(settings.dest_path, 'report.txt'),
                                       hooks=hooks)
