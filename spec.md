# Gibson Peg Turner — Engineering Specification

## 1. Overview

A 3D-printed T-handle string winder for Gibson-style guitar tuning pegs. Designed to protect decorative peg heads during string changes using a compliant TPU insert.

### Design Goals
- Protect vintage/decorative peg heads from scratches and damage
- Fast, comfortable string winding via offset T-handle crank
- Simple 3-piece assembly from two materials (PETG-CF + TPU)
- No supports required for any print

### Assembly
Three printed parts plus hardware:

| # | Part | Material | Function |
|---|------|----------|----------|
| A | Socket body | PETG-CF | Structural frame: holds TPU insert, integrates T-handle arm with bushing pocket |
| B | TPU insert | TPU 95A | Drops into socket body (exact fit); slot engages peg head with cushioned grip |
| C | Handle knob | PETG-CF | Palm grip with integral bushing post; sits on arm, spins freely |

Hardware: 1× M3×8 pan head bolt, 1× M3 fender washer (9mm OD), 1× M3 heat-set insert (knob retention from arm underside).

---

## 2. Peg Head Interface (Reference Dimensions)

These dimensions define the peg head geometry the tool must interface with. Source: `gib-tuners-mk2/src/gib_tuners/config/parameters.py` (`PegHeadParams`).

### Peg Head Profile (head-first, in engagement order)

```
        ┌─────────┐
        │   Pip   │  2.1mm dia × 1.4mm tall (1.2 + 0.2 stalk)
   ┌────┴─────────┴────┐
   │       Ring         │  12.5mm OD, 9.8mm bore, 2.4mm width at edge
   │    ┌─────────┐    │
   │    │  Bore   │    │  0.25mm offset from ring center
   │    └─────────┘    │
   └────┬─────────┬────┘
        │  Join   │       3.5mm dia × 3.0mm long (through bore)
        ├─────────┤
    ┌───┴─────────┴───┐
    │      Cap        │   8.5mm dia × 1.0mm tall (flange against frame)
    └───┬─────────┬───┘
        │Shoulder │       7.0mm dia (fits inside frame worm entry hole)
        │         │
```

### Reference Dimension Table

| Feature | Dimension | Value |
|---------|-----------|-------|
| Ring | Outer diameter | 12.5mm |
| Ring | Inner bore | 9.8mm |
| Ring | Width at outer edge | 2.4mm |
| Ring | Bore center offset | 0.25mm |
| Ring | Edge chamfer | 0.3mm |
| Pip | Diameter | 2.1mm |
| Pip | Length (body) | 1.2mm |
| Pip | Stalk diameter | 1.0mm |
| Pip | Stalk length | 0.2mm |
| Pip | Total protrusion | 1.4mm |
| Join | Diameter | 3.5mm |
| Join | Length | 3.0mm |
| Cap | Diameter | 8.5mm |
| Cap | Height | 1.0mm |
| Shoulder | Diameter | 7.0mm |

### Engagement Depth

The TPU slot engages the full peg head from the ring down past the cap and onto the shoulder. Total engagement stack:

| Zone | Depth | Cumulative |
|------|-------|------------|
| Ring (width at edge) | 2.4mm | 2.4mm |
| Join section | 3.0mm | 5.4mm |
| Cap | 1.0mm | 6.4mm |
| Shoulder (partial) | 10.6mm | 17.0mm |

The 17mm slot depth provides full engagement for positive drive and alignment.

---

## 3. Component A — Socket Body (PETG-CF)

### Overall Shape
**Stadium-shaped** socket body with an integrated T-handle arm. The socket axis is vertical (peg engagement direction). The cross-section is a stadium (rectangle with semicircular ends). The long axis of the stadium aligns with the arm direction, so the arm flows naturally out of one end of the stadium. The arm connects at the **top** of the socket.

### Stadium Cross-Section Derivation

Both the socket body and TPU insert share a stadium cross-section. Dimensions are derived from the peg slot geometry outward:

