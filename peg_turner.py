"""
Gibson Peg Turner — build123d CAD Model

Generates STEP files for a 3-piece T-handle string winder:
  A) Socket body (PETG-CF)  — stadium shape + arm + bushing post
  B) TPU insert (TPU 95A)   — stadium plug with peg-engagement slot
  C) Handle knob (PETG-CF)  — barrel knob, free-spins on bushing post

All parts designed for FDM printing without supports.
"""

from build123d import *
from pathlib import Path

OUT = Path(__file__).parent

# ─── Peg Slot ─────────────────────────────────────────
SLOT_WIDTH   = 4.0      # Y — grips peg ring (2.4mm + compression)
SLOT_LENGTH  = 15.0     # X — spans ring OD (12.5mm) + clearance
SLOT_DEPTH   = 17.0     # Z — full peg engagement depth
SLOT_CHAMFER = 1.0      # 45° entry chamfer

# ─── TPU Insert ───────────────────────────────────────
TPU_WALL   = 3.0
TPU_SHORT  = SLOT_WIDTH  + 2 * TPU_WALL   # 10.0 — short axis (Y)
TPU_LONG   = SLOT_LENGTH + 2 * TPU_WALL   # 21.0 — long axis (X)
TPU_HEIGHT = SLOT_DEPTH  + TPU_WALL        # 20.0 — total height (Z)

# ─── Socket Body ──────────────────────────────────────
SOCKET_WALL   = 2.65
SOCKET_SHORT  = TPU_SHORT + 2 * SOCKET_WALL   # 15.3 — short axis (Y)
SOCKET_LONG   = TPU_LONG  + 2 * SOCKET_WALL   # 26.3 — long axis (X)
SOCKET_HEIGHT = TPU_HEIGHT + 5.0               # 25.0 — total height (Z)
POCKET_DEPTH  = TPU_HEIGHT                     # 20.0
POCKET_CHAMFER = 0.5

# ─── T-Handle Arm ─────────────────────────────────────
ARM_LENGTH = 50.0    # socket center → bushing center (X)
ARM_WIDTH  = 12.0    # Y — horizontal on bed
ARM_HEIGHT = 8.0     # Z — vertical
ARM_RADIUS = 2.0     # corner rounding
ARM_FILLET = 5.0     # junction stress-relief fillet

# ─── Bushing Post ─────────────────────────────────────
POST_OD           = 8.0     # bearing surface for knob
POST_BORE         = 3.4     # M3 bolt clearance
POST_HEIGHT       = 14.0    # total above arm (12mm knob + 2mm shoulder)
POST_SHOULDER     = 2.0     # prevents knob sliding down
POST_SHOULDER_DIA = 10.0    # must exceed KNOB_BORE (8.4)

# ─── Heat-set Insert ──────────────────────────────────
HEATSET_DIA   = 4.0
HEATSET_DEPTH = 4.5

# ─── Handle Knob ──────────────────────────────────────
KNOB_OD       = 20.0
KNOB_HEIGHT   = 12.0
KNOB_BORE     = 8.4     # post clearance
KNOB_EDGE_RAD = 3.0     # barrel rounding
KNOB_CAP      = 2.0     # solid top cap for bolt retention
WASHER_RECESS_DIA   = 6.5
WASHER_RECESS_DEPTH = 1.0


# ═══════════════════════════════════════════════════════
#  Component B — TPU Insert
# ═══════════════════════════════════════════════════════

def build_tpu_insert() -> Part:
    """Stadium-shaped plug with peg-engagement slot.

    Print upright, slot opening facing up. No supports needed.
    """
    with BuildPart() as bp:
        # Stadium body
        with BuildSketch():
            SlotOverall(TPU_LONG, TPU_SHORT)
        extrude(amount=TPU_HEIGHT)

        # Peg engagement slot — open at top, 3mm solid base
        with BuildSketch(Plane.XY.offset(TPU_HEIGHT)):
            Rectangle(SLOT_LENGTH, SLOT_WIDTH)
        extrude(amount=-SLOT_DEPTH, mode=Mode.SUBTRACT)

        # Chamfer the slot entry edges (inner wire of the top face)
        top_face = bp.faces().sort_by(Axis.Z)[-1]
        outer_wire_len = max(w.length for w in top_face.wires())
        inner_edges = [
            e
            for w in top_face.wires()
            if w.length < outer_wire_len - 0.1
            for e in w.edges()
        ]
        if inner_edges:
            chamfer(inner_edges, SLOT_CHAMFER)

    return bp.part


# ═══════════════════════════════════════════════════════
#  Component A — Socket Body
# ═══════════════════════════════════════════════════════

