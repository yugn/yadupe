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
from abc import ABC, abstractmethod
from utils import Settings, HookWrapper, NamedPath, _SimilarFiles, FilepathDict


__all__ = ['deduplicate']



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

"""
TODO 
сделать класс - интерфейс и иерархию классов, которые в зависимости от настроек settings будут разбираться со:
- сканированием одного или нескольких каталогов
- построением FilepathDict
- дополнением FilepathDict (для complement)
- подсчетом количества элементов для tqdm
- выполнением операции определенной в настройках
- созданием отчета об операции

Переделать тесты модулей core
"""
class FileProcessor(ABC):

    def __init__(self):
        self._file_data_dict = FilepathDict()

    @abstractmethod
    def scan_sources(self, sources: typing.List[str]) -> None:
        pass
    
    @abstractmethod
    def do_work(self, test_mode: bool) -> None:
        pass

    @abstractmethod
    def save_report(self, target: typing.TextIO) -> None:
        pass


class DedupeFileProcessor(FileProcessor):

    def scan_sources(self, sources: typing.List[str]) -> None:
        pass
    
    def do_work(self, test_mode: bool) -> None:
        pass

    def save_report(self, target: typing.TextIO) -> None:
        pass


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
            total_count = file_data_dict.duplicateslist_count()
        if settings.op_unique:
            total_count = file_data_dict.uniqueslist_count()
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