"""Exception hierarchy for the converter."""

from __future__ import annotations


class ConverterError(Exception):
    """Base class for every error raised by wotlkconv."""


class UnsupportedFormatError(ConverterError):
    """The input is a format (or format version) this tool cannot read."""


class TruncatedFileError(ConverterError):
    """The input ended earlier than its own headers claim."""


class MalformedFileError(ConverterError):
    """The input parsed structurally but contains impossible values."""


class ConversionError(ConverterError):
    """The input was understood but cannot be expressed in the 3.3.5a format."""


class MissingDependencyError(ConverterError):
    """Conversion needs an external input that was not supplied (e.g. a listfile)."""
