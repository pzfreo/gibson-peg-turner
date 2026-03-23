"""
Gibson Peg Turner — build123d CAD Model

Generates STEP files for a 4-piece T-handle string winder:
  A) Socket body (PETG-CF)  — stadium shape + arm with through-bore bearing
  B) TPU insert (TPU 95A)   — stadium plug with peg-engagement slot
  C) Handle knob (PETG-CF)  — barrel knob with integral bushing post
  D) Retaining washer (PETG-CF) — printed washer, covers bore from below

Modelled in usage orientation:
  - z=0 bottom: peg engagement (pocket opens here)
  - z=30 top: solid cap, arm extends from here
  - Knob sits on arm; post goes through arm bore
  - Flange (top) + printed washer (bottom) retain knob axially
  - Knob+post+bolt+washer spin freely as a unit

For printing:
  - Socket body: flip so arm is on the bed, pocket faces up
  - Knob: print barrel-down, post pointing up (no supports)
  - TPU insert: print upright, slot opening up
  - Retaining washer: print flat
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
TPU_WALL   = 2.0
TPU_SHORT  = SLOT_WIDTH  + 2 * TPU_WALL   # 8.0 — short axis (Y)
TPU_LONG   = SLOT_LENGTH + 2 * TPU_WALL   # 19.0 — long axis (X)
TPU_HEIGHT = SLOT_DEPTH  + TPU_WALL        # 19.0 — total height (Z)

# ─── Socket Body ──────────────────────────────────────
SOCKET_WALL   = 2.65
SOCKET_SHORT  = TPU_SHORT + 2 * SOCKET_WALL   # 13.3 — short axis (Y)
SOCKET_LONG   = TPU_LONG  + 2 * SOCKET_WALL   # 24.3 — long axis (X)
SOCKET_CAP    = 10.0                           # solid cap above pocket (arm clearance)
SOCKET_HEIGHT = TPU_HEIGHT + SOCKET_CAP        # 29.0 — total height (Z)
POCKET_DEPTH  = TPU_HEIGHT                     # 19.0
POCKET_CHAMFER = 0.5

# ─── T-Handle Arm ─────────────────────────────────────
ARM_LENGTH = 23.0    # socket center → bushing center (X)
ARM_WIDTH  = 12.0    # Y — horizontal on bed
ARM_HEIGHT = 8.0     # Z — through-bore, no floor needed
ARM_RADIUS = 2.0     # corner rounding
ARM_FILLET = 5.0     # junction stress-relief fillet

# ─── Arm Bearing Bore (through-hole for knob post) ───
ARM_BORE_DIA = 8.4   # POST_OD + 0.4mm clearance

# ─── Knob Bushing Post (integral with knob) ──────────
POST_OD       = 8.0    # bearing surface
POST_HEIGHT   = 8.3    # ARM_HEIGHT + 0.3mm — protrudes below for washer
FLANGE_DIA    = 12.0   # wider than bore, sits on arm top
FLANGE_HEIGHT = 2.0    # shoulder ring

# ─── Heat-set Insert (in knob post tip) ──────────────
HEATSET_DIA   = 4.0
HEATSET_DEPTH = 4.5

# ─── Handle Knob ──────────────────────────────────────
KNOB_OD       = 16.0
KNOB_HEIGHT   = 30.0
KNOB_EDGE_RAD = 3.0     # barrel rounding

# ─── Printed Retaining Washer (PETG-CF) ──────────────
WASHER_OD = 12.0    # must be > ARM_BORE_DIA (8.4mm) — covers bore
WASHER_ID = 3.2     # M3 bolt clearance
WASHER_H  = 2.0     # thick enough for PETG-CF strength

# ─── M3 Bolt (ghost) ─────────────────────────────────
M3_SHAFT_DIA  = 3.0
M3_SHAFT_LEN  = 8.0     # only needs to reach heat-set
M3_HEAD_DIA   = 5.5     # pan head
M3_HEAD_H     = 2.0

# ─── Derived Z positions (usage orientation) ──────────
ARM_Z_BOTTOM  = SOCKET_HEIGHT - ARM_HEIGHT     # 21.0
ARM_Z_TOP     = SOCKET_HEIGHT                  # 29.0
KNOB_Z_BOTTOM = ARM_Z_TOP + FLANGE_HEIGHT     # 31.0
KNOB_Z_TOP    = KNOB_Z_BOTTOM + KNOB_HEIGHT   # 61.0
POST_TIP_Z    = ARM_Z_TOP - POST_HEIGHT        # 20.7 (0.3mm below arm)


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

        # Peg engagement slot — stadium shape matching outer profile, open at top
        with BuildSketch(Plane.XY.offset(TPU_HEIGHT)):
            SlotOverall(SLOT_LENGTH, SLOT_WIDTH)
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
    """Stadium body + T-handle arm with through-bore bearing.

    Usage orientation: pocket opens at z=0 (bottom), arm at top (z=22-30).
    Socket cap raised to 10mm to keep arm clear of adjacent tuning pegs.
    Arm has a through-bore for the knob's bushing post.

    For printing: flip so arm is on the bed and pocket faces up.
    """
    with BuildPart() as bp:
        # Stadium tube
        with BuildSketch():
            SlotOverall(SOCKET_LONG, SOCKET_SHORT)
        extrude(amount=SOCKET_HEIGHT)

        # T-handle arm at the TOP of the socket — extends +X only
        arm_left = 0                                # start at socket center (solid cap region)
        arm_overshoot_right = FLANGE_DIA / 2 + 2   # extend past flange seating
        arm_right = ARM_LENGTH + arm_overshoot_right
        arm_total_len = arm_right - arm_left
        arm_cx = (arm_left + arm_right) / 2
        with BuildSketch(Plane.XY.offset(ARM_Z_BOTTOM)):
            with Locations([(arm_cx, 0)]):
                RectangleRounded(arm_total_len, ARM_WIDTH, ARM_RADIUS)
        extrude(amount=ARM_HEIGHT)

        # TPU pocket — stadium bore from bottom (z=0 upward)
        with BuildSketch(Plane.XY):
            SlotOverall(TPU_LONG, TPU_SHORT)
        extrude(amount=POCKET_DEPTH, mode=Mode.SUBTRACT)

        # Pocket entry chamfer (bottom face, z=0)
        bottom_face = bp.faces().sort_by(Axis.Z)[0]
        outer_wire_len = max(w.length for w in bottom_face.wires())
        pocket_edges = [
            e
            for w in bottom_face.wires()
            if w.length < outer_wire_len - 0.1
            for e in w.edges()
        ]
        if pocket_edges:
            chamfer(pocket_edges, POCKET_CHAMFER)

        # Through-bore for bushing post
        with BuildSketch(Plane.XY.offset(ARM_Z_BOTTOM)):
            with Locations([(ARM_LENGTH, 0)]):
                Circle(ARM_BORE_DIA / 2)
        extrude(amount=ARM_HEIGHT, mode=Mode.SUBTRACT)

    return bp.part


# ═══════════════════════════════════════════════════════
#  Component C — Handle Knob
# ═══════════════════════════════════════════════════════

def build_handle_knob() -> Part:
    """Barrel-shaped palm knob with integral bushing post.

    Built with barrel at z=0..KNOB_HEIGHT, flange below at z=0..-FLANGE_HEIGHT,
    and post below flange to z=-(FLANGE_HEIGHT+POST_HEIGHT).

    Heat-set insert pocket at post tip for bolt retention.

    Print barrel-down (flat bottom on bed), post pointing up. No supports.
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

        # Flange below barrel (wider than bore, acts as shoulder)
        with BuildSketch(Plane.XY):
            Circle(FLANGE_DIA / 2)
        extrude(amount=-FLANGE_HEIGHT)

        # Bushing post below flange
        with BuildSketch(Plane.XY.offset(-FLANGE_HEIGHT)):
            Circle(POST_OD / 2)
        extrude(amount=-POST_HEIGHT)

        # Heat-set insert pocket at post tip (boring upward from tip)
        post_tip_z = -(FLANGE_HEIGHT + POST_HEIGHT)
        with BuildSketch(Plane.XY.offset(post_tip_z)):
            Circle(HEATSET_DIA / 2)
        extrude(amount=HEATSET_DEPTH, mode=Mode.SUBTRACT)

    return bp.part


