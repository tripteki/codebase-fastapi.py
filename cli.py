#!/usr/bin/env python3

import sys
from src.app.bases.app_console import AppConsole

def main ():
    """
    Args:
        None
    Returns:
        None
    """
    console = AppConsole ()
    exitCode = console.execute (sys.argv[1:])
    sys.exit (exitCode)

if __name__ == "__main__":
    main ()
