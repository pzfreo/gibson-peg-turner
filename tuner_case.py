#!/usr/bin/env python3
"""Print-in-place "book" clamshell PACKAGING CASE for a Gibson tuner kit.

Folds shut like a book and holds the two assembled 5-gang tuners plus the spare
parts (two each of peg, post and wheel) in pockets at the ends. The remaining
kit items (peg turner, marking jig, screws/washers) are chunky and ship as loose
fill in the postal box.

Design, in order of importance:

  * BOTH GANGS IN THE BASE: the two mirror gangs sit SIDE-BY-SIDE in the base
    leaf, bodies DOWN in snug cradles, with their worm turn-button CAPS pointing
    UP. The caps are the only part of either gang that reaches above the mounting
    plate (~6.5 mm), so they are the only things that cross the closed seam.

  * LID = HOLEY COVER: the lid leaf is a plain cover whose inner (seam) face has
    ten blind receiver holes -- one per button cap. When the book folds shut the
    caps drop into the holes, which locates the two halves and shields the caps.
    Because the lid carries no gang of its own, nothing else can collide: the
    earlier "one gang per leaf" idea failed precisely because each leaf's solid
    cradle sat where the OTHER leaf's caps needed to go. (Verified by dropping
    the real assembly STEPs in and measuring interference.)

  * CRADLES: each gang sits in a snug, REMOVABLE, feature-based cradle (a body
    channel + five ring-eyelet relief lobes + an open button slot) at ~0.4 mm
    clearance -- NOT a literal negative (which would have undercuts that trap the
    part). Every cradle opens straight UP so the gang lifts out vertically. The
    two button columns sit at the leaf centre +-GANG_D with the bodies splaying
    outward, ring eyelets toward the side walls.

  * HINGE: a piano hinge from the `pip-hinge` library (Knuckle.SMALL), the only
    thing joining the two leaves; it prints in place. SMALL keeps the knuckle to
    ~3.35 mm radius with a ~22deg self-supporting ramp.

  * CATCH: Ø6 x 3 mm disc magnets at the two front corners (the long edge
    opposite the hinge), in press-fit pockets with a boss-fillet pushed into the
    interior corner -- the add_corner_magnet_pockets pattern from pip-hinge's
    examples/clamshell.py. Magnet-to-magnet when the book is shut.

  * PRINT POSE: base and lid lie flat and coplanar on the bed, joined only at
    the hinge ("open 180deg"). The hinge axis runs along Y; the base leaf
    extends +X, the lid leaf -X. base and lid stay SEPARATE print-in-place
    bodies (no boolean union) so the mechanism is free to move once printed.

The gang geometry is measured from the real assembly STEPs: worm turn-button
caps (Ø7.5) at gang-local X=20 projecting to Z=+6.5, the body (housings, worm
drums, ring eyelets) hanging 11.25 mm below the plate. Wall height captures the
below-plate body so the plate sits flush with the rim and the caps project into
the lid holes.

The piano hinge is derived from `pip-hinge`, itself a build123d port of
"Parametric print-in-place hinge. FreeCAD." by r0berts on Printables
(https://www.printables.com/model/1395662), licensed CC BY 4.0. This case
inherits that licence for the hinge geometry; credit r0berts and pzfreo.

Usage:
    python tuner_case.py                 # step + stl, print pose + closed viz
    python tuner_case.py --format stl
"""

import argparse
import copy
import math
import os
import sys
from pathlib import Path

OUT = Path(__file__).parent

# --- Locate pip-hinge (the print-in-place piano hinge library) ---------------
_pip = Path(os.environ.get("PIP_HINGE", OUT.parent / "pip-hinge")) / "src"
if not (_pip / "pip_hinge").is_dir():
    sys.exit(
        f"Cannot find pip-hinge at {_pip}.\n"
        "Clone it next to this repo, or set PIP_HINGE to its path."
    )
sys.path.insert(0, str(_pip))

