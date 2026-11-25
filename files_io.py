"""File persistence and export helpers."""
import json
from dataclasses import asdict
from pathlib import Path
from beam import Design, Load, Analysis

def save_design(path,d):
    Analysis(d)
    Path(path).write_text(json.dumps({'version':1,**asdict(d)},indent=2,allow_nan=False)+'\n',encoding='utf-8')

def open_design(path):
    obj=json.loads(Path(path).read_text(encoding='utf-8'))
    if not isinstance(obj,dict) or obj.pop('version',None)!=1: raise ValueError('Unsupported beam file version.')
    obj['loads']=tuple(Load(**l) for l in obj['loads']); d=Design(**obj); Analysis(d); return d

def export_csv(path,a):
    import csv
    with open(path,'w',newline='',encoding='utf-8-sig') as f:
        writer=csv.writer(f); writer.writerow(['x (ft)','V (kip)','M (kip-ft)','deflection (in)'])
        writer.writerows([f'{v:.10g}' for v in row] for row in a.data)

def export_pdf(path,a):
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_pdf import PdfPages
    from plots import draw
    d=a.d
    with PdfPages(path) as pdf:
        fig=Figure(figsize=(8.5,11)); draw(fig,a,report=True)
        fig.subplots_adjust(top=.75,bottom=.13,hspace=.42)
        fig.text(.1,.955,'BEAM DESIGNER',fontsize=23,fontweight='bold',color='#243b49')
        fig.text(.1,.925,'Calculation sheet  |  CCE 270',fontsize=11,color='#157b80')
        fig.text(.1,.895,f'{d.support}   |   Span {d.span:g} ft   |   {d.material} {d.section}   |   L/{d.limit}',fontsize=10)
        fig.text(.1,.873,f'E = {a.E:,.0f} ksi     I = {a.I:g} in⁴     S = {a.S:g} in³     Self-weight excluded',fontsize=9)
        if len(d.loads)<=4:
            load_text='; '.join(f'{l.magnitude:g} kip at {l.start:g} ft' if l.kind=='Point' else f'{l.magnitude:g} kip/ft from {l.start:g} to {l.end:g} ft' for l in d.loads) or 'No loads'
            import textwrap
            fig.text(.1,.85,'Loads: '+'\n'.join(textwrap.wrap(load_text,95)),fontsize=8,va='top')
        else: fig.text(.1,.85,f'Loads: {len(d.loads)} entries (see load schedule on following pages)',fontsize=9)
        fig.text(.1,.083,f'Bending: {a.stress:.3f} / {a.Fb:.3f} ksi  —  {"PASS" if a.bending_pass else "FAIL"}     Deflection: {a.deflection:.3f} / {a.allow_def:.3f} in  —  {"PASS" if a.deflection_pass else "FAIL"}',fontsize=10,fontweight='bold')
        fig.text(.1,.055,'Downward loads positive; sagging moment positive; upward displacement positive.',fontsize=8,color='#52636e')
        fig.text(.1,.035,'Classroom elastic beam model only; not a complete structural design or approval.',fontsize=8,color='#52636e'); pdf.savefig(fig)
        if len(d.loads)>4:
            for start in range(0,len(d.loads),35):
                page=Figure(figsize=(8.5,11)); page.text(.1,.94,'Load schedule',fontsize=20,fontweight='bold'); page.text(.1,.91,f'{d.section} • {d.span:g} ft • {d.support}',fontsize=10)
                for i,l in enumerate(d.loads[start:start+35]):
                    detail=f'{l.magnitude:g} kip at {l.start:g} ft' if l.kind=='Point' else f'{l.magnitude:g} kip/ft from {l.start:g} to {l.end:g} ft'
                    page.text(.12,.87-i*.022,f'{start+i+1:>3}. {l.kind}: {detail}',fontsize=9)
                pdf.savefig(page)
