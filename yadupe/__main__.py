"""
Minimal CLI application to use yadupe as standalone software.

"""

import sys
import yadupe
from yadupe import argutils, core
import tqdm


def main():

    settings = argutils.parse_arguments()
    try:
        settings = argutils.verify_settings(settings)
    except ValueError as ex:
        print(f'{ex}')
        exit()

    progress = None
    max_progress = 0
    step = 0

    def progress_reset():
        if progress:
            progress.close()

    def progress_start(count: int, title: str):
        progress_reset()
        print(title)
        global progress
        progress = tqdm.tqdm(total=100)
        global max_progress
        max_progress = 100
        global step
        step = 100 / count

    def on_item_progress():
        global max_progress
        global step
        global progress
        if max_progress < (1.9 * step):
            step = max_progress
        progress.update(step)
        max_progress -= step

    def on_scan(count: int):
        progress_start(count, 'Search for duplicates:')

    def on_move(count: int):
        progress_start(count, 'Move duplicates:')

    def on_purge():
        progress_reset()
        print(f'Remove empty folders.')

    def on_report(count):
        progress_start(count, 'Save report:')

    hooks = core.HookWrapper()
    hooks.beforescanhook = on_scan
    hooks.pathscannedhook = on_item_progress
    hooks.beforemovehook = on_move
    hooks.groupmovedhook = on_item_progress
    hooks.beforepurgehook = on_purge
    hooks.beforereporthook = on_report
    hooks.groupreportedhook = on_item_progress

    core.deduplicate(settings, hooks)
    progress_reset()

if __name__ == "__main__":
    main()