from build123d import (  # noqa: E402
    Align,
    Axis,
    Box,
    Compound,
    Cylinder,
    Part,
    export_step,
    export_stl,
)

from pip_hinge import HingeParams, Knuckle, make_hinge  # noqa: E402


# ===========================================================================
# Gang feature geometry (measured from assembly_5gang_rh.step).
#
# Gang frame: mounting plate at Z~=0; the worm turn-button CAPS project UP to
# Z=+POST_TOP in a column at X=POST_X; everything else (housings, worm drums,
# ring eyelets) hangs BELOW the plate to Z=-BODY_BOTTOM. Body footprint in X is
# [BODY_XMIN, BODY_XMAX] with the ring eyelets reaching out to BUTTON_XMAX. The
# LH gang is the mirror across X. Only the button caps cross the closed seam.
# ===========================================================================
HOUSING_Y = (18.1, 45.3, 72.5, 99.7, 126.9)   # five housing centres along Y
GANG_LEN = 145.0                               # gang length (Y)

POST_X = 20.0           # worm turn-button column X (gang-local); the cradle and
#                         the lid receiver holes both key off this column
POST_OD = 6.0           # button stem Ø
POST_TOP = 6.5          # button caps rise this far above the plate (+Z)

BUTTON_Y = (15.0, 42.2, 69.4, 96.6, 123.8)     # button-cap centres in Y (local)
BUTTON_CAP_D = 7.5                             # button-cap Ø (what projects up)

BODY_XMIN = 13.0        # frame body min X (housing outer wall)
BODY_XMAX = 30.7        # frame body max X (worm-entry wall)
BUTTON_XMAX = 43.0      # ring-eyelet outer X (sets cradle relief width)
BUTTON_OD = 9.8         # ring/relief Ø (sets relief-lobe Y width)
BODY_BOTTOM = 11.25     # body hangs this far below the plate (-Z)

GANG_CLR = 0.4          # snug clearance added around every gang feature


# ===========================================================================
# Case / clamshell parameters.
#
# BOTH gangs sit side-by-side in the BASE leaf, bodies down, button caps up.
# The LID is a plain cover whose inner (seam) face has ten receiver holes that
# the caps drop into when the book closes -- locating the book and protecting
# the caps. Only the caps cross the seam, so nothing else can collide.
# ===========================================================================
WALL_H = 15.0           # leaf wall height. The gang body rests on the cradle
#                         floor (plate ~1.75 mm below the rim) so the ring
#                         eyelets -- which rise ~1.25 mm above the plate -- clear
#                         under the rim; the 6.5 mm button caps then project
#                         above the rim into the lid receiver holes.
WALL_T = 2.5            # outer wall thickness
FLOOR_T = 2.0           # floor thickness under the gang cradle
PIVOT_Z_OFFSET = 0.2    # HingeParams default; lifts the seam 2*0.2 mm

STATIONS = 8            # piano-hinge tab count (even); clasp_width=hinge_len/8
PIVOT_CLEARANCE = 0.45  # radial pin/bore gap (FDM-tuned; pip default 0.6)

# Two gangs in the base: button columns at the leaf centre +-GANG_D, bodies
# splaying outward (ring eyelets toward the side walls). The central divider
# land between the two body channels is 2*GANG_D - 14.8 mm wide; GANG_D=10 gives
# a robust ~5.2 mm fin (GANG_D=8 left a flimsy 1.2 mm one). Widening GANG_D only
# grows the centre -- side-wall clearance is independent of it.
GANG_D = 10.0                  # button-column offset from the base-leaf centre
EDGE_CLR = 2.5                 # outermost gang feature -> side wall clearance
Y_END_MARGIN = WALL_T + 20.0   # end margin: holds the side-lying spare pockets
#                                (was +8.0; widened to fit the ~16 mm spare pegs)
GANG_Y0 = -GANG_LEN / 2.0      # gang min-Y (gangs centred on Y=0)

