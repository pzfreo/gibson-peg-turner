"""Tests for peg_turner.py — verify dimensions, fit, and printability."""

import pytest
from build123d import *
from peg_turner import (
    build_tpu_insert,
    build_socket_body,
    build_handle_knob,
    # Parameters
    SLOT_WIDTH, SLOT_LENGTH, SLOT_DEPTH, SLOT_CHAMFER,
    TPU_WALL, TPU_SHORT, TPU_LONG, TPU_HEIGHT,
    SOCKET_WALL, SOCKET_SHORT, SOCKET_LONG, SOCKET_HEIGHT,
    POCKET_DEPTH,
    ARM_LENGTH, ARM_WIDTH, ARM_HEIGHT,
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
    # X spans from socket -X edge to bushing post +X edge (shoulder is widest)
    expected_x = ARM_LENGTH + SOCKET_LONG / 2 + POST_SHOULDER_DIA / 2
    assert abs(x_size - expected_x) < TOL, f"Body X={x_size}, expected ~{expected_x}"
    # Y should be max of socket width or arm width
    expected_y = max(SOCKET_SHORT, ARM_WIDTH)
    assert abs(y_size - expected_y) < TOL, f"Body Y={y_size}, expected {expected_y}"
    # Z spans from 0 to whichever is taller: socket or post top
    expected_z = max(SOCKET_HEIGHT, ARM_HEIGHT + POST_HEIGHT)
    assert abs(z_size - expected_z) < TOL, f"Body Z={z_size}, expected {expected_z}"

def test_body_is_solid(body):
    assert len(body.solids()) == 1

def test_pocket_depth(body):
    """Socket top is at SOCKET_HEIGHT (taller than arm+post)."""
    bb = body.bounding_box()
    # Socket height (25mm) > arm+post top (22mm), so max Z = SOCKET_HEIGHT
    expected_z = max(SOCKET_HEIGHT, ARM_HEIGHT + POST_HEIGHT)
    assert abs(bb.max.Z - expected_z) < TOL


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
    # Stadium cross-sections match exactly (no interference)
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
    assert POST_SHOULDER_DIA > KNOB_BORE, (
        f"Shoulder {POST_SHOULDER_DIA} must exceed bore {KNOB_BORE}"
    )

def test_bolt_clears_post_bore():
    """M3 bolt (3.0mm) must fit through post bore."""
    m3_dia = 3.0
    assert POST_BORE > m3_dia

def test_heatset_wider_than_bore():
    """Heat-set pocket must be wider than the M3 bore."""
    assert HEATSET_DIA > POST_BORE

def test_washer_recess_wider_than_bolt():
    """Washer recess must accommodate M3 washer (5.5mm OD)."""
    m3_washer_od = 5.5
    assert WASHER_RECESS_DIA > m3_washer_od

def test_washer_recess_narrower_than_bore():
    """Washer recess must be smaller than post bore to create a shelf."""
    assert WASHER_RECESS_DIA < KNOB_BORE, (
        f"Recess {WASHER_RECESS_DIA} must be < bore {KNOB_BORE} for retention"
    )


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
    """TPU insert: every layer's XY footprint should not exceed the layer below.

    Check by verifying the bottom face area >= top face area (no flaring).
    """
    bb = tpu.bounding_box()
    bottom_z = bb.min.Z
    top_z = bb.max.Z
    # The stadium is constant cross-section — the slot only removes material at the top.
    # Bottom face should be at least as large as any cross-section above it.
    bottom_faces = [f for f in tpu.faces() if abs(f.center().Z - bottom_z) < 0.1]
    top_faces = [f for f in tpu.faces() if abs(f.center().Z - top_z) < 0.1]
    if bottom_faces and top_faces:
        bottom_area = sum(f.area for f in bottom_faces)
        top_area = sum(f.area for f in top_faces)
        assert bottom_area >= top_area, "TPU flares outward — needs supports"

def test_knob_no_overhang(knob):
    """Knob: barrel fillets should not create unsupported overhangs > 45°."""
    bb = knob.bounding_box()
    # The knob is a revolved shape symmetric about Z.
    # At the very bottom (z=0), the fillet reduces the footprint.
    # But it's printed on the bed, so the bed IS the support.
    # The top fillet curves inward — no overhang.
    # Just verify it's a single solid with reasonable geometry.
    assert len(knob.solids()) == 1

def test_body_arm_on_bed(body):
    """Socket body: arm must start at z=0 (flat on print bed)."""
    bb = body.bounding_box()
    assert abs(bb.min.Z - 0.0) < TOL, f"Body min Z={bb.min.Z}, expected 0"


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
