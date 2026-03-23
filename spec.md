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
| A | Socket body | PETG-CF | Structural frame: holds TPU insert, integrates T-handle arm with bushing post |
| B | TPU insert | TPU 95A | Drops into socket body (exact fit); slot engages peg head with cushioned grip |
| C | Handle knob | PETG-CF | Palm grip at end of T-handle arm; spins freely on bushing post |

Hardware: 1× M3×12 pan head bolt, 1× M3 washer (knob retention).

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
| Arm cross-section | 12mm × 8mm | Rectangular, rounded edges (2mm radius). 12mm wide (horizontal), 8mm tall (vertical). Wide face flat on print bed. |
| Junction | Blend/tangent | Arm blends into the semicircular end of the stadium |
| Junction fillet | 5.0mm | Stress relief at arm-to-socket junction |

### Bushing Post (at arm end)
| Parameter | Value | Notes |
|-----------|-------|-------|
| Post OD | 8.0mm | Bearing surface for knob |
| Post bore | 3.4mm | M3 bolt clearance (3.0mm + 0.4mm) |
| Post height | 32.0mm | Knob height (30mm) + 2mm shoulder below |
| Shoulder height | 2.0mm | Prevents knob sliding down |

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
Barrel-shaped palm knob. Through-bore for bushing post. Retained by M3 bolt + washer from the top.

### Dimensions
| Parameter | Value | Notes |
|-----------|-------|-------|
| Knob OD | 20.0mm | Comfortable palm grip |
| Knob height | 30.0mm | Full palm wrap |
| Bore diameter | 8.4mm | Bushing post OD (8.0mm) + 0.4mm clearance |
| Edge radius | 3.0mm | Rounded top and bottom edges for comfort |
| Washer recess diameter | 6.5mm | Recesses M3 washer (5.5mm OD + clearance) |
| Washer recess depth | 1.0mm | Flush bolt head |

---

## 6. Assembly & Interfaces

### Assembly Sequence
1. Drop TPU insert into socket body pocket (exact fit, no interference)
2. Slide knob onto bushing post (clearance fit)
3. Insert M3×12 bolt through knob bore, through bushing post, thread into heat-set insert

The bushing post bore is a clearance hole. A brass M3 heat-set insert is installed in the base of the bushing post for bolt retention.

### Interface Tolerances

| Interface | Type | Clearance/Interference |
|-----------|------|----------------------|
| TPU insert → Socket pocket | Exact fit | 0mm — TPU insert matches pocket exactly |
| Knob bore → Bushing post | Running fit (clearance) | 0.4mm clearance on diameter |
| M3 bolt → Bushing bore | Clearance | 0.4mm clearance on diameter |
| M3 bolt → Heat-set insert | Thread engagement | Standard M3 heat-set (4mm deep, ~4.0mm pocket dia) |

### Bill of Materials

| Item | Qty | Specification |
|------|-----|---------------|
| M3 × 12mm pan head bolt | 1 | Stainless steel |
| M3 washer | 1 | OD ~5.5mm |
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
| Infill | 50% gyroid (arm), 100% (bushing post area) |
| Notes | High infill near bushing post for bearing durability |

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
Print with the socket bore facing **up** (arm flat on the bed, 12mm wide face down). The arm lies flat, providing a stable base. The stadium-shaped socket rises vertically from the arm. No supports needed — the pocket bore is open at the top, the arm junction has a generous fillet, and the stadium shape has no overhangs.

### TPU Insert
Print **upright** with the slot opening facing **up**. The stadium outer wall needs no supports. The slot is open-ended, so internal supports are not needed.

### Handle Knob
Print **upright** with the bore vertical. Simple revolved shape, no supports needed.

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
- [ ] Knob spins freely on bushing post (no binding)
- [ ] M3 bolt + heat-set insert retains knob securely
- [ ] T-handle arm does not flex noticeably under normal cranking force
- [ ] Pip does not tear or permanently deform the TPU slot

### Dimensional Checks
- [ ] TPU slot width accommodates ring (2.4mm) + pip (2.1mm protrusion) via flex
- [ ] TPU slot length clears ring OD (12.5mm) for easy entry
- [ ] Engagement depth (17mm) provides stable, wobble-free drive
- [ ] Knob bore clearance allows free rotation without excessive play
- [ ] Socket body wall thickness adequate (no cracking under torque)

### Usability
- [ ] Comfortable single-hand operation
- [ ] Peg head shows no marks or damage after 100+ winding cycles
- [ ] Tool fits in a guitar case accessory pocket