# Button-cap receiver holes in the lid.
RECV_D = BUTTON_CAP_D + 1.0    # Ø8.5: 0.5 mm radial clearance round the cap
RECV_DEPTH = POST_TOP + 1.0    # 7.5 mm deep blind holes from the seam face

# Spare-part pockets: TWO each of peg, post and wheel ship per set. The parts are
# too tall to stand in the ~13 mm cavity, so one of each lies on its side (axis
# along Y) in each of the two Y-end margins, opening UP and capped flat by the
# lid when the book shuts -- the same top-opening box pockets as the gang cradles.
SPARE_PEG_D = 12.5     # button/worm peg: the ring OD is the widest part
SPARE_PEG_L = 16.0
SPARE_POST_D = 7.5     # string post: the cap OD is the widest part
SPARE_POST_L = 14.8
SPARE_WHEEL_D = 7.6    # worm-wheel disc
SPARE_WHEEL_L = 7.7
SPARE_CLR = 0.5        # clearance around each spare

# ---------------------------------------------------------------------------
# Magnet catch (Ø6 x 3 disc magnets), pockets per pip-hinge clamshell example.
# ---------------------------------------------------------------------------
MAGNET_OD = 6.0
MAGNET_T = 3.0
POCKET_RADIAL_CLR = 0.1
POCKET_R = MAGNET_OD / 2 + POCKET_RADIAL_CLR
POCKET_DEPTH = MAGNET_T + 0.1
BOSS_R = POCKET_R + 1.5


# ---------------------------------------------------------------------------
# Hinge helpers (lifted from pip-hinge examples/clamshell.py).
# ---------------------------------------------------------------------------
def _split_hinge_by_side(hinge):
    """Sort the hinge's solids into cs-side (+X bias) and ps-side (-X bias).

    At the default mounting_flat (< pivot_clearance) the bare hinge comes back
    fragmented; classify the fragments by bbox X-centre rather than unpacking,
    then fuse each into its leaf wall. (Same approach as clamshell.py.)
    """
    cs, ps = [], []
    for s in hinge.solids():
        bb = s.bounding_box()
        (cs if (bb.min.X + bb.max.X) >= 0 else ps).append(s)
    return Compound(cs), Compound(ps)


# ---------------------------------------------------------------------------
# Cradle pockets.
# ---------------------------------------------------------------------------
def _gang_pocket(leaf: Part, x_sign: int, post_x_leaf: float, floor_top: float,
                 wall_h: float) -> Part:
    """Cut the feature-silhouette gang cradle into a leaf, opening UPWARD.

    `x_sign` is +1 for the base/RH leaf (gang body on the +X side of its post
    row) and -1 for the lid/LH leaf (mirror). `post_x_leaf` is the X coordinate
    of the gang's POST ROW in leaf coordinates; every other gang feature is
    placed relative to it using the measured gang-local offsets. The pockets are
    cut down from the leaf top (Z = floor_top + cavity) leaving FLOOR_T beneath;
    each opens straight up so the gang lifts out vertically.
    """
    cuts = []
    # Pocket floor sits FLOOR_T above the bed; every pocket is cut from well
    # above the wall top straight down to that floor, so it opens UPWARD and the
    # gang lifts out vertically. The body occupies the full FLOOR_T..wall_top
    # cavity (11 mm) with its plate near the wall top and posts projecting above.
    floor_z = floor_top                         # = FLOOR_T
    cut_top = wall_h + POST_TOP + 1.0           # safely above the wall + posts

    def box_cut(x_lo, x_hi, y_lo, y_hi):
        c = Box(x_hi - x_lo, y_hi - y_lo, cut_top - floor_z,
                align=(Align.MIN, Align.MIN, Align.MIN))
        c = c.translate((x_lo, y_lo, floor_z))
        cuts.append(c)

    # gang-local X offsets relative to the post row (POST_X = 20):
    body_lo = (BODY_XMIN - POST_X)      # -7.0
    body_hi = (BODY_XMAX - POST_X)      # +10.7
    btn_hi = (BUTTON_XMAX - POST_X)     # +23.0
    post_half = POST_OD / 2 + GANG_CLR

    y0 = GANG_Y0
    y1 = GANG_Y0 + GANG_LEN

    # --- Main body channel: the frame housings + worm-entry block. Snug in X
    #     to the body silhouette (not the full button width), full gang length.
    #     Compute the two body edges in leaf X explicitly (x_sign handles the
    #     LH mirror).
    e1 = post_x_leaf + x_sign * (body_lo - GANG_CLR)
    e2 = post_x_leaf + x_sign * (body_hi + GANG_CLR)
    box_cut(min(e1, e2), max(e1, e2), y0 - GANG_CLR, y1 + GANG_CLR)

    # --- Worm-button relief lobes: five pockets on the button side, each at a
    #     housing centre, reaching out to the button cap. Buttons hang in the
    #     lower (below-plate) band, so these are full body-depth too.
    bl1 = post_x_leaf + x_sign * (body_hi + GANG_CLR)
    bl2 = post_x_leaf + x_sign * (btn_hi + GANG_CLR)
    for yc in HOUSING_Y:
        ylo = GANG_Y0 + yc - BUTTON_OD / 2 - GANG_CLR
        yhi = GANG_Y0 + yc + BUTTON_OD / 2 + GANG_CLR
        box_cut(min(bl1, bl2), max(bl1, bl2), ylo, yhi)

    # --- Post slot: a narrow channel over the post row so the plate is captured
    #     by ledges on each side but the posts project freely up to the seam.
    box_cut(post_x_leaf - post_half, post_x_leaf + post_half,
            y0 - GANG_CLR, y1 + GANG_CLR)

    for c in cuts:
        leaf = leaf - c
    return leaf


