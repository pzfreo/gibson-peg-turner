#!/usr/bin/env python3
"""Marking template for the 5-gang Gibson tuner frame.

A drill/scribe template for transferring the frame's mounting-hole pattern and
outline onto a guitar headstock. It is the *outer shell* of the frame only: the
top (mounting) plate plus the outer housing side walls — with the inner cavity
and the bottom wall removed. Press it onto the headstock and mark through the
small centre-marking holes.

Only the six mounting holes are marked, and they all lie on the centreline, so
the template is hand-agnostic: one part serves both left- and right-hand frames
(the blank flange wall is cosmetic/structural and has no holes). It is built
from the right-hand frame internally.

The frame geometry is the single source of truth in the `gib-tuners` package
(github.com/pzfreo/gib-tuners-mk2); this script imports `create_frame()` from it
so the template can never drift from the real frame.

Usage:
    python marking_template.py                 # c13-10 gear
    python marking_template.py --gear bh11-cd-fx --format both
"""

import argparse
import math
from dataclasses import replace
from pathlib import Path

from build123d import Align, Axis, Box, Cylinder, Location, Part, export_step, export_stl
from gib_tuners.components.frame import create_frame
from gib_tuners.config.defaults import (
    calculate_worm_z,
    create_default_config,
    resolve_gear_config,
)
from gib_tuners.config.parameters import Hand

OUT = Path(__file__).parent


def _add_flex_gaps(frame, config, plate_top: float, web: float):
    """Cut two 45 degree V-notches from the TOP face only into each of the 4 gaps
    between stations, forming a printable living hinge so the jig can flex to a
    curved headstock. With all notches on the top, the thin web sits at the
    bottom (contact) face, so that face keeps its length when bent and the marked
    hole spacing stays correct. Notches span the full width; printed upside-down
    (plate top on the bed) the <=45 degree walls need no supports.

    The two notches sit at the outer thirds of each gap, leaving the centre
    (where the marking hole is) un-notched: this keeps the hole clean and avoids
    a third nozzle-crossing per gap, which reduces stringing.
    """
    fp = config.frame
    scale = config.scale
    wall = fp.wall_thickness * scale
    box_outer = fp.box_outer * scale
    hl = fp.housing_length * scale
    hcs = [c * scale for c in fp.housing_centers]

    thickness = plate_top + wall          # plate thickness in the gaps
    depth = thickness - web               # cut depth that leaves `web` at apex
    margin = 0.5                          # keep notches off the housings

    def notch(y):
        diag = depth * math.sqrt(2)       # square side -> 45 deg V of this depth
        cut = Box(box_outer + 4, diag, diag).rotate(Axis.X, 45)
        return cut.locate(Location((0, y, plate_top)))

    for i in range(len(hcs) - 1):
        g0, g1 = hcs[i] + hl / 2 + margin, hcs[i + 1] - hl / 2 - margin
        width = g1 - g0
        if width < 1.0:
            continue
        for frac in (1 / 6, 5 / 6):       # outer thirds; centre stays clear
            frame = frame - notch(g0 + width * frac)
    return frame


