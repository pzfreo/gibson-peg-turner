#!/usr/bin/env python3
"""Print-in-place clamshell PACKAGING CASE for a set of Gibson tuning machines.

A single-print, clamshell case that holds the whole tuner kit: two assembled
5-gang tuner frames, the marking jig, the peg turner, and the loose spares
(peg heads, wheels, posts, screws/washers). The base is a solid block with
rectangular/cylindrical pockets milled into it to cradle each part; the lid is
a plain cover (a floor plate plus a perimeter rim that nests inside the base
walls). The parts are retained by the base pockets, so the lid carries no
pockets of its own.

Three design choices, all deliberate:

  * HINGE: a print-in-place PIN (barrel) hinge, not a living hinge. Living
    hinges fatigue and crack after a few dozen cycles; a barrel hinge with a
    captured pin lasts indefinitely. ~9 alternating knuckles share a Ø3 pin.
  * CATCH: two Ø6x3 disc magnets (one at each front corner), not a printed
    snap latch. Snap latches wear and lose grip; magnets are maintenance-free
    and let the lid be opened/closed endlessly. Each magnet hides in a blind
    pocket behind a thin skin so it sits flush and pulls through the wall.
  * PRINT POSE: the case prints UNFOLDED — base and lid lie flat and coplanar
    on the bed, joined only at the hinge, lid "open 180 degrees". This needs no
    supports for the cavities and prints the hinge knuckles cleanly.

Everything is a separate (non-fused) solid: base, lid, and pin keep their
modelled clearances so the print-in-place mechanism is actually free to move.

Usage:
    python tuner_case.py                 # both step + stl, all configs
    python tuner_case.py --format stl
"""

import argparse
from pathlib import Path

from build123d import (
    Align,
    Axis,
    Box,
    Compound,
    Cylinder,
    Location,
    Part,
    Plane,
    export_step,
    export_stl,
)

OUT = Path(__file__).parent

# ---------------------------------------------------------------------------
# Part envelopes (real measured, mm) and fit allowances.
# ---------------------------------------------------------------------------
CLR = 0.7          # clearance added around every part in its pocket
WALL = 2.5         # outer wall thickness
FLOOR = 2.0        # base floor thickness under the pockets
DIV = 2.0          # divider wall thickness between pockets
CAV = 20.0         # cavity (pocket) depth: 18mm tallest part + headroom

# The three long parts run along Y for the gang length.
GANG_W = 30.0      # gang width  (X)
GANG_L = 145.0     # gang length (Y)
GANG_H = 18.0      # gang height (Z)  -> tallest part, sets CAV
JIG_W = 11.0       # marking jig: 11x11 prismatic pocket along its length
JIG_L = 145.0

# Pocket footprints = envelope + 2*CLR (clearance on each side).
GANG_PX = GANG_W + 2 * CLR      # ~31.4
GANG_PY = GANG_L + 2 * CLR      # ~146.4
JIG_PX = JIG_W + 2 * CLR        # ~12.4
JIG_PY = JIG_L + 2 * CLR        # ~146.4 (same length as the gangs)

# End zone (Y beyond the long pockets).
PEG_TURNER_X = 44.0 + 2 * CLR   # lies on its side: 44 footprint -> ~45.4
PEG_TURNER_Y = 69.0 + 2 * CLR   # 69 footprint -> ~70.4
PEG_TURNER_H = 17.0             # lying down it is 17 tall (fits CAV easily)

PEGHEAD_X = 28.0 + 2 * CLR      # spare peg head 28 x 12.5 x 13
PEGHEAD_Y = 12.5 + 2 * CLR
PEGHEAD_H = 13.0
WHEEL_D = 8.0 + 2 * CLR         # spare wheel Ø8 x 9
WHEEL_H = 9.0
POST_D = 8.0 + 2 * CLR          # spare post  Ø8 x 15
POST_H = 15.0
BIN = 30.0                      # screw/washer bin ~30 x 30
BIN_DEPTH = 12.0

# ---------------------------------------------------------------------------
# Hinge (print-in-place pin/barrel) and magnet catch.
# ---------------------------------------------------------------------------
BARREL_R = 4.0     # knuckle outer radius
N_KNUCKLE = 9      # base owns 1,3,5,7,9 ; lid owns 2,4,6,8
KN_GAP = 0.4       # axial gap between adjacent knuckles (don't fuse)
PIN_R = 1.5        # Ø3.0 pin
BORE_R = 1.95      # Ø3.9 knuckle bore (~0.45 radial clearance over pin)

MAG_D = 6.0        # disc magnet Ø6 x 3
MAG_T = 3.0
MAG_POCKET_D = 6.2 # press-fit pocket Ø6.2
MAG_SKIN = 0.6     # skin left to the outside so the magnet hides flush

