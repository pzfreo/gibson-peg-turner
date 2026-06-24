"""tuner_jig.py -- assembly jig: hold a 5-gang tuner strip peg-heads DOWN.

Holds the assembled gang frame steady with the peg-heads (worm + turn-ring)
pointing down into shaped pockets and the worm axis vertical, so you can screw
the peg/worm bolt straight down from the top. The frame body bridges the pockets
and rests on the supports (lands) between them.

ALL geometry is measured from the real assembled gangs (assembly_5gang_rh/lh),
rotated so the peg-heads face down (worm axis vertical):

  * 5 peg-heads on a 145 mm strip at Y = PEG_YC, pitch ~27.2 mm.
  * Each peg-head is a thin turn-ring (X~12.4 x Y~3 mm) with a round POST
    SURROUND (~8.5 mm) at its top end, just below where the frame connects
    (REST_Z). The pocket Y is sized to clear that 8.5 mm surround.
  * RH peg-heads sit at Xc=-5, LH at Xc=+5 (mirror images). The default
    'both' jig centres a wider pocket on X=0 so EITHER gang drops in -- the
    assembled gang is one rigid geared piece held by all five pockets + the
    frame resting on the supports, so the extra X width doesn't loosen the hold.
    --hand rh|lh gives a snug single-hand pocket instead.
  * String posts sit ~5 mm higher pointing sideways, clear of the block.

Output: tuner_jig.step / .stl
"""
import argparse
from pathlib import Path

from build123d import (
    Align,
    Box,
    Part,
    RectangleRounded,
    export_step,
    export_stl,
    extrude,
)

OUT = Path(__file__).resolve().parent

# --- Measured peg-head geometry (rings-down pose; mm) ----------------------
PEG_YC = (21.2, 48.4, 75.6, 102.8, 130.0)   # peg-head centres along the strip (Y)
RING_XW = 12.4            # turn-ring length in X (the wide, thin blade)
RING_XC = 5.0             # ring centre offset: RH at -RING_XC, LH at +RING_XC
SURROUND_W = 8.5          # round post-surround Ø at the peg-head top end (sets pocket Y)
REST_Z = 18.0             # frame connects here -> pocket depth / rest-plane height
GANG_Y = (0.0, 145.0)     # strip extent along Y

# --- Jig parameters --------------------------------------------------------
POCKET_CLR = 0.6          # clearance added all round each peg-head pocket
TIP_GAP = 1.0             # gap under the peg-head tip so the FRAME rests on the
#                           supports (not the peg bottoming in the pocket)
FLOOR = 3.0               # solid floor under the pockets
Y_MARGIN = 8.0            # block overhang past the strip ends (Y)
BLOCK_HALF_X = 16.0       # half block width in X (symmetric; covers every pocket
#                           + the frame rest for either hand)


def _pocket_x(hand: str):
    """Return (centre_x, width_x) of the peg-head pocket for the given hand."""
    if hand == "rh":
        return (-RING_XC, RING_XW)
    if hand == "lh":
        return (+RING_XC, RING_XW)
    # 'both': span the union of the RH and LH ring positions, centred on 0
    return (0.0, 2 * RING_XC + RING_XW)        # = 22.4 mm


def build_jig(hand: str = "both") -> Part:
    """One jig block with five peg-head pockets and the supports between them."""
    y0 = GANG_Y[0] - Y_MARGIN
    y1 = GANG_Y[1] + Y_MARGIN
    block = Box(2 * BLOCK_HALF_X, y1 - y0, REST_Z + FLOOR,
                align=(Align.MIN, Align.MIN, Align.MIN)).translate((-BLOCK_HALF_X, y0, -FLOOR))

    xc, xw = _pocket_x(hand)
    px = xw + 2 * POCKET_CLR
    py = SURROUND_W + 2 * POCKET_CLR           # clears the 8.5 mm post surround
    depth = REST_Z + TIP_GAP                    # from REST_Z down to z = -TIP_GAP
    for yc in PEG_YC:
        sk = RectangleRounded(px, py, radius=min(px, py) / 2 - 0.01)
        cutter = extrude(sk, amount=depth).translate((xc, yc, -TIP_GAP))
        block = block - cutter
    return block


def main():
    parser = argparse.ArgumentParser(description="Peg-heads-down assembly jig for one tuner gang")
    parser.add_argument("--format", choices=["step", "stl", "both"], default="both")
    parser.add_argument("--hand", choices=["both", "rh", "lh"], default="both",
                        help="'both' = symmetric pocket for either gang; rh/lh = snug single-hand")
    args = parser.parse_args()

    print(f"Building tuner assembly jig (hand={args.hand}, peg-heads down)...")
    jig = build_jig(args.hand)
    bb = jig.bounding_box()
    xc, xw = _pocket_x(args.hand)
    print(f"  block: {bb.size.X:.1f} x {bb.size.Y:.1f} x {bb.size.Z:.1f} mm; "
          f"5 pockets {xw + 2*POCKET_CLR:.1f}(X) x {SURROUND_W + 2*POCKET_CLR:.1f}(Y) mm, "
          f"{REST_Z:.0f} mm deep")

    suffix = "" if args.hand == "both" else f"_{args.hand}"
    stem = OUT / f"tuner_jig{suffix}"
    if args.format in ("step", "both"):
        export_step(jig, str(stem.with_suffix(".step")))
        print(f"Exported: {stem.with_suffix('.step')}")
    if args.format in ("stl", "both"):
        export_stl(jig, str(stem.with_suffix(".stl")))
        print(f"Exported: {stem.with_suffix('.stl')}")


if __name__ == "__main__":
    main()