| Layer | Short axis | Long axis | Derivation |
|-------|-----------|-----------|------------|
| Peg slot (void) | 4.0mm | 15.0mm | Slot width × slot length |
| TPU insert (outer) | 4.0 + 2×3.0 = **10.0mm** | 15.0 + 2×3.0 = **21.0mm** | Slot + 2× TPU wall (3.0mm) |
| Socket pocket (inner) | **10.0mm** | **21.0mm** | Exact fit — no interference (TPU drops in) |
| Socket body (outer) | 10.0 + 2×2.65 = **15.3mm** | 21.0 + 2×2.65 = **26.3mm** | Pocket + 2× socket wall (2.65mm) |

The stadium shape is a rectangle of (long − short) length with semicircular caps of radius = short/2:
- **Socket outer**: 15.3mm wide, semicircle radius 7.65mm, straight section 11.0mm (26.3 − 15.3)
- **Pocket/TPU insert**: 10.0mm wide, semicircle radius 5.0mm, straight section 11.0mm (21.0 − 10.0)

### TPU Insert Pocket
| Parameter | Value | Notes |
|-----------|-------|-------|
| Pocket shape | Stadium bore | Matches TPU insert exactly |
| Pocket short axis | 10.0mm | Exact fit to TPU insert (no interference) |
| Pocket long axis | 21.0mm | Exact fit to TPU insert (no interference) |
| Pocket depth | 20.0mm | TPU insert length (17mm slot + 3mm base) |
| Entry chamfer | 0.5mm × 45° | Eases TPU insertion |

### Socket Body Envelope
| Parameter | Value | Derivation |
|-----------|-------|------------|
| Socket short axis (OD) | 15.3mm | Pocket (10.0mm) + 2 × 2.65mm wall |
| Socket long axis (OD) | 26.3mm | Pocket (21.0mm) + 2 × 2.65mm wall |
| Socket height | 25.0mm | Pocket depth (20mm) + 5mm top cap |
| Wall thickness | 2.65mm | Minimum for PETG-CF structural integrity |

### T-Handle Arm
The arm extends from the **top** of the socket, flowing out of one end of the stadium's long axis. The arm blends smoothly into the socket body wall (tangent junction with fillet).

| Parameter | Value | Notes |
|-----------|-------|-------|
| Arm length | 35.0mm | Center of socket to center of knob bushing |
| Arm cross-section | 12mm × 8mm | Rectangular, rounded edges (2mm radius). 12mm wide (horizontal), 8mm tall (vertical). |
| Arm height | 8.0mm | Through-bore design — no floor needed |
| Junction | Blend/tangent | Arm blends into the semicircular end of the stadium |
| Junction fillet | 5.0mm | Stress relief at arm-to-socket junction |

### Bushing Bore (in arm, at arm end)
The arm has a **through-bore** at its far end. The knob's integral bushing post passes through the full 8mm arm height and protrudes 0.3mm below the arm underside for washer clearance. A fender washer and bolt from below bear on the post tip, retaining the knob axially without clamping the arm.

| Parameter | Value | Notes |
|-----------|-------|-------|
| Bore diameter | 8.4mm | POST_OD (8.0mm) + 0.4mm clearance |
| Bore type | Through-bore | Full 8.0mm arm height — no floor |
| Post protrusion below arm | 0.3mm | Washer + bolt bear on post tip, not on arm face |
| Bolt clearance | n/a | Bolt threads directly into heat-set insert in post tip |

---

## 4. Component B — TPU Insert

### Overall Shape
**Stadium-shaped** plug with an open-ended slot cut into one end. The slot runs along the long axis of the stadium. The slot engages the peg head; the stadium body drops into the socket body pocket (exact fit, no interference).

### Primary Dimensions
| Parameter | Value | Notes |
|-----------|-------|-------|
| Slot length | 15.0mm | Spans peg ring (12.5mm) + 2.5mm entry clearance |
| Slot width | 4.0mm | Grips 2.4mm ring with TPU compression (~0.8mm/side) |
| Slot depth | 17.0mm | Full peg head engagement (ring → cap → shoulder) |
| Entry chamfer | 1.0mm × 45° | Both slot edges, eases peg insertion |

