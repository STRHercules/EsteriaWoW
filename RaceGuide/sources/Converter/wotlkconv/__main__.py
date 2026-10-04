"""Allow ``python -m wotlkconv``."""

import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())
