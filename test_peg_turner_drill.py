"""Tests for peg_turner_drill.py — verify the drill-socket variant.

Confirms the reused stadium pocket still matches the TPU insert, and that the
hex shank has the right size, sits coaxial on top, and is printable."""

import math
import pytest
from build123d import *
from peg_turner_drill import (
    build_drill_socket,
    HEX_AF, HEX_RADIUS, SHANK_LENGTH,
    SOCKET_HEIGHT, DRILL_CAP, ROOF_HEIGHT,
)
from peg_turner import (
    TPU_LONG, TPU_SHORT, TPU_HEIGHT,
    SOCKET_LONG, SOCKET_SHORT, SOCKET_WALL,
    POCKET_DEPTH,
)

TOL = 0.15  # mm — geometric tolerance for bounding box checks


@pytest.fixture(scope="module")
def socket():
    return build_drill_socket()


# ─── Build Smoke ─────────────────────────────────────

def test_socket_builds(socket):
    assert socket is not None
    assert socket.volume > 0

def test_socket_is_solid(socket):
    assert len(socket.solids()) == 1


# ─── Overall Envelope ────────────────────────────────

def test_socket_bounding_box(socket):
    bb = socket.bounding_box()
    x_size = bb.max.X - bb.min.X
    y_size = bb.max.Y - bb.min.Y
    z_size = bb.max.Z - bb.min.Z
    # X/Y come from the stadium envelope (shank is much smaller)
    assert abs(x_size - SOCKET_LONG) < TOL, f"X={x_size}, expected {SOCKET_LONG}"
    assert abs(y_size - SOCKET_SHORT) < TOL, f"Y={y_size}, expected {SOCKET_SHORT}"
    # Z spans pocket bottom (z=0) through socket cap plus the hex shank
    expected_z = SOCKET_HEIGHT + SHANK_LENGTH
    assert abs(z_size - expected_z) < TOL, f"Z={z_size}, expected {expected_z}"

def test_pocket_opens_at_bottom(socket):
    """Pocket opens at z=0 (usage orientation: peg engagement at bottom)."""
    bb = socket.bounding_box()
    assert abs(bb.min.Z - 0.0) < TOL

def test_cap_houses_roof_with_shank_base():
    """Trimmed cap must fit the pyramid roof and leave solid base for the shank."""
    assert DRILL_CAP > ROOF_HEIGHT, "cap too short for the roof"
    assert DRILL_CAP - ROOF_HEIGHT >= 2.0, "too little solid cap under the shank base"


# ─── Reused Pocket Still Fits the TPU Insert ─────────

def test_pocket_matches_tpu_insert():
    """Reused pocket dimensions must still accept the shared TPU insert."""
    assert TPU_SHORT <= SOCKET_SHORT - 2 * SOCKET_WALL + TOL
    assert TPU_LONG <= SOCKET_LONG - 2 * SOCKET_WALL + TOL
    assert TPU_HEIGHT <= POCKET_DEPTH + TOL


# ─── Hex Shank ───────────────────────────────────────

def test_hex_circumradius_matches_across_flats():
    """Circumradius must yield the nominal 1/4" across-flats dimension."""
    af = HEX_RADIUS * math.sqrt(3)
    assert abs(af - HEX_AF) < 1e-6
    assert abs(HEX_AF - 6.35) < 1e-6  # 1/4" standard

def test_shank_is_coaxial(socket):
    """Hex shank must sit on the z-axis (centered over the socket)."""
    bb = socket.bounding_box()
    top_faces = [f for f in socket.faces() if abs(f.center().Z - bb.max.Z) < 0.1]
    assert top_faces, "no top face found"
    for f in top_faces:
        c = f.center()
        assert math.hypot(c.X, c.Y) < TOL, "shank tip not centered on z-axis"

def test_shank_tip_above_socket(socket):
    """Shank tip must clear the socket cap by the full shank length."""
    bb = socket.bounding_box()
    assert bb.max.Z >= SOCKET_HEIGHT + SHANK_LENGTH - TOL


# ─── Printability (No Supports) ──────────────────────

def test_shank_fits_within_socket_footprint():
    """Shank circumradius must be far smaller than the socket — narrows upward."""
    assert HEX_RADIUS < SOCKET_SHORT / 2
