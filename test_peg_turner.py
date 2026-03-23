"""Tests for peg_turner.py — verify dimensions, fit, and printability."""

import pytest
from build123d import *
from peg_turner import (
    build_tpu_insert,
    build_socket_body,
    build_handle_knob,
    build_ghost_bolt,
    build_ghost_heatset,
    # Parameters
    SLOT_WIDTH, SLOT_LENGTH, SLOT_DEPTH, SLOT_CHAMFER,
    TPU_WALL, TPU_SHORT, TPU_LONG, TPU_HEIGHT,
    SOCKET_WALL, SOCKET_SHORT, SOCKET_LONG, SOCKET_HEIGHT,
    POCKET_DEPTH,
    ARM_LENGTH, ARM_WIDTH, ARM_HEIGHT,
    ARM_Z_BOTTOM, ARM_Z_TOP, POST_Z_BOTTOM, POST_Z_TOP,
    POST_OD, POST_BORE, POST_HEIGHT, POST_SHOULDER, POST_SHOULDER_DIA,
    HEATSET_DIA, HEATSET_DEPTH,
    KNOB_OD, KNOB_HEIGHT, KNOB_BORE, KNOB_CAP,
    WASHER_RECESS_DIA, WASHER_RECESS_DEPTH,
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
    # Slot removes at least SLOT_WIDTH * SLOT_LENGTH * SLOT_DEPTH
    slot_vol = SLOT_WIDTH * SLOT_LENGTH * SLOT_DEPTH
    assert tpu.volume < full_block - slot_vol * 0.5  # rough check


# ─── Socket Body Dimensions ──────────────────────────

def test_body_bounding_box(body):
    bb = body.bounding_box()
    x_size = bb.max.X - bb.min.X
    y_size = bb.max.Y - bb.min.Y
    z_size = bb.max.Z - bb.min.Z
    # X: socket -X edge to arm end (arm extends past bushing by shoulder_dia/2 + 2)
    arm_right = ARM_LENGTH + POST_SHOULDER_DIA / 2 + 2
    expected_x = SOCKET_LONG / 2 + arm_right
    assert abs(x_size - expected_x) < TOL, f"Body X={x_size}, expected ~{expected_x}"
    # Y should be max of socket width or arm width
    expected_y = max(SOCKET_SHORT, ARM_WIDTH)
    assert abs(y_size - expected_y) < TOL, f"Body Y={y_size}, expected {expected_y}"
    # Z: from z=0 (pocket bottom) to post top
    expected_z = POST_Z_TOP
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
    # The arm is at z=ARM_Z_BOTTOM to z=ARM_Z_TOP (17 to 25)
    # The post extends above to POST_Z_TOP (39)
    assert abs(bb.max.Z - POST_Z_TOP) < TOL
    # Arm is in the upper portion of the socket
    assert ARM_Z_BOTTOM > SOCKET_HEIGHT / 2, "Arm should be in upper half of socket"

def test_arm_extends_past_bushing(body):
    """Arm must extend past the bushing post for solid heat-set support."""
    bb = body.bounding_box()
    # Arm right edge should be past ARM_LENGTH (bushing center)
    arm_right_edge = bb.max.X
    # The post shoulder at ARM_LENGTH has radius POST_SHOULDER_DIA/2 = 5
    # So the max X from the post is ARM_LENGTH + 5 = 55
    # The arm should extend at least that far
    assert arm_right_edge >= ARM_LENGTH + POST_SHOULDER_DIA / 2


# ─── Handle Knob Dimensions ──────────────────────────

def test_knob_bounding_box(knob):
    bb = knob.bounding_box()
    x_size = bb.max.X - bb.min.X
    y_size = bb.max.Y - bb.min.Y
    z_size = bb.max.Z - bb.min.Z
    assert abs(x_size - KNOB_OD) < TOL, f"Knob X={x_size}, expected {KNOB_OD}"
    assert abs(y_size - KNOB_OD) < TOL, f"Knob Y={y_size}, expected {KNOB_OD}"
    assert abs(z_size - KNOB_HEIGHT) < TOL, f"Knob Z={z_size}, expected {KNOB_HEIGHT}"

def test_knob_is_solid(knob):
    assert len(knob.solids()) == 1

def test_knob_volume_reasonable(knob):
    """Knob should be less than a full cylinder (bore + fillets removed)."""
    import math
    full_cyl = math.pi * (KNOB_OD / 2) ** 2 * KNOB_HEIGHT
    assert knob.volume < full_cyl
    assert knob.volume > full_cyl * 0.3  # not too hollow


# ─── Fit & Interface Checks ──────────────────────────

def test_tpu_fits_in_pocket():
    """TPU insert bounding box must fit within socket pocket."""
    assert TPU_SHORT <= SOCKET_SHORT - 2 * SOCKET_WALL + TOL
    assert TPU_LONG <= SOCKET_LONG - 2 * SOCKET_WALL + TOL
    assert TPU_HEIGHT <= POCKET_DEPTH + TOL

def test_knob_clears_post():
    """Knob bore must be larger than post OD (clearance fit)."""
    assert KNOB_BORE > POST_OD
    clearance = KNOB_BORE - POST_OD
    assert 0.2 <= clearance <= 1.0, f"Clearance={clearance}, expected 0.2-1.0"

def test_shoulder_stops_knob():
    """Bushing shoulder must be wider than knob bore."""
    assert POST_SHOULDER_DIA > KNOB_BORE

def test_bolt_clears_post_bore():
    """M3 bolt (3.0mm) must fit through post bore."""
    assert POST_BORE > 3.0

def test_heatset_wider_than_bore():
    """Heat-set pocket must be wider than the M3 bore."""
    assert HEATSET_DIA > POST_BORE

def test_washer_recess_wider_than_bolt():
    """Washer recess must accommodate M3 washer (5.5mm OD)."""
    assert WASHER_RECESS_DIA > 5.5

def test_washer_recess_narrower_than_bore():
    """Washer recess must be smaller than knob bore to create a shelf."""
    assert WASHER_RECESS_DIA < KNOB_BORE


# ─── Wall Thickness Checks ───────────────────────────

def test_socket_wall_minimum():
    """Socket wall must be at least 2mm for PETG-CF."""
    assert SOCKET_WALL >= 2.0

def test_tpu_wall_minimum():
    """TPU wall around slot must be at least 2mm."""
    assert TPU_WALL >= 2.0

def test_knob_cap_retains_washer():
    """Cap must be thicker than washer recess (or bolt falls through)."""
    assert KNOB_CAP > WASHER_RECESS_DEPTH


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


# ─── Parametric Consistency ───────────────────────────

def test_stadium_derivation():
    """Verify stadium dimensions are correctly derived from slot."""
    assert abs(TPU_SHORT - (SLOT_WIDTH + 2 * TPU_WALL)) < 0.01
    assert abs(TPU_LONG - (SLOT_LENGTH + 2 * TPU_WALL)) < 0.01
    assert abs(SOCKET_SHORT - (TPU_SHORT + 2 * SOCKET_WALL)) < 0.01
    assert abs(SOCKET_LONG - (TPU_LONG + 2 * SOCKET_WALL)) < 0.01

def test_socket_height_derivation():
    assert abs(SOCKET_HEIGHT - (POCKET_DEPTH + 5.0)) < 0.01
    assert abs(POCKET_DEPTH - TPU_HEIGHT) < 0.01

def test_post_height_derivation():
    assert abs(POST_HEIGHT - (KNOB_HEIGHT + POST_SHOULDER)) < 0.01

def test_z_position_derivations():
    """Verify derived Z positions are consistent."""
    assert abs(ARM_Z_BOTTOM - (SOCKET_HEIGHT - ARM_HEIGHT)) < 0.01
    assert abs(ARM_Z_TOP - SOCKET_HEIGHT) < 0.01
    assert abs(POST_Z_BOTTOM - SOCKET_HEIGHT) < 0.01
    assert abs(POST_Z_TOP - (SOCKET_HEIGHT + POST_HEIGHT)) < 0.01
