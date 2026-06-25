"""tuner_case_v2.py -- ALTERNATIVE packaging design (Option B).

A SECOND, independent design. The original integrated clamshell in
tuner_case.py is left untouched; this file builds a different concept:

  * SHELL  -- a print-in-place clamshell with plain SHELL_WALL (3 mm) walls and
              corner magnets. No internal cradle: just a protective book/box.
  * INSERT -- a separate, BOTTOMLESS tray that slides into the shell and holds the
              two 5-gang tuners + spares. The gang cradle is open top AND bottom so
              foam cushions the tuners on both faces; the short spares keep flush
              floored pockets. It REUSES the validated cradle, spare and
              L/R-engraving cuts from tuner_case.py, so the part fit is identical.

The shell's internal cavity is sized to hold the insert plus FOAM_T of foam
ABOVE and BELOW it (a foam / insert / foam sandwich): the parts are cushioned in
Z and the insert is a slide fit in X/Y. FOAM_T is a parameter (default 10 mm) --
the only knob you change to suit a different foam.

Outputs (tuner_case_v2_*):
  shell_print.{step,stl}  -- the two clamshell leaves, flat, print-in-place
  insert.{step,stl}       -- the insert tray
  assembly.step           -- insert dropped into the open base, for visualising fit
"""
import argparse
import copy
import math
from pathlib import Path

import tuner_case as tc                       # also sets up the pip-hinge import path
from tuner_case import (  # noqa: E402
    HingeParams,
    Knuckle,
    make_hinge,
    _split_hinge_by_side,
    _gang_pocket,
    _spare_pockets,
    _engrave_labels,
)
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

OUT = Path(__file__).resolve().parent

# ===========================================================================
# New parameters for this design.
# ===========================================================================
SHELL_WALL = 3.0     # clamshell wall AND floor thickness (mm)
FOAM_T = 5.0         # foam thickness ABOVE and BELOW the insert (mm); zero Z margin
#                      by design so the foam grips the tuners top and bottom
SLIDE_CLR = 0.4      # X/Y slide clearance between the insert and the shell bore

# Hinge feel (both are HingeParams knobs; defaults printed too stiff).
HINGE_PIVOT_CLR = 0.7        # radial pin/bore gap. 0.6 freed the cracking but was
#                              still hard to rotate; 0.7 spins freely (don't exceed
#                              ~0.8 or the pin goes sloppy).
HINGE_MOUNTING_FLAT = 1.0    # running gap between the knuckle barrel and the leaf
#                              wall = how far apart the two halves sit. The pip
#                              default 0.5 let the barrels rub the sides; 1.0 clears.

# ---------------------------------------------------------------------------
# Insert footprint -- reuses the gang cradle layout from tuner_case so the part
# fit is byte-for-byte the validated one. The insert is a solid slab the height
# of the original cradle cavity (tc.WALL_H), with the gang/spare/label cuts in.
# ---------------------------------------------------------------------------
_HALF_SPAN = tc.GANG_D + (tc.BUTTON_XMAX - tc.POST_X) + tc.EDGE_CLR  # 35.5
INSERT_DEPTH = 2 * _HALF_SPAN                       # X extent (71)
INSERT_WIDTH = tc.GANG_LEN + 2 * tc.Y_END_MARGIN    # Y extent (190)
INSERT_H = tc.WALL_H                                # frame height (15)
# BOTTOMLESS insert: the gang cradle is cut clean THROUGH so the gang rests on
# the bottom foam (foam both sides). The gang therefore stands on the foam, so
# its FULL height -- not floor + height -- sets the Z stack the shell must clear:
STACK_H = tc.BODY_BOTTOM + tc.POST_TOP              # 17.75  (gang total height)


