"""
Recursively scan one or more given directories for duplicate files. 
Found duplicates list could be saved into report or printed out in console.

Also, duplicates could be moved into destination directory in safe way, 
preserving it relative path. In this case file name is written in the report, 
as well as new path for the file.
If empty sub-directories turn up after duplicates removal, the could be 
deleted as well.

Modules:

    core.py     - core functions: search for duplicates, move files,
                    log operations.
    argutils.py - command line argument parser, settings validation.

To use package without CLI, use:
from yadupe import core

To use package with CLI or settings validation, use:
from yadupe import argutils, core

"""

__version__ = "1.0.0"

__all__ = ['core', 'argutils']