### Insert Envelope
| Parameter | Value | Derivation |
|-----------|-------|------------|
| Insert short axis | 10.0mm | Slot width (4mm) + 2 × 3mm wall |
| Insert long axis | 21.0mm | Slot length (15mm) + 2 × 3mm wall |
| Insert length (height) | 20.0mm | Slot depth (17mm) + 3mm solid base |
| Wall around slot (sides) | 3.0mm | Minimum for TPU grip strength |
| Wall around slot (ends) | 3.0mm | (21mm − 15mm) / 2 |
| Base thickness | 3.0mm | Solid base below slot bottom |

### Pip Accommodation
The pip (2.1mm dia, 1.4mm total protrusion) sits on the ring edge. The slot width of 4.0mm vs ring width of 2.4mm provides 0.8mm clearance per side. The TPU (95A) flexes to accommodate the pip protrusion without requiring a specific relief cutout.

---

## 5. Component C — Handle Knob (PETG-CF)

### Overall Shape
Barrel-shaped palm knob with an **integral bushing post** that passes through the arm's through-bore. The knob sits above the arm via a flange (wider than the bore), and is retained axially by an M3 fender washer and bolt bearing on the protruding post tip from below. The knob, post, bolt, and washer all rotate together as a unit inside the fixed arm bore.

### Barrel Dimensions
| Parameter | Value | Notes |
|-----------|-------|-------|
| Knob OD | 20.0mm | Comfortable palm grip |
| Knob height | 30.0mm | Full palm wrap |
| Edge radius | 3.0mm | Rounded top and bottom edges for comfort |

### Integral Bushing Post
| Parameter | Value | Notes |
|-----------|-------|-------|
| Post OD | 8.0mm | Bearing surface, rotates inside arm bore (8.4mm) |
| Post height | 8.3mm | ARM_HEIGHT (8.0mm) + 0.3mm protrusion below arm |
| Flange diameter | 10.0mm | Wider than 8.4mm bore — bears on arm top, axial retention |
| Flange height | 2.0mm | Ring between barrel and post |

### Axial Retention
The knob is captured between two features wider than the 8.4mm bore:
- **Top**: integral flange (10mm OD) bears on the arm top face
- **Bottom**: M3 fender washer (9mm OD) bears on the post tip (0.3mm protrusion)

The bolt pulls the washer up against the post tip. No clamping load passes through the arm — the arm is a free bearing surface only.

### Heat-set Insert (in post tip)
| Parameter | Value | Notes |
|-----------|-------|-------|
| Heat-set pocket diameter | 4.0mm | Standard M3 brass insert |
| Heat-set pocket depth | 4.5mm | Full insert engagement |
| Location | Post tip (bottom face) | M3×8 bolt from below threads into this |

---

## 6. Assembly & Interfaces

### Assembly Sequence
1. Drop TPU insert into socket body pocket (exact fit, no interference)
2. Insert knob post down through arm through-bore from above (clearance fit)
3. Place M3 fender washer (9mm OD) on post tip below the arm
4. Thread M3×8 bolt up through washer into heat-set insert in post tip — snug, not overtorqued

The knob's flange (10mm OD) rests on the arm top, preventing the knob from pulling down through the bore. The washer + bolt bear on the post tip (0.3mm protrusion) from below, preventing the knob from lifting out. No clamping force acts on the arm.

### Interface Tolerances

| Interface | Type | Clearance/Interference |
|-----------|------|----------------------|
| TPU insert → Socket pocket | Exact fit | 0mm — TPU insert matches pocket exactly |
| Knob post → Arm bore | Running fit (clearance) | 0.4mm clearance on diameter |
| Fender washer → Post tip | Bearing contact | Washer OD (9mm) > bore (8.4mm); bears on post tip only |
| M3 bolt → Heat-set insert | Thread engagement | Standard M3 heat-set (4.5mm deep, ~4.0mm pocket dia) |

### Bill of Materials

| Item | Qty | Specification |
|------|-----|---------------|
| M3 × 8mm pan head bolt | 1 | Stainless steel (shorter — no arm floor to pass through) |
| M3 fender washer | 1 | OD 9mm (must exceed 8.4mm bore) |
| M3 × 4mm heat-set insert | 1 | Standard brass, knurled |

---

## 7. Materials & Print Parameters

### Socket Body (PETG-CF)
| Parameter | Value |
|-----------|-------|
| Material | PETG-CF (carbon fiber filled) |
| Nozzle | 0.4mm (hardened steel) |
| Layer height | 0.2mm |
| Perimeters | 4 |
| Infill | 50% gyroid (arm), 100% (bushing pocket area) |
| Notes | High infill near bushing pocket for bearing durability |