def build_marking_template(
    config, plate_thickness: float, wall_thickness: float,
    flex: bool = True, web: float = 0.6, mark_dia: float = 1.5,
) -> Part:
    """Top plate + the peg-entry side flange. The string-post, peg-entry and the
    full-size mounting holes are all plugged; a small `mark_dia` centre-marking
    hole is drilled at each mounting position instead.
    The opposite bearing-side wall, bottom wall and inner cavity are gone.

    For print strength the plate is thickened upward and the side wall is built
    out inward into a continuous full-length flange (contact faces, hole axes and
    the outer profile are preserved). Pass the frame's native 1.1mm to skip.
    """
    frame = create_frame(config, label=True)

    fp = config.frame
    scale = config.scale
    box_outer = fp.box_outer * scale
    wall = fp.wall_thickness * scale
    total_length = fp.total_length * scale
    half = box_outer / 2
    right = config.hand == Hand.RIGHT

    # Remove everything below the top plate except the peg-entry wall.
    # Entry (large Ø7.2 hole) is on +X for RH, -X for LH (matches frame.py).
    if right:
        x_min, x_max = -half - 0.1, half - wall   # keep +X wall
    else:
        x_min, x_max = -half + wall, half + 0.1   # keep -X wall

    cut = Box(
        x_max - x_min, total_length + 2, box_outer,
        align=(Align.MIN, Align.MIN, Align.MAX),
    )
    cut = cut.locate(Location((x_min, -1, -wall)))  # top of cut at underside of top plate
    frame = frame - cut

    # Plug the string-post and peg-entry holes (keep only the mounting holes).
    # Radius is oversized 0.1mm so the plug overlaps surrounding solid for a
    # clean union; plug spans the wall thickness flush with both faces.
    housing_centers = [c * scale for c in fp.housing_centers]
    effective_cd = (config.gear.center_distance - config.gear.extra_backlash) * scale
    post_r = config.with_tolerance(fp.post_bearing_hole) * scale / 2 + 0.1
    worm_r = config.with_tolerance(fp.worm_entry_hole) * scale / 2 + 0.1
    worm_z = calculate_worm_z(config)
    wall_x = (half - wall / 2) if right else (-half + wall / 2)

    for hc in housing_centers:
        post_plug = Cylinder(post_r, wall, align=(Align.CENTER, Align.CENTER, Align.CENTER))
        post_plug = post_plug.locate(Location((0, hc - effective_cd / 2, -wall / 2)))
        frame = frame + post_plug

        worm_plug = Cylinder(worm_r, wall, align=(Align.CENTER, Align.CENTER, Align.CENTER))
        worm_plug = worm_plug.rotate(Axis.Y, 90)
        worm_plug = worm_plug.locate(Location((wall_x, hc + effective_cd / 2, worm_z)))
        frame = frame + worm_plug

    # Plug the full-size mounting holes; a small marking hole replaces them later.
    mount_plug_r = config.with_tolerance(fp.mounting_hole) * scale / 2 + 0.1
    for y_pos in (p * scale for p in fp.mounting_hole_positions):
        mplug = Cylinder(mount_plug_r, wall, align=(Align.CENTER, Align.CENTER, Align.CENTER))
        frame = frame + mplug.locate(Location((0, y_pos, -wall / 2)))

    plate_top_z = (-wall + plate_thickness) if plate_thickness > wall else 0.0

    # Build out the side wall, one thickened flange per housing (the gaps between
    # housings are the slots and must stay open). Each flange grows OUTWARD (inner
    # face fixed, so the inside cavity is unchanged) AND rises to the full
    # thickened-plate height, so the plate/flange corner is a solid block rather
    # than a thin 1.1mm overlap.
    if wall_thickness > wall:
        inner_x = half - wall  # inner face of the entry wall (cavity datum)
        hl = fp.housing_length * scale
        for hc in housing_centers:
            flange = Box(
                wall_thickness, hl, box_outer + plate_top_z,
                align=((Align.MIN if right else Align.MAX), Align.MIN, Align.MAX),
            )
            flange = flange.locate(
                Location((inner_x if right else -inner_x, hc - hl / 2, plate_top_z))
            )
            frame = frame + flange

    # Thicken the top plate upward (bottom face stays the datum).
    if plate_thickness > wall:
        buildup = Box(
            box_outer, total_length, plate_thickness - wall,
            align=(Align.CENTER, Align.MIN, Align.MIN),
        )
        frame = frame + buildup.locate(Location((0, 0, 0)))

    # Drill the small centre-marking holes through the full plate thickness.
    mark_r = mark_dia * scale / 2
    full_thickness = plate_top_z + wall
    for y_pos in (p * scale for p in fp.mounting_hole_positions):
        drill = Cylinder(
            mark_r, full_thickness + 0.4,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
        frame = frame - drill.locate(Location((0, y_pos, -wall - 0.2)))

    if flex:
        frame = _add_flex_gaps(frame, config, plate_top_z, web)

    return frame


def main():
    parser = argparse.ArgumentParser(
        description="Marking template (outer shell) for the tuner frame",
    )
    parser.add_argument("--gear", default="c13-10", help="Gear config name (default: c13-10)")
    parser.add_argument("--format", choices=["step", "stl", "both"], default="step")
    parser.add_argument(
        "--plate-thickness", type=float, default=2.0,
        help="Top plate thickness in mm, built up from the frame's 1.1mm (default: 2.0)",
    )
    parser.add_argument(
        "--wall-thickness", type=float, default=2.0,
        help="Side flange thickness in mm, built outward from the frame's 1.1mm (default: 2.0)",
    )
    parser.add_argument(
        "--no-flex", action="store_true",
        help="Disable the zigzag flex notches in the inter-station gaps",
    )
    parser.add_argument(
        "--web", type=float, default=0.6,
        help="Remaining web thickness at the flex-notch apex in mm (default: 0.6)",
    )
    parser.add_argument(
        "--mark-dia", type=float, default=1.5,
        help="Centre-marking hole diameter at each mounting position in mm (default: 1.5)",
    )
    args = parser.parse_args()

    gear_paths = resolve_gear_config(args.gear)
    # Hand-agnostic: only the centreline mounting holes are marked, so the
    # right-hand frame serves for both hands. Build from the right-hand frame.
    config = create_default_config(
        scale=1.0,
        tolerance="production",
        hand=Hand.RIGHT,
        gear_json_path=gear_paths.json_path,
        config_dir=gear_paths.config_dir,
    )
    # Decorative engraving has no marking purpose and only weakens the part.
    config = replace(
        config,
        frame=replace(config.frame, engraving=replace(config.frame.engraving, enabled=False)),
    )

    print(
        f"Building marking template (gear {args.gear}, "
        f"plate {args.plate_thickness}mm, flange {args.wall_thickness}mm)..."
    )
    template = build_marking_template(
        config, args.plate_thickness, args.wall_thickness,
        flex=not args.no_flex, web=args.web, mark_dia=args.mark_dia,
    )

    base = OUT / "marking_template"
    if args.format in ("step", "both"):
        export_step(template, str(base.with_suffix(".step")))
        print(f"Exported: {base.with_suffix('.step')}")
    if args.format in ("stl", "both"):
        export_stl(template, str(base.with_suffix(".stl")))
        print(f"Exported: {base.with_suffix('.stl')}")


if __name__ == "__main__":
    main()