# ---------------------------------------------------------------------------
# Spare-part end pockets.
# ---------------------------------------------------------------------------
def _spare_pockets(leaf: Part, xc: float, floor_top: float, wall_h: float) -> Part:
    """Cut the spare-part pockets into the base leaf's two Y-end margins.

    One peg, one post and one wheel lie on their sides (axis along Y) in each end
    margin -- two of each across the set. Each is a box pocket cut down from the
    rim, deep enough to capture the part between its floor and the closed lid, and
    opening straight UP so the part lifts out vertically (like the gang cradles).
    The three sit in a row across X, flush to the gang-side end and extending
    outward toward the end wall.
    """
    # (diameter, length, x-offset from the leaf interior centre) per spare.
    spares = (
        (SPARE_PEG_D, SPARE_PEG_L, -20.0),
        (SPARE_POST_D, SPARE_POST_L, -2.0),
        (SPARE_WHEEL_D, SPARE_WHEEL_L, 14.0),
    )
    gang_end = GANG_Y0 + GANG_LEN              # +72.5: gang extent toward +Y
    for y_sign in (-1, +1):
        y_inner = y_sign * (gang_end + 1.5)    # 1.5 mm clear of the gang end
        for d, ln, xoff in spares:
            w = d + SPARE_CLR
            depth = d + SPARE_CLR              # pocket floor = wall_h - depth
            length = ln + SPARE_CLR
            y_a, y_b = y_inner, y_inner + y_sign * length
            cut = Box(w, abs(y_b - y_a), depth + 1.0,
                      align=(Align.CENTER, Align.MIN, Align.MAX))
            cut = cut.translate((xc + xoff, min(y_a, y_b), wall_h + 1.0))
            leaf = leaf - cut
    return leaf


# ---------------------------------------------------------------------------
# Lid button-cap receiver holes.
# ---------------------------------------------------------------------------
def _button_receiver_holes(lid: Part, hole_xs, wall_h: float) -> Part:
    """Drill the ten blind button-cap receiver holes into the lid seam face.

    `hole_xs` are the two button-column X positions in LID coordinates (already
    mirrored from the base, so a hole at lid X = -(base button X) lands on that
    cap after the 180deg fold). Holes open at the rim (Z=wall_h) and go
    RECV_DEPTH deep; when the lid folds shut each base button cap drops in.
    """
    for hx in hole_xs:
        for yn in BUTTON_Y:
            bore = Cylinder(
                RECV_D / 2, RECV_DEPTH + 1.0,
                align=(Align.CENTER, Align.CENTER, Align.MAX),
            )
            lid = lid - bore.translate((hx, GANG_Y0 + yn, wall_h + 1.0))
    return lid


