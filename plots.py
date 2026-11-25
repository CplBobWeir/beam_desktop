"""Shared drawing for desktop and calculation sheet."""
from matplotlib.figure import Figure
import numpy as np

ACCENT='#157b80'

def draw(fig, a, report=False):
    fig.clear(); fig.set_facecolor('white')
    axes=fig.subplots(4,1,sharex=True,gridspec_kw={'height_ratios':[1,1,1,1]})
    fig.subplots_adjust(left=.15,right=.95,top=.87 if report else .96,bottom=.09,hspace=.43)
    L=a.d.span; ax=axes[0]
    ax.plot([0,L],[0,0],color='#253c4b',lw=4,solid_capstyle='round')
    if a.d.support=='Simply supported':
        ax.scatter([0,L],[-.07,-.07],marker='^',s=120,color='#253c4b',clip_on=False)
    else: ax.plot([0,0],[-.2,.24],lw=6,color='#253c4b')
    for l in a.d.loads:
        if not l.magnitude: continue
        sign=1 if l.magnitude>0 else -1
        if l.kind=='Point':
            ax.annotate('',(l.start,0),(l.start,.55*sign),arrowprops={'arrowstyle':'-|>','color':ACCENT,'lw':1.8})
            ax.text(l.start,.61*sign,f'{l.magnitude:g} k',ha='center',va='bottom' if sign>0 else 'top',fontsize=8)
        else:
            for x in np.linspace(l.start,l.end,max(2,min(18,int((l.end-l.start)*2)+1))):
                ax.annotate('',(x,0),(x,.35*sign),arrowprops={'arrowstyle':'-|>','color':ACCENT,'lw':1})
            ax.plot([l.start,l.end],[.35*sign]*2,color=ACCENT,lw=1)
            ax.text((l.start+l.end)/2,.42*sign,f'{l.magnitude:g} k/ft',ha='center',va='bottom' if sign>0 else 'top',fontsize=8)
    ax.text(0,-.35,f'RA {a.ra:.2f} k',ha='left',fontsize=8)
    if a.d.support=='Simply supported': ax.text(L,-.35,f'RB {a.rb:.2f} k',ha='right',fontsize=8)
    else: ax.text(0,-.57,f'Fixed moment {a.fixed:.2f} kip-ft',ha='left',fontsize=8)
    ax.set_ylim(-.86,.85); ax.set_yticks([]); ax.set_title('Beam and loads',loc='left',fontsize=10,fontweight='bold')
    for spine in ax.spines.values(): spine.set_visible(False)
    for i,(ax,title,unit,color) in enumerate(zip(axes[1:],['Shear','Moment','Deflection'],['kip','kip-ft','in'],[ACCENT,'#4774a6','#a16b38']),1):
        x=a.data[:,0]; y=a.data[:,i]; ax.axhline(0,color='#9cabb4',lw=.8); ax.plot(x,y,color=color,lw=1.6); ax.fill_between(x,0,y,color=color,alpha=.18)
        xp,yp=a.peaks[i-1]; ax.scatter([xp],[yp],s=18,color=color,zorder=5)
        ax.annotate(f'{yp:.3f} @ {xp:.2f} ft',(xp,yp),xytext=(5,-13 if yp>=0 else 8),textcoords='offset points',fontsize=7,ha='right' if xp>L*.8 else 'left')
        ax.set_ylabel(unit,fontsize=8); ax.set_title(title,loc='left',fontsize=10,fontweight='bold'); ax.grid(axis='x',alpha=.18); ax.margins(y=.22)
        ax.tick_params(labelsize=8); ax.spines[['top','right']].set_visible(False)
    axes[-1].set_xlabel('Position along beam (ft)',fontsize=9); axes[-1].set_xlim(-L*.025,L*1.025)
    return axes
