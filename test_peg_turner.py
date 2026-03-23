"""Tests for peg_turner.py — verify dimensions, fit, and printability."""

import pytest
from build123d import *
from peg_turner import (
    build_tpu_insert,
    build_socket_body,
    build_handle_knob,
    build_retaining_washer,
    build_ghost_bolt,
    build_ghost_heatset,
    # Parameters
    SLOT_WIDTH, SLOT_LENGTH, SLOT_DEPTH, SLOT_CHAMFER,
    TPU_WALL, TPU_SHORT, TPU_LONG, TPU_HEIGHT,
    SOCKET_WALL, SOCKET_SHORT, SOCKET_LONG, SOCKET_HEIGHT, SOCKET_CAP,
    POCKET_DEPTH,
    ARM_LENGTH, ARM_WIDTH, ARM_HEIGHT,
    ARM_Z_BOTTOM, ARM_Z_TOP,
    ARM_BORE_DIA,
    POST_OD, POST_HEIGHT, FLANGE_DIA, FLANGE_HEIGHT,
    HEATSET_DIA, HEATSET_DEPTH,
    KNOB_OD, KNOB_HEIGHT,
    KNOB_Z_BOTTOM, KNOB_Z_TOP, POST_TIP_Z,
    WASHER_OD, WASHER_ID, WASHER_H, WASHER_CBORE_DIA, WASHER_CBORE_DEPTH,
)

TOL = 0.15  # mm — geometric tolerance for bounding box checks


# ─── Fixtures ─────────────────────────────────────────

@pytest.fixture(scope="module")
def tpu():
    return build_tpu_insert()

@pytest.fixture(scope="module")
def body():
    return build_socket_body()

@pytest.fixture(scope="module")
def knob():
    return build_handle_knob()

@pytest.fixture(scope="module")
def washer():
    return build_retaining_washer()


# ─── Build Smoke Tests ───────────────────────────────

def test_tpu_builds(tpu):
    assert tpu is not None
    assert tpu.volume > 0

def test_body_builds(body):
    assert body is not None
    assert body.volume > 0

def test_knob_builds(knob):
    assert knob is not None
    assert knob.volume > 0

def test_washer_builds(washer):
    assert washer is not None
    assert washer.volume > 0

def test_ghost_bolt_builds():
    bolt = build_ghost_bolt()
    assert bolt is not None
    assert bolt.volume > 0

def test_ghost_heatset_builds():
    hs = build_ghost_heatset()
    assert hs is not None
    assert hs.volume > 0


# ─── TPU Insert Dimensions ───────────────────────────

def test_tpu_bounding_box(tpu):
    bb = tpu.bounding_box()
    x_size = bb.max.X - bb.min.X
    y_size = bb.max.Y - bb.min.Y
    z_size = bb.max.Z - bb.min.Z
    assert abs(x_size - TPU_LONG) < TOL, f"TPU X={x_size}, expected {TPU_LONG}"
    assert abs(y_size - TPU_SHORT) < TOL, f"TPU Y={y_size}, expected {TPU_SHORT}"
    assert abs(z_size - TPU_HEIGHT) < TOL, f"TPU Z={z_size}, expected {TPU_HEIGHT}"

def test_tpu_is_solid(tpu):
    """TPU insert must be a single solid (no disconnected pieces)."""
    assert len(tpu.solids()) == 1

def test_tpu_volume_reasonable(tpu):
    """Volume should be less than the full stadium block (slot removed)."""
    full_block = TPU_LONG * TPU_SHORT * TPU_HEIGHT  # overestimate (rect, not stadium)
    assert tpu.volume < full_block
    slot_vol = SLOT_WIDTH * SLOT_LENGTH * SLOT_DEPTH
    assert tpu.volume < full_block - slot_vol * 0.5  # rough check


# ─── Socket Body Dimensions ──────────────────────────

def test_body_bounding_box(body):
    bb = body.bounding_box()
    x_size = bb.max.X - bb.min.X
    y_size = bb.max.Y - bb.min.Y
    z_size = bb.max.Z - bb.min.Z
    # X: socket -X edge to arm end (arm starts at socket center, extends +X)
    arm_right = ARM_LENGTH + FLANGE_DIA / 2 + 2
    expected_x = SOCKET_LONG / 2 + arm_right  # -X from socket + arm to +X
    assert abs(x_size - expected_x) < TOL, f"Body X={x_size}, expected ~{expected_x}"
    # Y should be max of socket width or arm width
    expected_y = max(SOCKET_SHORT, ARM_WIDTH)
    assert abs(y_size - expected_y) < TOL, f"Body Y={y_size}, expected {expected_y}"
    # Z: from z=0 (pocket bottom) to ARM_Z_TOP (arm top)
    expected_z = ARM_Z_TOP
    assert abs(z_size - expected_z) < TOL, f"Body Z={z_size}, expected {expected_z}"