# ═══════════════════════════════════════════════════════
#  Component D — Printed Retaining Washer
# ═══════════════════════════════════════════════════════

def build_retaining_washer() -> Part:
    """Printed PETG-CF washer — covers arm bore from below.

    12mm OD × 2mm thick, 3.2mm M3 bore. Print flat. No supports.
    """
    with BuildPart() as bp:
        Cylinder(
            WASHER_OD / 2, WASHER_H,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
        Cylinder(
            WASHER_ID / 2, WASHER_H,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
            mode=Mode.SUBTRACT,
        )
    return bp.part


# ═══════════════════════════════════════════════════════
#  Ghost Hardware (for assembly visualization only)
# ═══════════════════════════════════════════════════════

def build_ghost_bolt() -> Part:
    """M3 pan head bolt — ghost visualization.

    Built with head at z=0 (bottom), shaft extending upward (+Z).
    """
    with BuildPart() as bp:
        Cylinder(
            M3_HEAD_DIA / 2, M3_HEAD_H,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
        with BuildSketch(Plane.XY.offset(M3_HEAD_H)):
            Circle(M3_SHAFT_DIA / 2)
        extrude(amount=M3_SHAFT_LEN)
    return bp.part


def build_ghost_heatset() -> Part:
    """M3×4mm brass heat-set insert — ghost visualization."""
    with BuildPart() as bp:
        Cylinder(
            HEATSET_DIA / 2, 4.0,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
        Cylinder(
            M3_SHAFT_DIA / 2, 4.0,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
            mode=Mode.SUBTRACT,
        )
    return bp.part


# ═══════════════════════════════════════════════════════
#  Build & Export
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    print("Building components...")
    tpu     = build_tpu_insert()
    body    = build_socket_body()
    knob    = build_handle_knob()
    washer  = build_retaining_washer()
    bolt    = build_ghost_bolt()
    heatset = build_ghost_heatset()

    # Export individual STEP files (for slicing)
    export_step(tpu, str(OUT / "tpu_insert.step"))
    export_step(body, str(OUT / "socket_body.step"))
    export_step(knob, str(OUT / "handle_knob.step"))
    export_step(washer, str(OUT / "retaining_washer.step"))

    # ── Assembly: position parts in usage orientation ──
    # TPU insert drops into pocket from z=0
    tpu_asm = Pos(0, 0, 0) * tpu
    tpu_asm.label = "TPU Insert"
    tpu_asm.color = Color("royalblue")

    # Socket body at origin
    body.label = "Socket Body"
    body.color = Color("dimgray")

    # Knob: barrel z=0 maps to KNOB_Z_BOTTOM in assembly
    knob_asm = Pos(ARM_LENGTH, 0, KNOB_Z_BOTTOM) * knob
    knob_asm.label = "Handle Knob"
    knob_asm.color = Color("silver")

    # Printed washer — sits on post tip below arm
    washer_asm = Pos(ARM_LENGTH, 0, POST_TIP_Z - WASHER_H) * washer
    washer_asm.label = "Retaining Washer"
    washer_asm.color = Color("forestgreen")

    # Ghost bolt — head below washer, shaft goes up into post heat-set
    bolt_z = POST_TIP_Z - WASHER_H - M3_HEAD_H
    bolt_asm = Pos(ARM_LENGTH, 0, bolt_z) * bolt
    bolt_asm.label = "M3 Bolt"
    bolt_asm.color = Color("gold")

    # Ghost heat-set — in knob post tip
    heatset_asm = Pos(ARM_LENGTH, 0, POST_TIP_Z) * heatset
    heatset_asm.label = "Heat-set Insert"
    heatset_asm.color = Color("darkorange")

    assembly = Compound(
        label="Peg Turner Assembly",
        children=[body, tpu_asm, knob_asm, washer_asm, bolt_asm, heatset_asm],
    )
    export_step(assembly, str(OUT / "assembly.step"))

    print("Exported STEP files:")
    for name in ["socket_body", "tpu_insert", "handle_knob",
                  "retaining_washer", "assembly"]:
        print(f"  {OUT / name}.step")

    # Show in OCP CAD Viewer (VSCode) if available — fail silently
    try:
        from ocp_vscode import show
        show(
            body, tpu_asm, knob_asm, washer_asm, bolt_asm, heatset_asm,
            names=["Socket Body", "TPU Insert", "Handle Knob",
                   "Retaining Washer", "M3 Bolt", "Heat-set Insert"],
            colors=["dimgray", "royalblue", "silver",
                    "forestgreen", "gold", "darkorange"],
            alphas=[1.0, 0.8, 1.0, 1.0, 0.4, 0.4],
        )
    except Exception:
        pass
