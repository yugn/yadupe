# Usage example: simple CLI application using package

import sys
from yadupe import argutils, core


if __name__ == "__main__":
    # Parse command line arguments.
    settings = argutils.parse_arguments()
    # Check parameters.
    try:
        settings = argutils.verify_settings(settings)
    except ValueError as ex:
        print(f'{ex}')
        exit()
    # Search for duplicates.
    core.deduplicate(settings)