def build_socket_body() -> Part:
    """Stadium body + T-handle arm + bushing post.

    Modelled in print orientation: arm at z=0 (on bed), pocket opens at z=25.
    In use the tool is flipped — arm on top, peg engagement at bottom.
    """
    with BuildPart() as bp:
        # Stadium tube
        with BuildSketch():
            SlotOverall(SOCKET_LONG, SOCKET_SHORT)
        extrude(amount=SOCKET_HEIGHT)

        # T-handle arm — extends in +X, overshoots into socket for clean union
        arm_overshoot = SOCKET_LONG / 2
        arm_total_len = ARM_LENGTH + arm_overshoot
        arm_cx = (ARM_LENGTH - arm_overshoot) / 2
        with BuildSketch():
            with Locations([(arm_cx, 0)]):
                RectangleRounded(arm_total_len, ARM_WIDTH, ARM_RADIUS)
        extrude(amount=ARM_HEIGHT)

        # Bushing post — shoulder (wider ring, knob stop)
        with BuildSketch(Plane.XY.offset(ARM_HEIGHT)):
            with Locations([(ARM_LENGTH, 0)]):
                Circle(POST_SHOULDER_DIA / 2)
        extrude(amount=POST_SHOULDER)

        # Bushing post — shaft
        shaft_z = ARM_HEIGHT + POST_SHOULDER
        shaft_h = POST_HEIGHT - POST_SHOULDER
        with BuildSketch(Plane.XY.offset(shaft_z)):
            with Locations([(ARM_LENGTH, 0)]):
                Circle(POST_OD / 2)
        extrude(amount=shaft_h)

        # TPU pocket — stadium bore from top
        with BuildSketch(Plane.XY.offset(SOCKET_HEIGHT)):
            SlotOverall(TPU_LONG, TPU_SHORT)
        extrude(amount=-POCKET_DEPTH, mode=Mode.SUBTRACT)

        # Pocket entry chamfer
        top_face = bp.faces().sort_by(Axis.Z)[-1]
        outer_wire_len = max(w.length for w in top_face.wires())
        pocket_edges = [
            e
            for w in top_face.wires()
            if w.length < outer_wire_len - 0.1
            for e in w.edges()
        ]
        if pocket_edges:
            chamfer(pocket_edges, POCKET_CHAMFER)

        # M3 through-bore — post top down through arm bottom
        post_top_z = ARM_HEIGHT + POST_HEIGHT
        bore_total = POST_HEIGHT + ARM_HEIGHT
        with BuildSketch(Plane.XY.offset(post_top_z)):
            with Locations([(ARM_LENGTH, 0)]):
                Circle(POST_BORE / 2)
        extrude(amount=-bore_total, mode=Mode.SUBTRACT)

        # Heat-set insert pocket — wider bore at arm underside
        with BuildSketch(Plane.XY):
            with Locations([(ARM_LENGTH, 0)]):
                Circle(HEATSET_DIA / 2)
        extrude(amount=HEATSET_DEPTH, mode=Mode.SUBTRACT)

    return bp.part


# ═══════════════════════════════════════════════════════
#  Component C — Handle Knob
# ═══════════════════════════════════════════════════════

def build_handle_knob() -> Part:
    """Barrel-shaped palm knob with stepped bore.

    Print upright, bore vertical. No supports needed.

    Bore profile (top to bottom):
      - Washer recess:  6.5mm dia × 1mm   (flush bolt head)
      - Bolt clearance: 3.4mm dia × 1mm   (M3 through cap)
      - Post bore:      8.4mm dia × 10mm  (bushing post clearance)
    """
    with BuildPart() as bp:
        # Barrel body
        Cylinder(
            KNOB_OD / 2, KNOB_HEIGHT,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )

        # Fillet top and bottom circular edges → barrel shape
        circ_edges = bp.edges().filter_by(GeomType.CIRCLE)
        fillet(circ_edges, KNOB_EDGE_RAD)

        # Post bore — from bottom up to cap
        bore_depth = KNOB_HEIGHT - KNOB_CAP
        with BuildSketch(Plane.XY):
            Circle(KNOB_BORE / 2)
        extrude(amount=bore_depth, mode=Mode.SUBTRACT)

        # Bolt clearance through cap
        with BuildSketch(Plane.XY.offset(bore_depth)):
            Circle(POST_BORE / 2)
        extrude(amount=KNOB_CAP, mode=Mode.SUBTRACT)

        # Washer recess — widens top of bolt hole for flush washer
        with BuildSketch(Plane.XY.offset(KNOB_HEIGHT)):
            Circle(WASHER_RECESS_DIA / 2)
        extrude(amount=-WASHER_RECESS_DEPTH, mode=Mode.SUBTRACT)

    return bp.part


# ═══════════════════════════════════════════════════════
#  Build & Export
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    print("Building components...")
    tpu  = build_tpu_insert()
    body = build_socket_body()
    knob = build_handle_knob()

    # Export individual STEP files (for slicing)
    export_step(tpu, str(OUT / "tpu_insert.step"))
    export_step(body, str(OUT / "socket_body.step"))
    export_step(knob, str(OUT / "handle_knob.step"))

    # Assembly — position parts in assembled configuration
    # (print orientation: arm at z=0, pocket opens at z=SOCKET_HEIGHT)
    tpu_asm  = Pos(0, 0, SOCKET_HEIGHT - POCKET_DEPTH) * tpu
    knob_asm = Pos(ARM_LENGTH, 0, ARM_HEIGHT + POST_SHOULDER) * knob

    assembly = Compound(children=[body, tpu_asm, knob_asm])
    export_step(assembly, str(OUT / "assembly.step"))

    print("Exported STEP files:")
    for name in ["socket_body", "tpu_insert", "handle_knob", "assembly"]:
        print(f"  {OUT / name}.step")

    # Show in OCP CAD Viewer (VSCode) if available
    try:
        from ocp_vscode import show
        show(body, tpu_asm, knob_asm)
    except ImportError:
        pass
