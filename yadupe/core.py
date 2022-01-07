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


class Settings(typing.NamedTuple):
    op_dedup: bool            # do deduplication
    op_unique: bool           # unique elements move
    dest_path: str            # path to destination dir, or report file
    source: typing.List[str]  # path to scan
    remove_empty: bool        # remove empty sub folders after deduplication (op_dedup == True only)
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

    @property
    def first_path(self):
        return self.path[0]

    @first_path.setter
    def first_path(self, value):
        self.path[0] = value
    


class _SimilarFiles(object):
    """ File path dictionary-based container, indexed by file content hash. 
    First added path stored w/o hashing.
    It will be hashed only on adding second path.
    So finally each key contains pathes for binary identical files.
    """

    def __init__(self, value: str):
        key = hash_file(value)
        self._pathes_ = {}
        self._pathes_[key] = NamedPath(os.path.basename(value), [value])


    def _add_(self, key: str, value: str):
        if key in self._pathes_.keys():
            self._pathes_[key].path.append(value)
        else:
            self._pathes_[key] = NamedPath(os.path.basename(value), [value])


    def add(self, extra_path: str) -> None:
        new_key = hash_file(extra_path)
        self._add_(new_key, extra_path)


    def duplicates(self) -> typing.Iterator[NamedPath]:
        """ Iterator, return each list of file path with equivalent hash values."""

        for key in self._pathes_.keys():
            if len(self._pathes_[key].path) > 1:
                yield self._pathes_[key]


    def uniques(self) -> typing.Iterator[NamedPath]:
        """ Iterator, return one path for each unique hash value. """
        for key in self._pathes_.keys():
            yield self._pathes_[key]

    def __eq__(self, other):
        if not len(self._pathes_.keys()) == len(other._pathes_.keys()):
            return False
        return self._pathes_ == other._pathes_

    def __ne__(self, other):
        return not self.__eq__(other)


class FilepathDict(dict):
    """ Customized dictionary contains pairs {file-key : file-path-info}. 
    file-key - simple file key (size based)
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
        if hooks.beforereporthook and hooks.groups_count_cache > 0:
            hooks.beforereporthook(hooks.groups_count_cache)
        print('Duplicate list:', file=target)
        for sk in self.keys():
            for duplicates in self[sk].duplicates():
                print(f'Filename: {duplicates.name}', file=target)
                print(f'Size: {sk.size} byte',
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

    def _save_uniques_(self, target, hooks=HookWrapper()):
        if hooks.beforereporthook and hooks.groups_count_cache > 0:
            hooks.beforereporthook(hooks.groups_count_cache)
        print('Unique list:', file=target)
        for sk in self.keys():
            for unique in self[sk].uniques():
                print(f'Filename: {unique.name}', file=target)
                print(f'Size: {sk.size} byte', file=target)
                print(f'{unique.first_path}', file=target)
                if hooks.groupreportedhook:
                    hooks.groupreportedhook()
        print('End of list.', file=target)

    def print_uniques(self, hooks=HookWrapper()):
        self._save_uniques_(target=sys.stdout, hooks=hooks)

    def save_uniques(self, filepath: str, hooks=HookWrapper()):
        with open(filepath, 'wt') as fileout:
            self._save_uniques_(target=fileout, hooks=hooks)

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

    def uniqueslist_count(self):
        """ Count number of unique files in files_dict """
        total_cnt = 0
        for sk in self.keys():
            total_cnt += FilepathDict._iter_len(self[sk].uniques())
        return total_cnt


def _append_filename_id_(filename: str, id: int):
    name, ext = os.path.splitext(filename)
    return "{name}_{uid}{ext}".format(name=name, uid=id, ext=ext)


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

    if hooks.beforemovehook and hooks.groups_count_cache > 0:
        hooks.beforemovehook(hooks.groups_count_cache)

    for sk in files_dict.keys():
        for duplicates in files_dict[sk].duplicates():

            if duplicates.name in name_check_dict.keys():
                idx = name_check_dict[duplicates.name]
                shortname = _append_filename_id_(duplicates.name, idx)
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


def _move_uniques(files_dict: dict,
                sources: typing.List[str],
                dest: str,
                testmode=False,
                hooks=HookWrapper()):
    """ Move uniques into new location, log operation."""

    name_check_dict = {}

    if hooks.beforemovehook and hooks.groups_count_cache > 0:
        hooks.beforemovehook(hooks.groups_count_cache)

    for sk in files_dict.keys():
        
        for unique in files_dict[sk].uniques():

            if unique.name in name_check_dict.keys():
                idx = name_check_dict[unique.name]
                short_dest_name = _append_filename_id_(unique.name, idx)
                name_check_dict[unique.name] += 1
            else:
                name_check_dict[unique.name] = 1
                short_dest_name = unique.name
            full_dest_name = os.path.join(dest, short_dest_name)

            if not testmode:
                os.replace(unique.first_path, full_dest_name)

            # log file move operation
            unique.first_path = f'{unique.first_path} -> {full_dest_name}'

            if hooks.groupmovedhook:
                hooks.groupmovedhook()

    return files_dict


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
        total_count = 0
        if settings.op_dedup:
            file_data_dict.duplicateslist_count()
        if settings.op_unique:
            file_data_dict.uniqueslist_count()
        if total_count > 0:
            hooks.groups_count_cache = total_count

    if not (settings.op_dedup or settings.op_unique):
        # report result
        if settings.dest_path:
            file_data_dict.save_duplicates(filepath=os.path.join(os.path.abspath(settings.dest_path),
                                                                 'report.txt'), hooks=hooks)
        else:
            file_data_dict.print_duplicates(hooks=hooks)
    else:
        if settings.op_dedup:
            file_data_dict = _move_duplicates(file_data_dict,
                                            settings.source,
                                            settings.dest_path,
                                            settings.op_test,
                                            hooks=hooks)
        if settings.op_unique:
            file_data_dict = _move_uniques(file_data_dict,
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
        if settings.op_dedup:
            file_data_dict.save_duplicates(filepath=os.path.join(os.path.abspath(settings.dest_path),
                                                                'report.txt'), hooks=hooks)
        if settings.op_unique:
            file_data_dict.save_uniques(filepath=os.path.join(os.path.abspath(settings.dest_path),
                                                                'report.txt'), hooks=hooks)