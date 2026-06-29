"""
Gibson Peg Turner — Drill Socket variant

A power-drill version of the peg turner. Reuses the stadium socket + TPU-insert
pocket from `peg_turner.py` unchanged (so it takes the SAME TPU insert and
engages the SAME peg head), but replaces the T-handle arm + bushing bore with a
coaxial 1/4" hex shank that chucks into a cordless drill / driver.

Shared dimensions are imported from peg_turner.py — the parametric pocket that
fits the TPU insert is single-sourced there. Only the socket geometry itself
(stadium tube + pocket + entry chamfer) is rebuilt here, plus the hex shank.

Modelled in usage orientation:
  - z=0 bottom: peg engagement (pocket opens here, same as peg_turner)
  - z=SOCKET_HEIGHT top: solid cap
  - hex shank rises coaxially from the cap top into the drill chuck

For printing:
  - Print shank UP, pocket opening DOWN on the bed. No supports:
    the shank narrows upward, and the pocket roof is a short (~TPU_SHORT) bridge.
"""

from build123d import *
from pathlib import Path

from peg_turner import (
    TPU_LONG, TPU_SHORT,
    SOCKET_LONG, SOCKET_SHORT,
    POCKET_DEPTH, POCKET_CHAMFER,
)

OUT = Path(__file__).parent

# ─── Socket Cap (drill variant) ───────────────────────
# The T-handle design uses an 18mm solid cap to push the retaining bolt clear of
# adjacent tuning pegs. The drill variant has no bolt near the pegs, so the cap
# only needs to house the pyramid roof (~ROOF_HEIGHT) plus a little solid base
# for the hex shank. Override it here (shorter part) rather than touching
# peg_turner.SOCKET_HEIGHT, which the T-handle model depends on.
DRILL_CAP     = 6.0                          # solid cap above the pocket
SOCKET_HEIGHT = POCKET_DEPTH + DRILL_CAP     # 25.0 — total socket height (was 37)

# ─── Pocket Roof ──────────────────────────────────────
# 45° self-supporting pyramid over the pocket — replaces the flat ceiling that
# would otherwise need bridging when printed pocket-down. Built as a uniform 45°
# inward taper of the pocket stadium, so every roof face sits at exactly 45°.
# It closes to a hairline ridge (ROOF_RIDGE_SHORT) rather than a sharp point: a
# true apex is a cone-tip singularity (prints as a blob, defeats analysis),
# whereas a sub-mm ridge lays down one clean bridge line. Carved into the solid
# cap above the pocket — the TPU pocket (z=0..POCKET_DEPTH) is untouched, so the
# TPU insert shape is unchanged.
ROOF_RIDGE_SHORT = 0.4                        # residual ridge width at the apex
ROOF_HEIGHT      = (TPU_SHORT - ROOF_RIDGE_SHORT) / 2   # 3.3 — 45° => height = inset
ROOF_RIDGE_LONG  = TPU_LONG - 2 * ROOF_HEIGHT          # 12.4 — top stadium long axis

# ─── Hex Drill Shank ──────────────────────────────────
HEX_AF        = 6.35                  # 1/4" across-flats — universal drill/driver shank
HEX_RADIUS    = HEX_AF / 3 ** 0.5     # 3.667 — circumradius (vertex) for RegularPolygon
SHANK_LENGTH  = 25.0                  # gripped length for keyless chuck
SHANK_FILLET  = 1.5                   # base stress-relief fillet at cap junction
SHANK_LEAD_IN = 0.5                   # tip chamfer, eases chuck insertion


# ═══════════════════════════════════════════════════════
#  Drill Socket — stadium socket (reused) + hex shank
# ═══════════════════════════════════════════════════════

def build_drill_socket() -> Part:
    """Stadium socket body (reused pocket) with a coaxial 1/4" hex drill shank.

    Usage orientation: pocket opens at z=0 (bottom), hex shank rises from the
    cap top (z=SOCKET_HEIGHT) to z=SOCKET_HEIGHT+SHANK_LENGTH.

    For printing: flip so the shank points up and the pocket opens onto the bed.
    """
    # 45° pyramid roof solid (algebra mode — built outside the BuildPart context
    # so SlotOverall isn't captured by the active builder), subtracted below.
    roof = loft(
        [
            Plane.XY.offset(POCKET_DEPTH) * SlotOverall(TPU_LONG, TPU_SHORT),
            Plane.XY.offset(POCKET_DEPTH + ROOF_HEIGHT)
            * SlotOverall(ROOF_RIDGE_LONG, ROOF_RIDGE_SHORT),
        ],
        ruled=True,
    )

    with BuildPart() as bp:
        # Stadium tube (identical envelope to peg_turner socket body)
        with BuildSketch():
            SlotOverall(SOCKET_LONG, SOCKET_SHORT)
        extrude(amount=SOCKET_HEIGHT)

        # TPU pocket — stadium bore from bottom (z=0 upward), exact-fit to insert
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

        # 45° pyramid roof over the pocket (overhang-free ceiling)
        add(roof, mode=Mode.SUBTRACT)

        # Hex shank rising coaxially from the cap top
        with BuildSketch(Plane.XY.offset(SOCKET_HEIGHT)):
            RegularPolygon(HEX_RADIUS, side_count=6)
        extrude(amount=SHANK_LENGTH)

        # Stress-relief fillet where the shank meets the cap top
        base_edges = [
            e for e in bp.edges()
            if abs(e.center().Z - SOCKET_HEIGHT) < 0.5
            and (e.center().X ** 2 + e.center().Y ** 2) ** 0.5 < HEX_RADIUS + 1.0
        ]
        if base_edges:
            fillet(base_edges, SHANK_FILLET)

        # Lead-in chamfer at the shank tip for easy chuck insertion
        tip_z = SOCKET_HEIGHT + SHANK_LENGTH
        tip_edges = [
            e for e in bp.edges()
            if abs(e.center().Z - tip_z) < 0.5
        ]
        if tip_edges:
            chamfer(tip_edges, SHANK_LEAD_IN)

    return bp.part


# ═══════════════════════════════════════════════════════
#  Build & Export
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    print("Building drill socket...")
    socket = build_drill_socket()

    export_step(socket, str(OUT / "drill_socket.step"))
    print(f"Exported {OUT / 'drill_socket.step'}")

    try:
        from ocp_vscode import show
        socket.label = "Drill Socket"
        socket.color = Color("dimgray")
        show(socket, names=["Drill Socket"], colors=["dimgray"], alphas=[1.0])
    except Exception:
        pass