### TPU Insert
| Parameter | Value |
|-----------|-------|
| Material | TPU 95A shore hardness |
| Nozzle | 0.4mm |
| Layer height | 0.2mm |
| Perimeters | 4 |
| Infill | 100% |
| Print speed | 25mm/s max |
| Notes | 100% infill for maximum grip strength and durability |

### Handle Knob (PETG-CF)
| Parameter | Value |
|-----------|-------|
| Material | PETG-CF |
| Nozzle | 0.4mm (hardened steel) |
| Layer height | 0.2mm |
| Perimeters | 3 |
| Infill | 20% gyroid |
| Notes | Non-structural, light infill sufficient |

---

## 8. Print Orientation

All parts must print **without supports**.

### Socket Body
Print with the socket bore facing **up** (arm flat on the bed, 8mm tall face down). The arm lies flat, providing a stable base. The stadium-shaped socket rises vertically from the arm. No supports needed — the pocket bore is open at the top, the bushing bore is a simple through-hole in the arm (easily bridged or printed as a clean bore with no overhang concern at 8.4mm), and the stadium shape has no overhangs.

### TPU Insert
Print **upright** with the slot opening facing **up**. The stadium outer wall needs no supports. The slot is open-ended, so internal supports are not needed.

### Handle Knob
Print **barrel-down** (flat bottom on bed), bushing post pointing **up**. The barrel is a simple cylinder with fillets. The flange (10mm) is narrower than the barrel (20mm), so it prints fine. The post (8mm OD, 8.3mm tall) is narrower than the flange (10mm) — only 1mm overhang per side, printable without supports. The heat-set pocket in the post tip faces up during printing.

---

## 9. Output & Tooling

### Implementation
Single Python file (`peg_turner.py`) using **build123d** to generate all three components.

### Output Format
- Individual **STEP** files for each component (for slicing/printing)
- Combined **STEP** assembly file (for visualization in VSCode OCP CAD Viewer)

### File Outputs
| File | Contents |
|------|----------|
| `socket_body.step` | Component A — Socket body (PETG-CF) |
| `tpu_insert.step` | Component B — TPU insert |
| `handle_knob.step` | Component C — Handle knob (PETG-CF) |
| `assembly.step` | All three components in assembled position |

---

## 10. Verification Checklist

### Fit & Function
- [ ] TPU slot slides over peg head without excessive force
- [ ] TPU slot grips peg ring firmly (tool doesn't fall off when inverted)
- [ ] TPU insert drops into socket body and stays put under cranking torque
- [ ] Knob post spins freely in arm through-bore (no binding)
- [ ] Knob, post, bolt, and washer all rotate together as a unit (no relative slip)
- [ ] M3 fender washer (9mm OD) bears on post tip, not on arm underside
- [ ] M3×8 bolt + heat-set insert retains knob securely — no axial play
- [ ] Flange (10mm OD) sits on arm top, preventing knob from pulling through bore
- [ ] T-handle arm does not flex noticeably under normal cranking force
- [ ] Pip does not tear or permanently deform the TPU slot

### Dimensional Checks
- [ ] TPU slot width accommodates ring (2.4mm) + pip (2.1mm protrusion) via flex
- [ ] TPU slot length clears ring OD (12.5mm) for easy entry
- [ ] Engagement depth (17mm) provides stable, wobble-free drive
- [ ] Knob post clearance (0.4mm on dia) allows free rotation without excessive play
- [ ] Post protrusion below arm (0.3mm) provides clearance for washer without excess slop
- [ ] Fender washer OD (9mm) confirmed larger than bore (8.4mm) — cannot pull through
- [ ] Flange OD (10mm) confirmed larger than bore (8.4mm) — cannot pull through
- [ ] Socket body wall thickness adequate (no cracking under torque)
- [ ] Arm height (8.0mm) adequate bearing length for post rotation

### Usability
- [ ] Comfortable single-hand operation
- [ ] Peg head shows no marks or damage after 100+ winding cycles
- [ ] Tool fits in a guitar case accessory pocket
