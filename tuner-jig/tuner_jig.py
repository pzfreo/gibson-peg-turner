"""tuner_jig.py -- assembly jig: hold a 5-gang tuner strip peg-heads DOWN.

Holds the assembled gang frame steady with the peg-heads (worm + turn-ring)
pointing down into snug shaped pockets and the worm axis vertical, so you can
screw the peg/worm bolt straight down from the top. The frame body bridges the
pockets and rests on the supports (lands) between them.

ONE PRINT, BOTH HANDS (snug). The peg-heads of the RH and LH gangs are mirror
images that overlap across the centreline, so a single pocket cannot be snug to
both at once. Instead the pockets are cut SNUG for one hand (Xc=-RING_XC), and
because the peg pattern is mirror-symmetric about its own centre (PEG_CENTER),
ROTATING THE WHOLE JIG 180 deg flat on the bench moves the pockets to +RING_XC --
exactly the other gang's peg-heads. So the same snug jig holds either gang; just
spin it end-for-end. The block is symmetric about (X=0, Y=PEG_CENTER) so the flip
lands on itself.

ALL geometry measured from the real assembled gangs (rings-down pose):
  * 5 peg-heads at Y = PEG_YC (pitch ~27.2 mm), turn-ring X~12.4 x Y~3 mm with a
    round ~8.5 mm post-surround at the top end (sets pocket Y).
  * Pocket cradles the ring in X and the surround in Y to ~POCKET_CLR.
  * Frame connects at REST_Z; pockets are that deep, frame rests on the supports.
  * String posts sit ~5 mm higher pointing sideways, clear of the block.

Output: tuner_jig.step / .stl   (--hand lh pre-flips the pockets if you prefer)
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
PEG_CENTER = sum(PEG_YC) / len(PEG_YC)       # 75.6 -- pattern is symmetric about this
RING_XW = 12.4            # turn-ring length in X (the wide, thin blade)
RING_XC = 5.0             # ring centre offset from the strip axis
SURROUND_W = 8.5          # round post-surround Ø at the peg-head top end (sets pocket Y)
REST_Z = 18.0             # frame connects here -> pocket depth / rest-plane height
GANG_Y = (0.0, 145.0)     # strip extent along Y

# --- Jig parameters --------------------------------------------------------
POCKET_CLR = 0.5          # snug clearance around the ring (X) and surround (Y)
TIP_GAP = 1.0             # gap under the peg-head tip so the FRAME rests on the supports
FLOOR = 3.0               # solid floor under the pockets
WALL = 3.0                # block wall past the pocket
Y_MARGIN = 8.0            # block overhang past the strip ends (Y)


def build_jig(hand: str = "rh") -> Part:
    """One block with five SNUG peg-head pockets on one side (flip for the other)."""
    xc = -RING_XC if hand == "rh" else RING_XC

    # Block symmetric about (X=0, Y=PEG_CENTER) so a 180 deg flip lands on itself.
    half_x = RING_XC + RING_XW / 2 + POCKET_CLR + WALL
    reach_y = max(PEG_CENTER - GANG_Y[0], GANG_Y[1] - PEG_CENTER) + Y_MARGIN
    block = Box(2 * half_x, 2 * reach_y, REST_Z + FLOOR,
                align=(Align.CENTER, Align.CENTER, Align.MIN)).translate(
                    (0, PEG_CENTER, -FLOOR))

    px = RING_XW + 2 * POCKET_CLR              # snug to the ring in X (~13.4)
    py = SURROUND_W + 2 * POCKET_CLR           # snug to the 8.5 surround in Y (~9.5)
    depth = REST_Z + TIP_GAP
    for yc in PEG_YC:
        sk = RectangleRounded(px, py, radius=min(px, py) / 2 - 0.01)
        cutter = extrude(sk, amount=depth).translate((xc, yc, -TIP_GAP))
        block = block - cutter
    return block


def main():
    parser = argparse.ArgumentParser(description="Peg-heads-down assembly jig (snug, flip for either gang)")
    parser.add_argument("--format", choices=["step", "stl", "both"], default="both")
    parser.add_argument("--hand", choices=["rh", "lh"], default="rh",
                        help="which side the snug pockets sit on (the SAME print holds the "
                             "other gang when rotated 180 deg flat)")
    args = parser.parse_args()

    print(f"Building tuner assembly jig (snug, pockets={args.hand}, peg-heads down)...")
    jig = build_jig(args.hand)
    bb = jig.bounding_box()
    print(f"  block: {bb.size.X:.1f} x {bb.size.Y:.1f} x {bb.size.Z:.1f} mm; "
          f"5 snug pockets {RING_XW + 2*POCKET_CLR:.1f}(X) x {SURROUND_W + 2*POCKET_CLR:.1f}(Y) mm, "
          f"{REST_Z:.0f} mm deep -- rotate 180 deg for the other gang")

    suffix = "" if args.hand == "rh" else "_lh"
    stem = OUT / f"tuner_jig{suffix}"
    if args.format in ("step", "both"):
        export_step(jig, str(stem.with_suffix(".step")))
        print(f"Exported: {stem.with_suffix('.step')}")
    if args.format in ("stl", "both"):
        export_stl(jig, str(stem.with_suffix(".stl")))
        print(f"Exported: {stem.with_suffix('.stl')}")


if __name__ == "__main__":
    main()
