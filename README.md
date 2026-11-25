# Beam Designer (desktop)

A Python/Tkinter app for simply supported and cantilever beams. Edit point and uniform loads, choose a steel or lumber section, and see reactions, shear, moment, deflection and simplified bending/stiffness checks. Save and reopen designs, export results to Excel-compatible CSV, or generate a letter-size calculation sheet PDF.

## Run on Windows

1. Extract the ZIP to a normal folder (do not run inside the ZIP).
2. Open `beam_desktop` in VS Code. Open a terminal in that folder.
3. Install dependencies and check Tkinter:

   ```powershell
   python -m pip install -r requirements.txt
   python -m tkinter
   ```

   Close the Tkinter test window, then run:

   ```powershell
   python app.py
   ```

On macOS or Linux, use `python3` if your `python` command is unavailable. Tkinter is included in the standard Windows/macOS Python installers from python.org. Some Linux distributions require a separate system package such as `python3-tk`.

## Try the features

The opening example is validation case 1. It should show 10 kip at each support, 50 kip-ft maximum moment, 17.964 ksi bending stress and 0.609 in maximum deflection. Both checks pass. Change supports, span, loads, material, section and deflection limit; use the recommendation button, hover over diagrams and drag a point load. Save using File > Save, edit a value, then File > Open and select your saved design. Export CSV and PDF and open both files to inspect them.

Run `python validate.py` to reproduce all published numerical checks. `python smoke_test.py` exercises the main GUI callbacks and export actions on a graphical desktop; the test uses temporary files and mocked file-dialog selections. See `validation.md` for the measured results.

## Files

- `app.py`: Tkinter user interface
- `beam.py`: beam calculations and section selection
- `plots.py`: beam and diagram drawing
- `files_io.py`: JSON persistence and CSV/PDF export
- `spec.md`: desktop specification adapted from the official BYU course Beam Designer spec
- `AGENTS.md`, `prompts.md`: agent rules and actual implementation log
- `reference/`: original uploaded Concrete Pour Planner files, which were not Beam Designer references

## Limits

For classroom use only. Simplified linear-elastic beam checks do not account for self-weight, shear stress, buckling, load combinations, or other structural design requirements. The actual Beam Designer web HTML was not provided; the public course specification was used instead. Tests were performed in a Linux virtual display, not on the student's Windows PC. Local hands-on testing, publishing to GitHub and submission remain the student's responsibility.
