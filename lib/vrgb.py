"""VRGB core encode/decode.

A Dimension is a named semantic axis anchored at a specific hue band. A value
in [0, 1] encodes to lightness within that band; hue is fixed by the dimension.
This keeps hex strings reversible *per dimension* and lets retrieval use hue
as the dimension address.

Saturation is held constant so the entire hex is interpretable: hue = which
dimension, lightness = where on it.
"""

from __future__ import annotations

import colorsys
from dataclasses import dataclass


_SAT = 0.70          # fixed saturation across all dimensions
_L_MIN = 0.15        # lightness floor (avoid pure black)
_L_MAX = 0.85        # lightness ceiling (avoid pure white)


@dataclass(frozen=True)
class Dimension:
    name: str
    low: str          # label at value = 0
    high: str         # label at value = 1
    hue: float        # 0-360, dimension anchor

    def label(self, value: float) -> str:
        v = max(0.0, min(1.0, value))
        if v < 0.2:
            return self.low
        if v < 0.4:
            return f"slightly {self.high}"
        if v < 0.6:
            return f"moderately {self.high}"
        if v < 0.8:
            return f"{self.high}"
        return f"very {self.high}"


def _hsl_to_hex(h_deg: float, s: float, l: float) -> str:
    r, g, b = colorsys.hls_to_rgb((h_deg % 360) / 360.0, l, s)
    return "#{:02x}{:02x}{:02x}".format(
        int(round(r * 255)), int(round(g * 255)), int(round(b * 255))
    )


def _hex_to_hsl(hex_str: str) -> tuple[float, float, float]:
    s = hex_str.lstrip("#")
    r = int(s[0:2], 16) / 255.0
    g = int(s[2:4], 16) / 255.0
    b = int(s[4:6], 16) / 255.0
    h, l, sat = colorsys.rgb_to_hls(r, g, b)
    return h * 360.0, sat, l


def encode(dim: Dimension, value: float) -> str:
    """Encode a 0..1 semantic value on dim to a hex string."""
    v = max(0.0, min(1.0, float(value)))
    l = _L_MIN + v * (_L_MAX - _L_MIN)
    return _hsl_to_hex(dim.hue, _SAT, l)


def decode(dim: Dimension, hex_str: str) -> tuple[float, str]:
    """Decode a hex under a known dimension back to (value, label)."""
    _, _, l = _hex_to_hsl(hex_str)
    v = (l - _L_MIN) / (_L_MAX - _L_MIN)
    v = max(0.0, min(1.0, v))
    return v, dim.label(v)


def midpoint(hex_a: str, hex_b: str) -> str:
    """Geometric midpoint in HSL. For same-dimension hexes this is just the
    lightness average; for cross-dimension hexes the hue takes a circular
    shortest-arc midpoint."""
    ha, sa, la = _hex_to_hsl(hex_a)
    hb, sb, lb = _hex_to_hsl(hex_b)
    diff = (hb - ha + 540) % 360 - 180
    hm = (ha + diff / 2) % 360
    return _hsl_to_hex(hm, (sa + sb) / 2, (la + lb) / 2)


def hue_distance(hex_a: str, hex_b: str) -> float:
    """Circular hue distance in degrees (0..180)."""
    ha, _, _ = _hex_to_hsl(hex_a)
    hb, _, _ = _hex_to_hsl(hex_b)
    d = abs(ha - hb) % 360
    return min(d, 360 - d)


# Canonical dimension catalog used across benchmarks.
DIMENSIONS: dict[str, Dimension] = {
    "urgency":    Dimension("urgency",    "casual",      "critical",   0),
    "confidence": Dimension("confidence", "uncertain",   "confident",  210),
    "risk":       Dimension("risk",       "safe",        "risky",      30),
    "priority":   Dimension("priority",   "low",         "high",       60),
    "clarity":    Dimension("clarity",    "unclear",     "clear",      180),
    "complexity": Dimension("complexity", "simple",      "complex",    270),
    "tone":       Dimension("tone",       "formal",      "casual",     150),
    "register":   Dimension("register",   "technical",   "plainspoken", 300),
}
