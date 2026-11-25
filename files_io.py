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