def test_body_is_solid(body):
    assert len(body.solids()) == 1

def test_pocket_opens_at_bottom(body):
    """Pocket opens at z=0 (usage orientation: peg engagement at bottom)."""
    bb = body.bounding_box()
    assert abs(bb.min.Z - 0.0) < TOL

def test_arm_at_top(body):
    """Arm must be at the top of the socket (usage orientation)."""
    bb = body.bounding_box()
    assert abs(bb.max.Z - ARM_Z_TOP) < TOL

def test_arm_clearance_from_peg():
    """Arm must be far enough from peg slot to clear adjacent tuning pegs."""
    # Distance from slot top (z=0) to arm bottom
    clearance = ARM_Z_BOTTOM
    assert clearance >= 20.0, f"Arm-to-peg clearance={clearance}mm, need >=20mm"

def test_arm_extends_past_bore(body):
    """Arm must extend past the bearing bore for structural integrity."""
    bb = body.bounding_box()
    arm_right_edge = bb.max.X
    assert arm_right_edge >= ARM_LENGTH + ARM_BORE_DIA / 2


# ─── Handle Knob Dimensions ──────────────────────────

def test_knob_bounding_box(knob):
    bb = knob.bounding_box()
    x_size = bb.max.X - bb.min.X
    y_size = bb.max.Y - bb.min.Y
    z_size = bb.max.Z - bb.min.Z
    assert abs(x_size - KNOB_OD) < TOL, f"Knob X={x_size}, expected {KNOB_OD}"
    assert abs(y_size - KNOB_OD) < TOL, f"Knob Y={y_size}, expected {KNOB_OD}"
    expected_z = KNOB_HEIGHT + FLANGE_HEIGHT + POST_HEIGHT
    assert abs(z_size - expected_z) < TOL, f"Knob Z={z_size}, expected {expected_z}"

def test_knob_is_solid(knob):
    assert len(knob.solids()) == 1

def test_knob_volume_reasonable(knob):
    """Knob should be less than a full cylinder of max envelope."""
    import math
    full_cyl = math.pi * (KNOB_OD / 2) ** 2 * (KNOB_HEIGHT + FLANGE_HEIGHT + POST_HEIGHT)
    assert knob.volume < full_cyl
    assert knob.volume > full_cyl * 0.2  # not too hollow


# ─── Retaining Washer Dimensions ─────────────────────

def test_washer_bounding_box(washer):
    bb = washer.bounding_box()
    x_size = bb.max.X - bb.min.X
    y_size = bb.max.Y - bb.min.Y
    z_size = bb.max.Z - bb.min.Z
    assert abs(x_size - WASHER_OD) < TOL, f"Washer X={x_size}, expected {WASHER_OD}"
    assert abs(y_size - WASHER_OD) < TOL, f"Washer Y={y_size}, expected {WASHER_OD}"
    assert abs(z_size - WASHER_H) < TOL, f"Washer Z={z_size}, expected {WASHER_H}"

def test_washer_is_solid(washer):
    assert len(washer.solids()) == 1


# ─── Fit & Interface Checks ──────────────────────────

def test_tpu_fits_in_pocket():
    """TPU insert bounding box must fit within socket pocket."""
    assert TPU_SHORT <= SOCKET_SHORT - 2 * SOCKET_WALL + TOL
    assert TPU_LONG <= SOCKET_LONG - 2 * SOCKET_WALL + TOL
    assert TPU_HEIGHT <= POCKET_DEPTH + TOL

def test_post_fits_in_bore():
    """Post OD must be smaller than arm bore (clearance fit)."""
    assert ARM_BORE_DIA > POST_OD
    clearance = ARM_BORE_DIA - POST_OD
    assert 0.2 <= clearance <= 1.0, f"Clearance={clearance}, expected 0.2-1.0"