LID_RIM = 6.0      # lid perimeter rim/lip height
LID_FLOOR = 2.0    # lid floor plate thickness
RIM_CLR = 0.3      # rim nests inside base walls with this clearance
LID_TOP = LID_FLOOR + LID_RIM   # lid total height (mouth/open face), = 8.0

# Hinge axis height. For a clamshell that folds 180 deg about a single Y axis,
# the two mating mouths must be equidistant from that axis on opposite sides:
#   base mouth at Z=base_h, lid mouth at Z=LID_TOP  ->  axis at their midpoint.
# (The spec suggested Z~4 "near the bed", but that is geometrically impossible
# for a 22mm-deep base: at Z=4 the folded lid would pass through the base. The
# midpoint is the only height at which the rim nests into the base mouth.)
# base_h = FLOOR + CAV = 22, so HINGE_Z = (22 + 8)/2 = 15.
HINGE_Z = (FLOOR + CAV + LID_TOP) / 2


def _pockets(base: Part, ox: float, oy: float, floor_top: float) -> Part:
    """Cut all part pockets into the base block.

    `ox, oy` is the interior origin (inside face of the front+min-Y walls).
    `floor_top` is the Z of the pocket floor's top reference (= base top).
    Pockets are cut DOWNWARD from the top face to depth CAV (or shallower for
    the small spares), leaving FLOOR mm of solid beneath. The dividers between
    the long pockets survive because we cut individual recesses, not one slot.
    """

    cuts = []

    def box_pocket(w, d, h, x, y):
        c = Box(w, d, h, align=(Align.MIN, Align.MIN, Align.MAX))
        cuts.append(c.locate(Location((ox + x, oy + y, floor_top))))

    def cyl_pocket(dia, h, cx, cy):
        c = Cylinder(dia / 2, h, align=(Align.CENTER, Align.CENTER, Align.MAX))
        cuts.append(c.locate(Location((ox + cx, oy + cy, floor_top))))

    # --- Long pockets across width X: gangA | div | jig | div | gangB ---
    x = 0.0
    box_pocket(GANG_PX, GANG_PY, CAV, x, 0.0)          # gang A
    x += GANG_PX + DIV
    box_pocket(JIG_PX, JIG_PY, CAV, x, 0.0)            # jig (11x11 prism)
    x += JIG_PX + DIV
    box_pocket(GANG_PX, GANG_PY, CAV, x, 0.0)          # gang B

    # --- End zone (beyond the long pockets in Y) ---
    end_y = max(GANG_PY, JIG_PY) + DIV                 # start of end zone

    # Peg turner lies on its side along the gang-A side of the end zone.
    box_pocket(PEG_TURNER_X, PEG_TURNER_Y, PEG_TURNER_H, 0.0, end_y)

    # Remaining X strip beside the peg turner holds the spares.
    sx = PEG_TURNER_X + DIV                             # left edge of spares strip
    sy = end_y + 1.0
    # Two peg-head pockets, stacked in Y.
    box_pocket(PEGHEAD_X, PEGHEAD_Y, PEGHEAD_H, sx, sy)
    box_pocket(PEGHEAD_X, PEGHEAD_Y, PEGHEAD_H, sx, sy + PEGHEAD_Y + 2.0)
    # Screw/washer bin below the peg heads.
    biny = sy + 2 * (PEGHEAD_Y + 2.0) + 1.0
    box_pocket(BIN, BIN, BIN_DEPTH, sx, biny)
    # Wheels and posts: bores in a row beneath the bin.
    bores_y = biny + BIN + 4.0
    cyl_pocket(WHEEL_D, WHEEL_H, sx + 5, bores_y)
    cyl_pocket(WHEEL_D, WHEEL_H, sx + 15, bores_y)
    cyl_pocket(POST_D, POST_H, sx + 25, bores_y)
    cyl_pocket(POST_D, POST_H, sx + 35, bores_y)

    for c in cuts:
        base = base - c
    return base


def _hinge_knuckles(length_y: float, owner: str, x_axis: float, z_axis: float):
    """Return the list of knuckle cylinders this body owns.

    Knuckles are cylinders (axis along Y) centred at (x_axis, *, z_axis), each
    bored Ø3.9 for the pin. `owner` is 'base' (odd index 1,3,5,7,9) or 'lid'
    (even 2,4,6,8). Knuckles tile the full Y length with KN_GAP between them so
    adjacent (opposite-owner) knuckles never fuse.
    """
    seg = (length_y - (N_KNUCKLE - 1) * KN_GAP) / N_KNUCKLE
    knuckles = []
    for i in range(N_KNUCKLE):
        idx = i + 1
        is_base = (idx % 2 == 1)
        if (owner == "base") != is_base:
            continue
        y0 = i * (seg + KN_GAP)
        cyl = Cylinder(BARREL_R, seg, align=(Align.CENTER, Align.CENTER, Align.MIN))
        cyl = cyl.rotate(Axis.X, -90)  # axis -> +Y
        cyl = cyl.locate(Location((x_axis, y0, z_axis)))
        bore = Cylinder(BORE_R, seg + 0.02, align=(Align.CENTER, Align.CENTER, Align.MIN))
        bore = bore.rotate(Axis.X, -90).locate(Location((x_axis, y0 - 0.01, z_axis)))
        knuckles.append(cyl - bore)
    return knuckles


