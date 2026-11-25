# Beam Designer — desktop edition

## Purpose and platform
A classroom tool for single-span beam statics, elastic deflection and simplified bending/stiffness checks. Python 3, Tkinter, NumPy and Matplotlib; no network needed. Based on the BYU CCE 270 [Beam Designer polished spec](https://byu-cce270.readthedocs.io/en/latest/unit3/05_ai_web_apps/web_class/#beam-designer). The supplied web files describe a different project and are archived in reference/ rather than used as a behavioral specification.

## Inputs
- Simply supported or left-fixed cantilever; span 4–40 ft, synchronized slider and number entry.
- Editable downward-positive point loads (kip, ft) and uniform loads (kip/ft, start/end ft), add/remove buttons. Point defaults to midspan or cantilever tip; uniform defaults to full span. Drag point arrows in 0.25-ft increments. Positions beyond the current span are clipped; reversed or empty uniform intervals are rejected. Signed magnitudes allow upward loads.
- Steel (E=29,000 ksi, Fb=30 ksi) and Douglas Fir-Larch No. 2 (E=1,600 ksi, Fb=0.900 ksi), classroom section properties:

| Steel | I (in^4) | S (in^3) | lb/ft |
|---|---:|---:|---:|
| W8x10 |30.8|7.81|10|
| W10x12 |53.8|10.9|12|
| W12x26 |204|33.4|26|
| W14x22 |199|29.0|22|
| W16x26 |301|38.4|26|
| W18x35 |510|57.6|35|
| W21x44 |843|81.6|44|
| W24x55 |1350|114|55|

| Lumber | I (in^4) | S (in^3) |
|---|---:|---:|
| 2x8 |47.63|13.14|
| 2x10 |98.93|21.39|
| 2x12 |177.98|31.64|

- Deflection limit L/360 (default) or L/240. No self-weight.

## Calculations and outputs
Use statics for reactions; positive shear and sagging moment, positive deflection upward. Integrate piecewise moment twice with E and I, converting ft to inches, and enforce the support boundary conditions. Include every load boundary and both shear limits at concentrated loads, sample at 0.1 ft or finer, and find interior moment/deflection extrema from polynomial roots. Display reaction values, beam/load drawing and aligned filled V, M and deflection diagrams with peak magnitude labels. Hover to read all three values; at a shear jump the cursor reports the right-hand value. Bending demand = 12 max(abs(M))/S in ksi. Deflection demand = max(abs(y)) in inches. Compare with Fb and 12L/limit respectively. Show actual/allowable and colored utilization (green <70%, amber 70–100%, red >100%) plus PASS/FAIL. Recommend the lowest-weight passing steel section (tie: larger I), or first passing lumber size; button applies it. Live refresh after inputs change; invalid entries clear results and disable exports. Default is simply supported W12x26, 20 ft, full-span 1 kip/ft. Light desktop layout with inputs on left and plots/checks on right.

## Validation
Published reference cases (reported to stated precision):
1. Simply supported, 20 ft, W12x26, 1 kip/ft full span: RA=RB=10 kip, max |V|=10 kip, max |M|=50.0 kip-ft at 10 ft, bending=17.96 ksi, max |y|=0.609 in at 10 ft, limit=0.667 in, both pass.
2. Simply supported, 20 ft, W12x26, 10 kip at 5 ft: RA=7.5, RB=2.5 kip; max |M|=37.5 kip-ft at 5 ft; bending=13.47 ksi; published deflection=0.340 in at 8.82 ft (verify independently).
3. Cantilever, 10 ft, W12x26, 5 kip at tip: RA=5 kip, external fixed moment=50 kip-ft; max |y|=0.487 in at tip; limit=0.333 in; deflection fails.
4. Simply supported, 12 ft, 2x10, 0.05 kip/ft full span: max |M|=0.90 kip-ft, bending=0.505 ksi, max |y|=0.147 in; both pass.

## Out of scope
Self-weight, shear stress, lateral-torsional buckling, load combinations and continuous beams. Not a substitute for engineering design review.

## Desktop features
- File > Save / Open: versioned JSON (.beam.json) preserves all input values and load definitions. Validate before replacing current design; report file errors without crashing.
- Export CSV: write x (ft), V (kip), M (kip-ft), and deflection (in) using the current plotted results, including two rows at discontinuities to preserve shear jumps. Use standard CSV readable in Excel.
- Calculation sheet: export a letter-size PDF listing beam inputs, section properties, loads, reactions, diagrams, peak values and checks. Paginate the load list if needed. Include the sign convention and classroom-only scope.
