"""wotlkconv -- convert modern World of Warcraft assets to 3.3.5a (build 12340).

The package is import-safe with no third-party dependencies; the command line
entry point lives in :mod:`wotlkconv.cli`.
"""

from .limits import TARGET_BUILD, TARGET_PATCH
from .options import Options, TextureFormat, UnresolvedPolicy
from .report import FileResult, Report, Status

__version__ = "0.1.0"

__all__ = [
    "TARGET_BUILD",
    "TARGET_PATCH",
    "FileResult",
    "Options",
    "Report",
    "Status",
    "TextureFormat",
    "UnresolvedPolicy",
    "__version__",
]