# ---------------------------------------------------------------------------
# INSERT.
# ---------------------------------------------------------------------------
def build_insert() -> Part:
    """The slide-in tray holding both gangs + spares (reuses tuner_case cuts)."""
    xc = _HALF_SPAN                 # gang button columns centred in the slab
    rh_bx = xc + tc.GANG_D
    lh_bx = xc - tc.GANG_D
    insert = Box(INSERT_DEPTH, INSERT_WIDTH, INSERT_H,
                 align=(Align.MIN, Align.CENTER, Align.MIN))   # x 0..71, y +-95, z 0..15
    # floor_top = -1 cuts the gang cradle THROUGH the bottom -> bottomless, so the
    # gang sits on the bottom foam. Spares keep their floored pockets (they are
    # short; a through-pocket would leave them rattling below the top foam).
    insert = _gang_pocket(insert, +1, rh_bx, -1.0, INSERT_H)         # RH gang (through)
    insert = _gang_pocket(insert, -1, lh_bx, -1.0, INSERT_H)         # LH gang (through)
    insert = _spare_pockets(insert, 0.0, tc.FLOOR_T, INSERT_H)       # end spares (floored)
    insert = _engrave_labels(insert, lh_bx, rh_bx, 0.0, INSERT_DEPTH, INSERT_H)

    # Clear the shell's two FRONT-corner magnet bosses: at closed they poke in by
    # (BOSS_R + BOSS_R/sqrt2), so notch that corner out (empty slab here).
    notch = tc.BOSS_R + tc.BOSS_R / math.sqrt(2) + 0.5
    for y_sign in (-1, +1):
        ny = (INSERT_WIDTH / 2 - notch) if y_sign > 0 else (-INSERT_WIDTH / 2)
        cut = Box(notch, notch, INSERT_H + 2.0,
                  align=(Align.MIN, Align.MIN, Align.MIN)).translate(
                      (INSERT_DEPTH - notch, ny, -1.0))
        insert = insert - cut

    # The insert rides up on the bottom foam and protrudes ~6 mm above the closed
    # seam into the lid. During the last few degrees of closure the lid's FRONT
    # wall tilts inward and pinches the insert's front-top edge (~0.18 mm) -- which
    # fouls on a real print. Relieve the FRONT face above the seam (insert-local
    # z = STACK_H/2 = 8.875, independent of foam) so the protruding part clears the
    # swinging wall; below the seam it stays full size and located, and Z/foam is
    # untouched. Front rim is EDGE_CLR (2.5 mm) so FRONT_RELIEF leaves a wall.
    FRONT_RELIEF = 1.5
    seam_local_z = STACK_H / 2.0 - 1.0          # start just below the seam
    relief = Box(FRONT_RELIEF + 1.0, INSERT_WIDTH + 2.0, INSERT_H - seam_local_z + 1.0,
                 align=(Align.MIN, Align.CENTER, Align.MIN)).translate(
                     (INSERT_DEPTH - FRONT_RELIEF, 0, seam_local_z))
    insert = insert - relief
    return insert


# ---------------------------------------------------------------------------
# SHELL leaf: a hollow tray (floor + four walls, all SHELL_WALL thick).
# ---------------------------------------------------------------------------
def _shell_leaf(x_sign: int, leaf_outer: float, leaf_depth: float, leaf_w: float,
                h_int: float, wall: float) -> Part:
    x_min = leaf_outer if x_sign > 0 else -(leaf_outer + leaf_depth)
    outer = Box(leaf_depth, leaf_w, h_int + wall,
                align=(Align.MIN, Align.CENTER, Align.MIN)).translate((x_min, 0, 0))
    cav = Box(leaf_depth - 2 * wall, leaf_w - 2 * wall, h_int + 1.0,
              align=(Align.MIN, Align.CENTER, Align.MIN)).translate(
                  (x_min + wall, 0, wall))                 # open-topped cavity, wall floor
    return outer - cav


def _shell_magnets(leaf: Part, x_sign: int, leaf_outer: float, leaf_depth: float,
                   leaf_w: float, h_total: float, wall: float) -> Part:
    """Ø6x3 magnet pockets at the two FRONT corners (long edge opposite hinge).

    Mirrors tuner_case.add_corner_magnet_pockets: a boss pushed into each corner
    fillets it, and a pocket opens at the rim so closed leaves attract."""
    x_corner = x_sign * (leaf_outer + leaf_depth - wall)
    s = tc.BOSS_R / math.sqrt(2)
    for y_sign in (-1, +1):
        y_corner = y_sign * (leaf_w / 2 - wall)
        x_boss = x_corner - x_sign * s
        y_boss = y_corner - y_sign * s
        boss = Cylinder(tc.BOSS_R, h_total,
                        align=(Align.CENTER, Align.CENTER, Align.MIN)).translate(
                            (x_boss, y_boss, 0))
        pocket = Cylinder(tc.POCKET_R, tc.POCKET_DEPTH,
                          align=(Align.CENTER, Align.CENTER, Align.MIN)).translate(
                              (x_boss, y_boss, h_total - tc.POCKET_DEPTH))
        leaf = (leaf + boss) - pocket
    return leaf


