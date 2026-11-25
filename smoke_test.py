"""Desktop smoke test: needs a graphical display (Xvfb is sufficient)."""
import tkinter as tk
from unittest.mock import patch
from tempfile import TemporaryDirectory
from pathlib import Path
import csv
from app import App
from beam import Design
from files_io import open_design

def run():
    root=tk.Tk(); a=App(root); root.update(); a.refresh(); root.update()
    assert abs(a.result.deflection-.60851927)<1e-7
    assert a.result.bending_pass and a.result.deflection_pass
    with TemporaryDirectory() as tmp:
        p=Path(tmp); j=p/'case.beam.json'; c=p/'case.csv'; f=p/'case.pdf'
        with patch('app.filedialog.asksaveasfilename',return_value=str(j)): a.save()
        assert open_design(j)==Design()
        with patch('app.filedialog.asksaveasfilename',return_value=str(c)): a.csv()
        with c.open(encoding='utf-8-sig') as handle: rows=list(csv.reader(handle))
        assert len(rows)==len(a.result.data)+1 and rows[0]==['x (ft)','V (kip)','M (kip-ft)','deflection (in)']
        with patch('app.filedialog.asksaveasfilename',return_value=str(f)): a.pdf()
        assert f.read_bytes().startswith(b'%PDF')
        a.support.set('Cantilever'); a.span.set('10'); a.remove(a.rows[0]); a.add('Point'); a.refresh(); root.update()
        assert not a.result.deflection_pass and abs(a.result.deflection-.4868154)<1e-7
        a.span.set('bad'); a.refresh(); assert a.result is None and str(a.csv_button['state'])=='disabled'
        with patch('app.filedialog.askopenfilename',return_value=str(j)): a.open()
        assert a.design()==Design() and a.result.deflection_pass
        a.material.set('Lumber'); a.refresh(); assert a.result.d.material=='Lumber'
        a.material.set('Steel'); a.section.set('W12x26'); a.limit.set('240'); a.refresh(); assert a.result.allow_def==1
    root.update(); root.destroy(); print('Tkinter smoke test passed: inputs, case 1 and 3, invalid state, save/open, CSV and PDF.')
if __name__=='__main__': run()
