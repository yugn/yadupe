# Usage example: automatic duplicate search in HOME dir.

import sys
import os
from yadupe import core

def onscan(n: int):
    print(f'Starting duplicate search in {n} directories.')

def onprint(n: int):
    print(f'{n} duplicates found.')

PATH_TO_SEARCH_DUPLICATES = '.'

if __name__ == "__main__":
    # Parameters setup
    settings = core.Settings(False, 
                            '.',
                            [os.path.abspath(PATH_TO_SEARCH_DUPLICATES)],
                            False,
                            False)

    # simple progress information
    hooks = core.HookWrapper()
    hooks.beforescanhook = onscan
    hooks.beforereporthook = onprint

    # Search for duplicates.
    core.deduplicate(settings, hooks=hooks)