# ---------------------------------------------------------------------------
# Magnet corner pockets (from pip-hinge examples/clamshell.py).
# ---------------------------------------------------------------------------
def add_corner_magnet_pockets(half, x_sign: int, leaf_outer: float,
                              leaf_depth: float, leaf_w: float, wall_h: float):
    """Add Ø6 x 3 magnet pockets at the two FRONT corners (long edge opposite
    the hinge). Each pocket sits inside a cylindrical boss pushed into the
    interior corner so the boss radius fillets the corner. The pocket opens
    downward from the wall top; a 0.x mm skin is left to the outside. Mirrors
    add_corner_magnet_pockets in pip-hinge's clamshell example.
    """
    x_corner = x_sign * (leaf_outer + leaf_depth - WALL_T)
    for y_sign in (-1, +1):
        y_corner = y_sign * (leaf_w / 2 - WALL_T)
        x_boss = x_corner - x_sign * BOSS_R / math.sqrt(2)
        y_boss = y_corner - y_sign * BOSS_R / math.sqrt(2)
        boss = Cylinder(
            radius=BOSS_R, height=wall_h,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        ).translate((x_boss, y_boss, 0))
        pocket = Cylinder(
            radius=POCKET_R, height=POCKET_DEPTH,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        ).translate((x_boss, y_boss, wall_h - POCKET_DEPTH))
        half = (half + boss) - pocket
    return half


def solid_leaf(x_sign: int, leaf_outer: float, leaf_depth: float, leaf_w: float,
               wall_h: float) -> Part:
    """SOLID block leaf extending from the hinge axis in the given X sign.

    The block starts solid; the gang cradle and secondary-item pockets carve the
    wells out of it, and the lands left between those pockets are exactly the
    snug walls that locate each item. (FDM infill keeps the solid-modelled block
    light when printed.) Pre-hollowing the interior here would make every
    feature pocket a subset of the empty cavity and thus a no-op -- that bug is
    why an earlier version produced two empty boxes.

    `leaf_outer` is |X| of the hinge-side back wall (= W from the hinge, where
    the leaf attaches). `leaf_depth` is the leaf's X extent (front-to-back),
    `leaf_w` its Y width.
    """
    if x_sign > 0:
        x_min = leaf_outer
    else:
        x_min = -(leaf_outer + leaf_depth)
    align = (Align.MIN, Align.CENTER, Align.MIN)
    return Box(leaf_depth, leaf_w, wall_h, align=align).translate((x_min, 0, 0))