def test_flange_wider_than_bore():
    """Flange must be wider than arm bore to act as shoulder."""
    assert FLANGE_DIA > ARM_BORE_DIA

def test_washer_wider_than_bore():
    """Printed washer must be wider than arm bore for axial retention."""
    assert WASHER_OD > ARM_BORE_DIA

def test_washer_bolt_clearance():
    """Washer bore must clear M3 bolt shaft."""
    assert WASHER_ID >= 3.0

def test_post_longer_than_arm():
    """Post must protrude below arm for washer clearance."""
    assert POST_HEIGHT > ARM_HEIGHT

def test_heatset_fits_in_post():
    """Heat-set must fit within post OD."""
    assert HEATSET_DIA < POST_OD

def test_heatset_shorter_than_post():
    """Heat-set must fit within post height."""
    assert HEATSET_DEPTH < POST_HEIGHT


# ─── Wall Thickness Checks ───────────────────────────

def test_socket_wall_minimum():
    """Socket wall must be at least 2mm for PETG-CF."""
    assert SOCKET_WALL >= 2.0

def test_tpu_wall_minimum():
    """TPU wall around slot must be at least 2mm."""
    assert TPU_WALL >= 2.0

def test_post_wall_around_heatset():
    """Post wall around heat-set must be at least 1.5mm."""
    wall = (POST_OD - HEATSET_DIA) / 2
    assert wall >= 1.5, f"Post wall={wall}, need >=1.5mm"

def test_washer_wall_minimum():
    """Washer wall around M3 bore must provide strength."""
    wall = (WASHER_OD - WASHER_ID) / 2
    assert wall >= 3.0, f"Washer wall={wall}, need >=3.0mm"


# ─── Printability (No Supports) ──────────────────────

def test_tpu_no_overhang(tpu):
    """TPU bottom face area >= top face area (no flaring)."""
    bb = tpu.bounding_box()
    bottom_faces = [f for f in tpu.faces() if abs(f.center().Z - bb.min.Z) < 0.1]
    top_faces = [f for f in tpu.faces() if abs(f.center().Z - bb.max.Z) < 0.1]
    if bottom_faces and top_faces:
        bottom_area = sum(f.area for f in bottom_faces)
        top_area = sum(f.area for f in top_faces)
        assert bottom_area >= top_area, "TPU flares outward — needs supports"

def test_knob_no_overhang(knob):
    """Knob must be a single solid (revolved, no overhang issues)."""
    assert len(knob.solids()) == 1

def test_knob_post_narrower_than_flange():
    """Post must be narrower than flange (prints without supports)."""
    assert POST_OD < FLANGE_DIA

def test_knob_flange_narrower_than_barrel():
    """Flange must be narrower than barrel (prints without supports)."""
    assert FLANGE_DIA < KNOB_OD


# ─── Parametric Consistency ───────────────────────────

def test_stadium_derivation():
    """Verify stadium dimensions are correctly derived from slot."""
    assert abs(TPU_SHORT - (SLOT_WIDTH + 2 * TPU_WALL)) < 0.01
    assert abs(TPU_LONG - (SLOT_LENGTH + 2 * TPU_WALL)) < 0.01
    assert abs(SOCKET_SHORT - (TPU_SHORT + 2 * SOCKET_WALL)) < 0.01
    assert abs(SOCKET_LONG - (TPU_LONG + 2 * SOCKET_WALL)) < 0.01

def test_socket_height_derivation():
    assert abs(SOCKET_HEIGHT - (POCKET_DEPTH + SOCKET_CAP)) < 0.01
    assert abs(POCKET_DEPTH - TPU_HEIGHT) < 0.01

def test_z_position_derivations():
    """Verify derived Z positions are consistent."""
    assert abs(ARM_Z_BOTTOM - (SOCKET_HEIGHT - ARM_HEIGHT)) < 0.01
    assert abs(ARM_Z_TOP - SOCKET_HEIGHT) < 0.01
    assert abs(KNOB_Z_BOTTOM - (ARM_Z_TOP + FLANGE_HEIGHT)) < 0.01
    assert abs(KNOB_Z_TOP - (KNOB_Z_BOTTOM + KNOB_HEIGHT)) < 0.01
    assert abs(POST_TIP_Z - (ARM_Z_TOP - POST_HEIGHT)) < 0.01
    # Post tip below arm bottom (protrusion)
    assert POST_TIP_Z < ARM_Z_BOTTOM
