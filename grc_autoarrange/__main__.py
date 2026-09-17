"""Allow ``python -m grc_autoarrange`` (used when re-launching under GNU Radio's interpreter)."""

import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())