def build_case():
    """Build the print-pose bodies and a closed-pose compound.

    Returns (print_compound, closed_compound) where print_compound holds the two
    SEPARATE print-in-place bodies [base, lid] flat on the bed (the hinge pin is
    moulded captive inside the lid), and closed_compound is the same folded shut
    for visualisation.
    """
    # --- Leaf footprints -----------------------------------------------------
    # Each leaf holds the 145 mm gang (Y) centred, plus an end margin each side.
    leaf_w = GANG_LEN + 2 * Y_END_MARGIN                     # = 166 mm

    hinge_length = leaf_w - 2 * WALL_T - 10.0                # hinge a bit short of ends

    # Hinge geometry: case_h includes the pivot offset so the SMALL knuckle
    # still lands on the bed when printed flat (see clamshell docs).
    case_h = WALL_H + PIVOT_Z_OFFSET
    params = HingeParams(
        case_h=case_h,
        hinge_length=hinge_length,
        stations=STATIONS,
        knuckle=Knuckle.SMALL,
        pivot_clearance=PIVOT_CLEARANCE,   # radial pin/bore gap (FDM-tuned)
        # mounting_flat / clasp_clearance at defaults
    )
    res = params._resolve()
    leaf_outer = res["W"]          # |X| of the leaf back wall (hinge side)

    # --- Leaf X depth (front-to-back). Both leaves share one depth so their
    # front (magnet) faces meet when closed. The base spans the two side-by-side
    # gangs: button columns at the interior centre +-GANG_D, each gang reaching
    # (BUTTON_XMAX - POST_X) outward to its ring eyelets, plus EDGE_CLR.
    half_span = GANG_D + (BUTTON_XMAX - POST_X) + EDGE_CLR
    leaf_depth = 2 * half_span + 2 * WALL_T
    xc = leaf_outer + WALL_T + half_span    # base interior centre (X)
    rh_bx = xc + GANG_D                      # RH button column (front gang)
    lh_bx = xc - GANG_D                      # LH button column (hinge-side gang)

    # ----- BASE leaf: two mirrored gang cradles, side by side -----
    base = solid_leaf(+1, leaf_outer, leaf_depth, leaf_w, WALL_H)
    base = _gang_pocket(base, +1, rh_bx, FLOOR_T, WALL_H)   # RH: body on +X
    base = _gang_pocket(base, -1, lh_bx, FLOOR_T, WALL_H)   # LH: body on -X
    base = _spare_pockets(base, xc, FLOOR_T, WALL_H)        # spares in end margins

    # ----- LID leaf: plain cover with the ten button-cap receiver holes.
    # Each hole sits at lid X = -(base button X) so it lands on its cap after
    # the 180deg fold about X=0.
    lid = solid_leaf(-1, leaf_outer, leaf_depth, leaf_w, WALL_H)
    lid = _button_receiver_holes(lid, (-rh_bx, -lh_bx), WALL_H)

    # ----- Magnet corner pockets (front edge, opposite the hinge) -----
    base = add_corner_magnet_pockets(base, +1, leaf_outer, leaf_depth, leaf_w, WALL_H)
    lid = add_corner_magnet_pockets(lid, -1, leaf_outer, leaf_depth, leaf_w, WALL_H)

    # ----- HINGE: fuse the two leaves into the back walls -----
    cs, ps = _split_hinge_by_side(make_hinge(params))
    cs = cs.translate((0, 0, case_h))      # axis to wall top + pivot offset
    ps = ps.translate((0, 0, case_h))
    base = base + cs
    lid = lid + ps

    # ----- PIN -----
    # NOTE on body count: pip-hinge is a *captured-pin* print-in-place design --
    # the pin is moulded integrally into the ps (lid) leaf and captured by the
    # bored cs knuckles on the base leaf. There is therefore no separable third
    # "pin" body to expose: the printed, free-to-move mechanism is exactly TWO
    # bodies, base and lid-with-integral-pin, kept un-fused to each other so the
    # joint articulates. We honour "keep print-in-place bodies separate" by
    # never boolean-unioning base to lid; the pin lives inside `lid`.

    # POSE 1: UNFOLDED (flat print). base and lid are independent bodies.
    print_parts = Compound(children=[base, lid])

    # POSE 2: CLOSED. Fold the lid 180deg about the hinge axis (line X=0,
    # Z=case_h, parallel to Y) onto the base. Independent copies (a shape can
    # only have one parent).
    base_c = copy.copy(base)
    lid_closed = copy.copy(lid).rotate(Axis((0, 0, case_h), (0, 1, 0)), 180)
    closed = Compound(children=[base_c, lid_closed])

    return print_parts, closed


def main():
    parser = argparse.ArgumentParser(
        description="Print-in-place book clamshell case for the Gibson tuner kit",
    )
    parser.add_argument("--format", choices=["step", "stl", "both"], default="both")
    args = parser.parse_args()

    print("Building tuner case (unfolded print pose + closed visualisation)...")
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
