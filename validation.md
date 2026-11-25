| Case | Quantity | Expected | Actual | Status |
|---|---|---:|---:|---|
| 1 | ra | 10.0 | 10.0 | PASS |
| 1 | rb | 10.0 | 10.0 | PASS |
| 1 | shear | 10.0 | 10.0 | PASS |
| 1 | moment | 50.0 | 50.0 | PASS |
| 1 | moment_x | 10.0 | 10.0 | PASS |
| 1 | stress | 17.96 | 17.96 | PASS |
| 1 | deflection | 0.609 | 0.609 | PASS |
| 1 | deflection_x | 10.0 | 10.0 | PASS |
| 1 | allow_def | 0.667 | 0.667 | PASS |
| 1 | bending_pass | True | True | PASS |
| 1 | deflection_pass | True | True | PASS |
| 2 | ra | 7.5 | 7.5 | PASS |
| 2 | rb | 2.5 | 2.5 | PASS |
| 2 | moment | 37.5 | 37.5 | PASS |
| 2 | moment_x | 5.0 | 5.0 | PASS |
| 2 | stress | 13.47 | 13.47 | PASS |
| 2 | deflection | 0.340 | 0.340 | PASS |
| 2 | deflection_x | 8.82 | 8.82 | PASS |
| 3 | ra | 5.0 | 5.0 | PASS |
| 3 | fixed | 50.0 | 50.0 | PASS |
| 3 | deflection | 0.487 | 0.487 | PASS |
| 3 | deflection_x | 10.0 | 10.0 | PASS |
| 3 | allow_def | 0.333 | 0.333 | PASS |
| 3 | deflection_pass | False | False | PASS |
| 4 | moment | 0.90 | 0.90 | PASS |
| 4 | stress | 0.505 | 0.505 | PASS |
| 4 | deflection | 0.147 | 0.147 | PASS |
| 4 | bending_pass | True | True | PASS |
| 4 | deflection_pass | True | True | PASS |

All published checks passed.

## Desktop checks

- Tkinter application launched under Xvfb (Linux virtual display).
- Default case and cantilever case 3 passed via the actual GUI callbacks.
- Invalid span cleared the displayed result and disabled exports.
- Save and open restored the design; CSV had expected header and number of rows; PDF generated successfully.
- Default exported letter-size PDF rendered and visually inspected.
- Windows-specific visual layout, native dialog interactions, and hands-on mouse dragging/hovering still require local confirmation.
