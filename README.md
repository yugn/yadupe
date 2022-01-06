# yadupe

__*yadupe*__ is yet another tool to find and remove duplicate files in a system.
It will recursively read a source directories, looking for duplicate files. Two files considered as duplicates if they have same size and content, though they could have different names.

In search mode utility report duplicate files list.

In deduplicate mode utility move duplicate files into the given destination directory. Only one file among group of duplicates is kept in the source directory. Also, report file contained all paths for moved diplicates will be saved in the destination directory.

In the alternate mode utility move unique files into the given  destination. Only one file among group of duplicates is moved into destination directory.

## Prerequisites

* [Python 3.4+](http://www.python.org/)

* [tqdm](https://tqdm.github.io/)


## Install

```
% pip install yadupe
```

If you don't have pip it's also easy to install: https://pip.pypa.io/en/stable/installing/

When yadupe installed it is availble on the CLI:

```
% yadupe -h
```

## Usage

1. Search and remove duplicate files in directories */home/user/source_a*, */home/user/source_b*. Found duplicates will be moved into */home/user/duplicates*, as well as report regarding moved files. Empty subfolders in  *source_a* and  *source_b* removed also.

```
% yadupe /home/user/source_a /home/user/source_b -d -p -r /home/user/duplicates
```

2. Search duplicates in directory */home/user/source_a* and print duplicate list.

```
% yadupe /home/user/source_a
```

3. Search and move unique files in directories */home/user/source_a*, */home/user/source_b*. Found uniques will be moved into */home/user/uniques*, as well as report regarding moved files.

```
% yadupe /home/user/source_a /home/user/source_b -u -p -r /home/user/uniques
```

4. There are couple examples of using yadupe package in Python applications in the __*examples*__ directory.

## Options

```
% yadupe -h

usage: yadupe [-h] [-d] [-u] [-p] [-r PATH] PATH [PATH ...]

Recursively scan one or more given directories for duplicate files. Found
duplicates list could be saved into report or printed out in console. Also,
duplicates could be moved into destination directory in safe way, preserving
it relative path. In this case file name is written in the report, as well as
new path for the file. If empty sub-directories turn up after duplicates
removal, the could be deleted as well.

positional arguments:
  PATH                  Source path to search duplicated files.

optional arguments:
  -h, --help            show this help message and exit
  -d, --deduplicate     Scan and remove mode. Duplicates will be moved into
                        given directory.
  -u, --unique          Scan and move mode. Unique files will be moved into
                        given directory.
  -p, --purge           Remove empty subdirs after duplicates or uniques move.
  -r PATH, --result PATH
                        Path to report dir (optional for default search mode)
                        OR directory to move duplicated files into.
```

## Testing

To run unit tests in __*test*__ directory first unzip *test-data.zip* archive inside __*test-data*__ directory. It create required directory tree for tests.