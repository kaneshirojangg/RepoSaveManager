"""Single source of truth for application theme tokens, typography, and small
style helpers. Every widget in ui/ should pull colors and fonts from here
instead of hardcoding hex values, so the whole app stays visually consistent."""

from __future__ import annotations


# ---------------------------------------------------------------------------
# Color palette
# ---------------------------------------------------------------------------
BG_PRIMARY = "#0A0A0A"
BG_SECONDARY = "#1A1A1A"
BG_CARD = "#171717"
BG_CARD_HOVER = "#232323"
BG_INPUT = "#141414"
BORDER = "#2A2A2A"

ACCENT = "#F5A623"
ACCENT_HOVER = "#D6900F"
ACCENT_MUTED = "#8A6224"

SUCCESS = "#3DDC84"
SUCCESS_BG = "#123023"
WARNING = "#F5A623"
WARNING_BG = "#332508"
DANGER = "#E24C4C"
DANGER_BG = "#301414"
NEUTRAL = "#6E6E6E"

TEXT_PRIMARY = "#F2F2F2"
TEXT_SECONDARY = "#9A9A9A"
TEXT_MUTED = "#6B6B6B"
TEXT_ON_ACCENT = "#1A1200"

# Backward-compatible alias: earlier revisions of this module exposed
# ACCENT_GLOW as a standalone token. Kept so any other module importing it
# directly does not break.
ACCENT_GLOW = ACCENT

# ---------------------------------------------------------------------------
# Typography
# ---------------------------------------------------------------------------
HEADER_FONT_FAMILY = "Oswald"
BODY_FONT_FAMILY = "Segoe UI"
MONO_FONT_FAMILY = "Consolas"

HEADER_FONT_WEIGHT = "bold"
BODY_FONT_WEIGHT = "normal"


def header_font(size: int = 18, weight: str = HEADER_FONT_WEIGHT) -> tuple[str, int, str]:
    """Bold condensed font for section titles / all-caps headers."""
    return (HEADER_FONT_FAMILY, size, weight)


def body_font(size: int = 13, weight: str = BODY_FONT_WEIGHT) -> tuple[str, int, str]:
    """Regular body text."""
    return (BODY_FONT_FAMILY, size, weight)


def mono_font(size: int = 12, weight: str = BODY_FONT_WEIGHT) -> tuple[str, int, str]:
    """Monospace-leaning font for the activity log / aligned data."""
    return (MONO_FONT_FAMILY, size, weight)


# ---------------------------------------------------------------------------
# Layout constants
# ---------------------------------------------------------------------------
PANEL_CORNER_RADIUS = 16
CARD_CORNER_RADIUS = 12
BADGE_CORNER_RADIUS = 8
BUTTON_CORNER_RADIUS = 10
PILL_CORNER_RADIUS = 999

# ---------------------------------------------------------------------------
# Small semantic icon glyphs (unicode, so no bundled asset is required)
# ---------------------------------------------------------------------------
ICON_SAVES = "\U0001F4C1"            # folder
ICON_BACKUPS_NEW = "\U0001F5C4"      # file cabinet
ICON_BACKUPS_UPDATED = "\U0001F504"  # refresh arrows
ICON_DELETIONS = "\u26A0"            # warning triangle
ICON_RESTORES = "\u267B"             # recycle / restore
ICON_RUNTIME = "\u23F1"              # stopwatch
ICON_SIZE = "\U0001F4BE"             # floppy disk
ICON_CLOCK = "\U0001F553"            # clock face
ICON_DOT = "\u25CF"                  # filled circle, used for status dots
ICON_SETTINGS = "\u2699"             # gear
ICON_MONITOR_ON = "\U0001F7E2"
ICON_MONITOR_OFF = "\u26AB"


def status_color(status: str) -> str:
    """Map a semantic status key to its accent color."""
    mapping = {
        "success": SUCCESS,
        "current": SUCCESS,
        "warning": WARNING,
        "outdated": WARNING,
        "danger": DANGER,
        "missing": DANGER,
        "none": DANGER,
        "info": TEXT_SECONDARY,
        "neutral": TEXT_SECONDARY,
    }
    return mapping.get(status, TEXT_SECONDARY)


def status_bg(status: str) -> str:
    mapping = {
        "success": SUCCESS_BG,
        "current": SUCCESS_BG,
        "warning": WARNING_BG,
        "outdated": WARNING_BG,
        "danger": DANGER_BG,
        "missing": DANGER_BG,
        "none": DANGER_BG,
    }
    return mapping.get(status, BG_CARD)


THEME_TOKENS = {
    "colors": {
        "bg_primary": BG_PRIMARY,
        "bg_secondary": BG_SECONDARY,
        "bg_card": BG_CARD,
        "bg_card_hover": BG_CARD_HOVER,
        "border": BORDER,
        "accent": ACCENT,
        "accent_hover": ACCENT_HOVER,
        "success": SUCCESS,
        "warning": WARNING,
        "danger": DANGER,
        "text_primary": TEXT_PRIMARY,
        "text_secondary": TEXT_SECONDARY,
        "text_muted": TEXT_MUTED,
    },
    "fonts": {
        "header_family": HEADER_FONT_FAMILY,
        "body_family": BODY_FONT_FAMILY,
        "mono_family": MONO_FONT_FAMILY,
        "header_weight": HEADER_FONT_WEIGHT,
        "body_weight": BODY_FONT_WEIGHT,
    },
}