def build_shell(foam_t: float = FOAM_T):
    """Two print-in-place clamshell leaves sized for insert + 2*foam_t in Z."""
    cavity_x = INSERT_DEPTH + 2 * SLIDE_CLR
    cavity_y = INSERT_WIDTH + 2 * SLIDE_CLR
    cavity_z = STACK_H + 2 * foam_t          # foam / insert / foam sandwich (Z)
    h_int = cavity_z / 2.0                    # symmetric clamshell: each leaf half
    leaf_depth = cavity_x + 2 * SHELL_WALL
    leaf_w = cavity_y + 2 * SHELL_WALL
    h_total = h_int + SHELL_WALL              # leaf outer height (floor + cavity)
    case_h = h_total + tc.PIVOT_Z_OFFSET
    hinge_length = leaf_w - 2 * SHELL_WALL - 10.0

    params = HingeParams(case_h=case_h, hinge_length=hinge_length,
                         stations=tc.STATIONS, knuckle=Knuckle.SMALL,
                         pivot_clearance=HINGE_PIVOT_CLR,
                         mounting_flat=HINGE_MOUNTING_FLAT)
    leaf_outer = params._resolve()["W"]

    base = _shell_leaf(+1, leaf_outer, leaf_depth, leaf_w, h_int, SHELL_WALL)
    lid = _shell_leaf(-1, leaf_outer, leaf_depth, leaf_w, h_int, SHELL_WALL)
    base = _shell_magnets(base, +1, leaf_outer, leaf_depth, leaf_w, h_total, SHELL_WALL)
    lid = _shell_magnets(lid, -1, leaf_outer, leaf_depth, leaf_w, h_total, SHELL_WALL)

    cs, ps = _split_hinge_by_side(make_hinge(params))
    cs = cs.translate((0, 0, case_h))
    ps = ps.translate((0, 0, case_h))
    base = base + cs
    lid = lid + ps

    geom = dict(leaf_outer=leaf_outer, leaf_depth=leaf_depth, leaf_w=leaf_w,
                h_int=h_int, h_total=h_total, case_h=case_h, cavity_z=cavity_z)
    return base, lid, geom


def build_all(foam_t: float = FOAM_T):
    """Return (shell_print, insert, assembly) compounds."""
    base, lid, g = build_shell(foam_t)
    insert = build_insert()

    # Drop the insert into the base interior, sitting on a foam_t-thick base
    # layer (the bottom of the sandwich), for the fit-visualisation assembly.
    base_int_xc = g["leaf_outer"] + SHELL_WALL + (g["leaf_depth"] - 2 * SHELL_WALL) / 2.0
    placed = copy.copy(insert).translate(
        (base_int_xc - INSERT_DEPTH / 2.0, 0, SHELL_WALL + foam_t))

    shell_print = Compound(children=[base, lid])
    assembly = Compound(children=[copy.copy(base), copy.copy(lid), placed])
    return shell_print, insert, assembly, g


def main():
    parser = argparse.ArgumentParser(description="Option B: thin clamshell + slide-in insert")
    parser.add_argument("--format", choices=["step", "stl", "both"], default="both")
    parser.add_argument("--foam", type=float, default=FOAM_T,
                        help="foam thickness above and below the insert (mm)")
    args = parser.parse_args()

    print(f"Building tuner case v2 (shell + insert, foam={args.foam} mm)...")
    shell_print, insert, assembly, g = build_all(args.foam)
    print(f"  shell leaf: {g['leaf_depth']:.1f} x {g['leaf_w']:.1f} mm, "
          f"outer h {g['h_total']:.1f} mm; closed cavity {g['cavity_z']:.1f} mm")

    targets = {
        "tuner_case_v2_shell_print": shell_print,
        "tuner_case_v2_insert": insert,
    }
    for stem, shape in targets.items():
        if args.format in ("step", "both"):
            export_step(shape, str(OUT / f"{stem}.step"))
            print(f"Exported: {OUT / (stem + '.step')}")
        if args.format in ("stl", "both"):
            export_stl(shape, str(OUT / f"{stem}.stl"))
            print(f"Exported: {OUT / (stem + '.stl')}")

    # Assembly is for visualisation only -> STEP.
    export_step(assembly, str(OUT / "tuner_case_v2_assembly.step"))
    print(f"Exported: {OUT / 'tuner_case_v2_assembly.step'}")


if __name__ == "__main__":
    main()
