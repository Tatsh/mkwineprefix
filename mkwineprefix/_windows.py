"""Windows font/registry constants used by ``create_wine_prefix``."""

from __future__ import annotations

import enum


class Weight(enum.IntEnum):
    """
    The weight of the font in the range 0 through 1000.

    For example, 400 is normal and 700 is bold. If this value is zero, a default weight is used.
    These values are provided for convenience.
    """

    FW_BLACK = 900
    FW_BOLD = 700
    FW_DEMIBOLD = 600
    FW_DONTCARE = 0
    FW_EXTRABOLD = 800
    FW_EXTRALIGHT = 200
    FW_HEAVY = 900
    FW_LIGHT = 300
    FW_MEDIUM = 500
    FW_NORMAL = 400
    FW_REGULAR = 400
    FW_SEMIBOLD = 600
    FW_THIN = 100
    FW_ULTRABOLD = 800
    FW_ULTRALIGHT = 200


class ClipPrecision(enum.IntEnum):
    """
    The clipping precision.

    The clipping precision defines how to clip characters that are partially
    outside the clipping region.
    """

    CLIP_DEFAULT_PRECIS = 0x0
    """Specifies default clipping behaviour."""


class CharacterSet(enum.IntEnum):
    """
    The character set.

    Fonts with other character sets may exist in the operating system.
    """

    DEFAULT_CHARSET = 1
    """Based on the current system locale."""


class OutputPrecision(enum.IntEnum):
    """The output precision."""

    OUT_DEFAULT_PRECIS = 0
    """Specifies the default font mapper behaviour."""


class Pitch(enum.IntEnum):
    """The pitch and family of the font (low-order bits)."""

    VARIABLE_PITCH = 0x02


class Family(enum.IntEnum):
    """Font Family (bits 4 through 7)."""

    FF_SWISS = 0x20
    """Fonts with variable stroke width (proportional) and without serifs."""


class Quality(enum.IntEnum):
    """Output quality."""

    DEFAULT_QUALITY = 0
    """Appearance of the font does not matter."""


LF_FULLFACESIZE = 64
