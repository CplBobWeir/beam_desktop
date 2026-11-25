"""Statically determinate beam calculations; ft, kip, kip-ft, inch."""
from dataclasses import dataclass, replace
import math
import numpy as np
from numpy.polynomial import Polynomial as Poly

STEEL = {'W8x10': (30.8,7.81,10), 'W10x12': (53.8,10.9,12), 'W12x26': (204,33.4,26), 'W14x22': (199,29,22), 'W16x26': (301,38.4,26), 'W18x35': (510,57.6,35), 'W21x44': (843,81.6,44), 'W24x55': (1350,114,55)}
LUMBER = {'2x8': (47.63,13.14,0), '2x10': (98.93,21.39,0), '2x12': (177.98,31.64,0)}
TABLES = {'Steel': STEEL, 'Lumber': LUMBER}
PROPERTIES = {'Steel': (29000,30), 'Lumber': (1600,.9)}
@dataclass(frozen=True)
class Load:
    kind: str
    magnitude: float
    start: float
    end: float = 0
@dataclass(frozen=True)
class Design:
    support: str = 'Simply supported'
    span: float = 20
    material: str = 'Steel'
    section: str = 'W12x26'
    limit: int = 360
    loads: tuple = (Load('Uniform',1,0,20),)

def normalized(d):
    if d.support not in ('Simply supported','Cantilever') or d.material not in TABLES or d.section not in TABLES[d.material] or d.limit not in (240,360):
        raise ValueError('Choose valid support, material, section and limit.')
    if not math.isfinite(d.span) or not 4 <= d.span <= 40: raise ValueError('Span must be 4–40 ft.')
    loads=[]
    for l in d.loads:
        if l.kind not in ('Point','Uniform') or not all(math.isfinite(v) for v in (l.magnitude,l.start,l.end)) or l.start<0 or (l.kind=='Uniform' and l.end<0):
            raise ValueError('Use finite loads and nonnegative positions.')
        a=min(l.start,d.span); b=min(l.end,d.span)
        if l.kind=='Uniform':
            if l.end<=l.start: raise ValueError('Uniform load end must exceed its start.')
            if b<=a: continue # fully outside span contributes nothing
        loads.append(Load(l.kind,l.magnitude,a,b if l.kind=='Uniform' else 0))
    return replace(d,loads=tuple(loads))

class Analysis:
    def __init__(self, design):
        self.d=normalized(design); d=self.d; L=d.span
        self.I,self.S,_=TABLES[d.material][d.section]; self.E,self.Fb=PROPERTIES[d.material]
        total=first=0
        for l in d.loads:
            force=l.magnitude if l.kind=='Point' else l.magnitude*(l.end-l.start)
            center=l.start if l.kind=='Point' else (l.start+l.end)/2
            total+=force; first+=force*center
        self.rb=first/L if d.support=='Simply supported' else 0
        self.ra=total-self.rb
        self.fixed=first if d.support=='Cantilever' else 0
        # Macaulay terms in ft: M(x) = -fixed + RA*x + sum c*(x-a)_+^n.
        self.terms=[(0,self.ra,1)]
        for l in d.loads:
            if l.kind=='Point': self.terms.append((l.start,-l.magnitude,1))
            else: self.terms.extend([(l.start,-l.magnitude/2,2),(l.end,l.magnitude/2,2)])
        self.factor=1728/(self.E*self.I)
        self.c1=-self.raw(L)/L if d.support=='Simply supported' else 0
        self.breaks=sorted({0.,float(L),*[a for a,_,_ in self.terms]})
        samples=set(np.linspace(0,L,math.ceil(L*10)+1))|set(self.breaks)
        for a,b in zip(self.breaks,self.breaks[1:]):
            p=Poly([a,1]); m=Poly([-self.fixed]); slope= -self.fixed*p + self.c1
            for pos,c,n in self.terms:
                if pos<=a:
                    m+=c*(p-pos)**n
                    slope+=c*(p-pos)**(n+1)/(n+1)
            for polynomial in (m.deriv(),slope):
                for root in polynomial.roots():
                    if abs(root.imag)<1e-8 and 0<root.real<b-a: samples.add(float(a+root.real))
        xs=sorted(samples); rows=[]
        for x in xs:
            if x in self.breaks and x>0: rows.append((x,*self.values(x,False)))
            rows.append((x,*self.values(x,True)))
        self.data=np.array(rows)
        self.peaks=[self.data[np.argmax(np.abs(self.data[:,i])),[0,i]] for i in (1,2,3)]
        self.stress=abs(self.peaks[1][1])*12/self.S
        self.deflection=abs(self.peaks[2][1]); self.allow_def=12*L/d.limit
        self.bending_pass=self.stress<=self.Fb+1e-10
        self.deflection_pass=self.deflection<=self.allow_def+1e-10
    def raw(self,x):
        return -self.fixed*x*x/2+sum(c*max(x-a,0)**(n+2)/((n+1)*(n+2)) for a,c,n in self.terms)
    def values(self,x,right=True):
        moment=-self.fixed+sum(c*max(x-a,0)**n for a,c,n in self.terms)
        shear=sum(c*n*max(x-a,0)**(n-1) for a,c,n in self.terms if x>a or (right and x==a))
        if right and x==self.d.span: shear+=self.rb
        return shear,moment,(self.raw(x)+self.c1*x)*self.factor
    def recommendation(self):
        names=list(TABLES[self.d.material])
        if self.d.material=='Steel': names.sort(key=lambda n:(STEEL[n][2],-STEEL[n][0]))
        for name in names:
            trial=Analysis(replace(self.d,section=name))
            if trial.bending_pass and trial.deflection_pass: return name
        return None
