#!/usr/bin/env python3
"""Marking template for the 5-gang Gibson tuner frame.

A drill/scribe template for transferring the frame's hole pattern and outline
onto a guitar headstock. It is the *outer shell* of the frame only: the top
(mounting) plate plus the outer housing side walls — with the inner cavity and
the bottom wall removed. Press it onto the headstock and mark through the holes.

The frame geometry is the single source of truth in the sibling `gib-tuners-mk2`
repository; this script imports `create_frame()` from it so the template can
never drift from the real frame.  Set GIB_TUNERS_MK2 to override the location.

Usage:
    python marking_template.py                 # right hand, c13-10 gear
    python marking_template.py --hand left
    python marking_template.py --gear bh11-cd-fx --format both
"""

import argparse
import os
import sys
from dataclasses import replace
from pathlib import Path

OUT = Path(__file__).parent

# --- Locate the sibling gib-tuners-mk2 repo (single source of truth) ---
_mk2 = Path(os.environ.get("GIB_TUNERS_MK2", OUT.parent / "gib-tuners-mk2"))
_mk2_src = _mk2 / "src"
if not (_mk2_src / "gib_tuners").is_dir():
    sys.exit(
        f"Cannot find gib-tuners-mk2 at {_mk2}.\n"
        "Clone it next to this repo, or set GIB_TUNERS_MK2 to its path."
    )
sys.path.insert(0, str(_mk2_src))

from build123d import Align, Axis, Box, Cylinder, Location, Part, export_step, export_stl  # noqa: E402

from gib_tuners.components.frame import create_frame  # noqa: E402
from gib_tuners.config.defaults import (  # noqa: E402
    calculate_worm_z,
    create_default_config,
    resolve_gear_config,
)
from gib_tuners.config.parameters import Hand  # noqa: E402


def build_marking_template(config, plate_thickness: float, wall_thickness: float) -> Part:
    """Top plate + the peg-entry side flange. Only the mounting holes are kept:
    the string-post holes (top plate) and the peg-entry holes (wall) are plugged.
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

    # Thicken the top plate upward (bottom face stays the datum), then re-drill
    # the mounting holes through the full new thickness so they stay open.
    if plate_thickness > wall:
        buildup = Box(
            box_outer, total_length, plate_thickness - wall,
            align=(Align.CENTER, Align.MIN, Align.MIN),
        )
        frame = frame + buildup.locate(Location((0, 0, 0)))

        mount_r = config.with_tolerance(fp.mounting_hole) * scale / 2
        for y_pos in (p * scale for p in fp.mounting_hole_positions):
            drill = Cylinder(
                mount_r, plate_thickness + 0.4,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            drill = drill.locate(Location((0, y_pos, -wall - 0.2)))
            frame = frame - drill

    return frame


def main():
    parser = argparse.ArgumentParser(
        description="Marking template (outer shell) for the tuner frame",
    )
    parser.add_argument("--gear", default="c13-10", help="Gear config name (default: c13-10)")
    parser.add_argument("--hand", choices=["right", "left"], default="right")
    parser.add_argument("--format", choices=["step", "stl", "both"], default="step")
    parser.add_argument(
        "--plate-thickness", type=float, default=2.0,
        help="Top plate thickness in mm, built up from the frame's 1.1mm (default: 2.0)",
    )
    parser.add_argument(
        "--wall-thickness", type=float, default=2.0,
        help="Side flange thickness in mm, built outward from the frame's 1.1mm (default: 2.0)",
    )
    args = parser.parse_args()

    gear_paths = resolve_gear_config(args.gear)
    config = create_default_config(
        scale=1.0,
        tolerance="production",
        hand=Hand.RIGHT if args.hand == "right" else Hand.LEFT,
        gear_json_path=gear_paths.json_path,
        config_dir=gear_paths.config_dir,
    )
    # Decorative engraving has no marking purpose and only weakens the part.
    config = replace(
        config,
        frame=replace(config.frame, engraving=replace(config.frame.engraving, enabled=False)),
    )

    print(
        f"Building marking template ({args.hand} hand, gear {args.gear}, "
        f"plate {args.plate_thickness}mm, flange {args.wall_thickness}mm)..."
    )
    template = build_marking_template(config, args.plate_thickness, args.wall_thickness)

    base = OUT / f"marking_template_{args.hand}"
    if args.format in ("step", "both"):
        export_step(template, str(base.with_suffix(".step")))
        print(f"Exported: {base.with_suffix('.step')}")
    if args.format in ("stl", "both"):
        export_stl(template, str(base.with_suffix(".stl")))
        print(f"Exported: {base.with_suffix('.stl')}")


if __name__ == "__main__":
    main()