def _magnet_pockets_base(base: Part, ly: float, top: float):
    """Cut the two magnet pockets into the BASE front wall (X = min, the long
    edge opposite the hinge) and return (base, centre_z).

    Blind pockets: axis along X, the disc face toward +X (interior), closed end
    MAG_SKIN inside the -X (outside) face so the magnet hides flush. One near
    each end of the front wall. The Y positions match the lid pockets so they
    sit magnet-to-magnet when the case is folded closed."""
    cz = top - MAG_T - 1.0 + MAG_T / 2          # pocket centre Z
    for y in (WALL + 12.0, ly - WALL - 12.0):
        c = Cylinder(MAG_POCKET_D / 2, MAG_T, align=(Align.CENTER, Align.CENTER, Align.CENTER))
        c = c.rotate(Axis.Y, -90)               # axis -> +X
        # centre X = MAG_SKIN + MAG_T/2 from the -X face.
        c = c.locate(Location((MAG_SKIN + MAG_T / 2, y, cz)))
        base = base - c
    return base, cz


def build_case():
    """Build the three deliverable configs.

    Returns (print_compound, closed_compound) where:
      * print_compound = base + lid + pin, UNFOLDED flat print pose, separate
        solids (no boolean union between bodies).
      * closed_compound = the same, lid folded 180 degrees onto the base.
    """
    # --- Base outer dimensions ---
    # Interior width Wi = gangA + div + jig + div + gangB.
    Wi = GANG_PX + DIV + JIG_PX + DIV + GANG_PX
    # Interior length Li = long-pocket length + end zone.
    end_zone = PEG_TURNER_Y + 6.0
    Li = max(GANG_PY, JIG_PY) + DIV + end_zone

    base_h = FLOOR + CAV                       # total base block height
    ox = WALL                                  # interior origin X (front wall inside)
    oy = WALL                                  # interior origin Y
    outer_w = Wi + 2 * WALL                    # base outer width (X)
    outer_l = Li + 2 * WALL                    # base outer length (Y)

    # ----- BASE BLOCK -----
    # Solid block, bottom at Z=0, top at Z=base_h. Front wall at X=0 (min),
    # hinge/back wall at X=outer_w (max).
    base = Box(outer_w, outer_l, base_h, align=(Align.MIN, Align.MIN, Align.MIN))
    base = _pockets(base, ox, oy, base_h)
    base, base_mag_z = _magnet_pockets_base(base, outer_l, base_h)

    # ----- LID -----
    # Plain cover = floor plate (LID_FLOOR) + perimeter rim (LID_RIM) that nests
    # inside the base walls with RIM_CLR clearance. Built here in its OWN local
    # frame (bottom of plate at Z=0), then placed into the unfolded/closed poses.
    lid_w = outer_w
    lid_l = outer_l
    # Plate
    plate = Box(lid_w, lid_l, LID_FLOOR, align=(Align.MIN, Align.MIN, Align.MIN))
    # Rim: a wall just inside the plate edge that drops into the base opening.
    # Outer face of rim is RIM_CLR inside the base interior wall -> rim outer
    # footprint = interior (Wi x Li) minus 2*RIM_CLR.
    rim_inset = WALL + RIM_CLR
    rim_outer = Box(
        lid_w - 2 * rim_inset, lid_l - 2 * rim_inset, LID_RIM,
        align=(Align.MIN, Align.MIN, Align.MIN),
    ).locate(Location((rim_inset, rim_inset, LID_FLOOR)))
    rim_inner = Box(
        lid_w - 2 * rim_inset - 2 * WALL, lid_l - 2 * rim_inset - 2 * WALL, LID_RIM + 0.01,
        align=(Align.MIN, Align.MIN, Align.MIN),
    ).locate(Location((rim_inset + WALL, rim_inset + WALL, LID_FLOOR)))
    lid = plate + (rim_outer - rim_inner)

    # Lid hinge riser: a back wall along the +X (hinge) edge rising from the lid
    # body up to the hinge axis height so the lid's knuckles are supported on the
    # bed (not floating). Its outer face is at the lid's hinge edge X = outer_w.
    riser = Box(
        WALL, lid_l, HINGE_Z,
        align=(Align.MAX, Align.MIN, Align.MIN),
    ).locate(Location((lid_w, 0, 0)))
    lid = lid + riser

    # Magnet pockets in the lid rim. The magnets must end up magnet-to-magnet
    # over the base pockets after the lid is mirrored across X=hinge_x and folded
    # 180 deg. The base pockets are in the front wall at X~0, at Y = 12 and
    # outer_l-12, with their closed end MAG_SKIN inside the -X face and centre at
    # Z = base_h - MAG_T - 1.0 - MAG_T/2.
    #
    # After mirror(X=hinge_x) a lid point x -> 2*hinge_x - x, and after fold(180
    # about axis X=hinge_x,Z=HINGE_Z): x -> 2*hinge_x - x' , z -> 2*HINGE_Z - z.
    # Net x mapping (mirror then fold) returns to the original lid x; net z is
    # flipped about HINGE_Z. So a lid pocket cut at local x = base_pocket_x and
    # at local z = (2*HINGE_Z - base_pocket_z) lands exactly on the base pocket.
    lid_mag_z = 2 * HINGE_Z - base_mag_z                  # so it maps onto base
    for y in (oy + 12.0, outer_l - WALL - 12.0):
        c = Cylinder(MAG_POCKET_D / 2, MAG_T, align=(Align.CENTER, Align.CENTER, Align.CENTER))
        c = c.rotate(Axis.Y, -90)
        # centre X = MAG_SKIN + MAG_T/2 from the -X face (matches base pocket).
        c = c.locate(Location((MAG_SKIN + MAG_T / 2, y, lid_mag_z)))
        lid = lid - c

    # ----- HINGE -----
    # Axis runs along Y at the back outer edge (X = outer_w = hinge_x), at
    # Z = HINGE_Z (the parting-plane midpoint, see HINGE_Z note above).
    hinge_x = outer_w
    base_kn = _hinge_knuckles(outer_l, "base", hinge_x, HINGE_Z)
    for kn in base_kn:
        base = base + kn

    # Lid knuckles are modelled in the BASE world frame (at hinge_x, HINGE_Z);
    # they are added to the lid AFTER it is mirrored into the unfolded pose so
    # they share the axis with the base knuckles.
    lid_kn = _hinge_knuckles(outer_l, "lid", hinge_x, HINGE_Z)

    # ----- PIN -----
    pin = Cylinder(PIN_R, outer_l - 1.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
    pin = pin.rotate(Axis.X, -90).locate(Location((hinge_x, 0.5, HINGE_Z)))

    # =====================================================================
    # POSE 1: UNFOLDED (flat print). Base sits as built (cavity up). The lid is
    # the mirror of the base half across the hinge plane X = hinge_x, lying flat
    # & coplanar on the bed (plate bottom at Z=0), joined only at the hinge.
    # =====================================================================
    lid_unfold = lid.mirror(Plane(origin=(hinge_x, 0, 0), z_dir=(1, 0, 0)))
    for kn in lid_kn:
        lid_unfold = lid_unfold + kn

    print_parts = Compound(children=[base, lid_unfold, pin])

    # =====================================================================
    # POSE 2: CLOSED. Fold the unfolded lid 180 deg about the hinge axis (line
    # X = hinge_x, Z = HINGE_Z, parallel to Y) onto the base. The lid rim nests
    # down into the base mouth and the magnet pockets land over the base ones.
    # =====================================================================
    # NOTE: a build123d shape can only have ONE parent. `base` and `pin` already
    # belong to `print_parts`, so the closed compound uses independent COPIES.
    import copy
    base_c = copy.copy(base)
    pin_c = copy.copy(pin)
    lid_closed = copy.copy(lid_unfold).rotate(
        Axis((hinge_x, 0, HINGE_Z), (0, 1, 0)), 180
    )
    closed = Compound(children=[base_c, lid_closed, pin_c])

    return print_parts, closed


def main():
    parser = argparse.ArgumentParser(
        description="Print-in-place clamshell case for the Gibson tuner kit",
    )
    parser.add_argument("--format", choices=["step", "stl", "both"], default="both")
    args = parser.parse_args()

    print("Building tuner case (unfolded print pose + closed visualization)...")
    print_parts, closed = build_case()

    pbase = OUT / "tuner_case_print"
    cbase = OUT / "tuner_case_closed"
    if args.format in ("step", "both"):
        export_step(print_parts, str(pbase.with_suffix(".step")))
        print(f"Exported: {pbase.with_suffix('.step')}")
        export_step(closed, str(cbase.with_suffix(".step")))
        print(f"Exported: {cbase.with_suffix('.step')}")
    if args.format in ("stl", "both"):
        export_stl(print_parts, str(pbase.with_suffix(".stl")))
        print(f"Exported: {pbase.with_suffix('.stl')}")


if __name__ == "__main__":
    main()
