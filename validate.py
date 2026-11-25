"""Run published reference cases; exits nonzero on a discrepancy."""
from beam import *
import unittest

CASES=[
 ('1',Design(),[('ra',10,1),('rb',10,1),('shear',10,1),('moment',50,1),('moment_x',10,1),('stress',17.96,2),('deflection',.609,3),('deflection_x',10,1),('allow_def',.667,3),('bending_pass',True,0),('deflection_pass',True,0)]),
 ('2',Design(loads=(Load('Point',10,5),)),[('ra',7.5,1),('rb',2.5,1),('moment',37.5,1),('moment_x',5,1),('stress',13.47,2),('deflection',.340,3),('deflection_x',8.82,2)]),
 ('3',Design('Cantilever',10,loads=(Load('Point',5,10),)),[('ra',5,1),('fixed',50,1),('deflection',.487,3),('deflection_x',10,1),('allow_def',.333,3),('deflection_pass',False,0)]),
 ('4',Design('Simply supported',12,'Lumber','2x10',loads=(Load('Uniform',.05,0,12),)),[('moment',.90,2),('stress',.505,3),('deflection',.147,3),('bending_pass',True,0),('deflection_pass',True,0)])]

def run():
    print('| Case | Quantity | Expected | Actual | Status |\n|---|---|---:|---:|---|')
    failed=0
    for case,d,expected in CASES:
        a=Analysis(d); values={'shear':abs(a.peaks[0][1]),'moment':abs(a.peaks[1][1]),'moment_x':a.peaks[1][0],'deflection_x':a.peaks[2][0]}
        for name,target,digits in expected:
            actual=values[name] if name in values else getattr(a,name)
            if isinstance(target,bool): ok=actual==target; e=str(target); v=str(actual)
            else: e=f'{target:.{digits}f}'; v=f'{actual:.{digits}f}'; ok=e==v
            failed+=not ok; print(f'| {case} | {name} | {e} | {v} | {"PASS" if ok else "FAIL"} |')
    print(f'\n{"All published checks passed." if not failed else str(failed)+" checks failed."}')
    if failed: raise SystemExit(1)
if __name__=='__main__': run()
