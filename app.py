"""Beam Designer desktop user interface."""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from dataclasses import replace
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from beam import Analysis, Design, Load, TABLES
from plots import draw
from files_io import save_design, open_design

class App:
    def __init__(self, root):
        self.root=root; root.title('Beam Designer | CCE 270'); root.geometry('1200x800'); root.minsize(950,650)
        self.pending=None; self.busy=False; self.rows=[]; self.result=None; self.drag=None; self.axes=[]; self.cursor=[]
        style=ttk.Style(root); style.theme_use('clam'); style.configure('TFrame',background='#f1f5f6'); style.configure('TLabel',background='#f1f5f6',foreground='#243b49'); style.configure('Title.TLabel',font=('Segoe UI',20,'bold')); style.configure('TLabelframe',background='#f1f5f6'); style.configure('TLabelframe.Label',background='#f1f5f6',font=('Segoe UI',10,'bold')); style.configure('TButton',padding=5)
        main=ttk.Frame(root,padding=14); main.pack(fill='both',expand=True)
        header=ttk.Frame(main); header.pack(fill='x'); ttk.Label(header,text='Beam Designer',style='Title.TLabel').pack(side='left'); ttk.Label(header,text='Single-span analysis • CCE 270').pack(side='right')
        body=ttk.Panedwindow(main,orient='horizontal'); body.pack(fill='both',expand=True,pady=8)
        left=ttk.Frame(body,padding=8,width=370); right=ttk.Frame(body,padding=8); body.add(left,weight=0); body.add(right,weight=1)
        setup=ttk.LabelFrame(left,text='Beam setup',padding=10); setup.pack(fill='x')
        self.support=tk.StringVar(value='Simply supported'); self.span=tk.StringVar(value='20'); self.slider=tk.DoubleVar(value=20); self.material=tk.StringVar(value='Steel'); self.section=tk.StringVar(value='W12x26'); self.limit=tk.StringVar(value='360')
        def combo(label,var,values,row):
            ttk.Label(setup,text=label).grid(row=row,column=0,sticky='w',pady=4); c=ttk.Combobox(setup,textvariable=var,values=values,state='readonly',width=19); c.grid(row=row,column=1,sticky='ew',pady=4); return c
        combo('Support',self.support,['Simply supported','Cantilever'],0)
        ttk.Label(setup,text='Span (ft)').grid(row=1,column=0,sticky='w'); ttk.Entry(setup,textvariable=self.span,width=12).grid(row=1,column=1,sticky='ew')
        ttk.Scale(setup,from_=4,to=40,variable=self.slider,command=self.slide).grid(row=2,column=0,columnspan=2,sticky='ew',pady=5)
        combo('Material',self.material,list(TABLES),3); self.sections=combo('Section',self.section,list(TABLES['Steel']),4); combo('Deflection L /',self.limit,['240','360'],5); setup.columnconfigure(1,weight=1)
        loads=ttk.LabelFrame(left,text='Loads (downward positive)',padding=7); loads.pack(fill='both',expand=True,pady=10)
        buttons=ttk.Frame(loads); buttons.pack(fill='x'); ttk.Button(buttons,text='+ Point load',command=lambda:self.add('Point')).pack(side='left',expand=True,fill='x'); ttk.Button(buttons,text='+ Uniform load',command=lambda:self.add('Uniform')).pack(side='left',expand=True,fill='x')
        ttk.Label(loads,text='Magnitude: kip or kip/ft   •   positions: ft',wraplength=310).pack(anchor='w',pady=5)
        self.lcanvas=tk.Canvas(loads,background='#f1f5f6',highlightthickness=0,width=330,height=200); sc=ttk.Scrollbar(loads,orient='vertical',command=self.lcanvas.yview); sc.pack(side='right',fill='y'); self.lcanvas.pack(side='left',fill='both',expand=True); self.lcanvas.configure(yscrollcommand=sc.set)
        self.loadframe=ttk.Frame(self.lcanvas); win=self.lcanvas.create_window((0,0),window=self.loadframe,anchor='nw'); self.loadframe.bind('<Configure>',lambda e:self.lcanvas.configure(scrollregion=self.lcanvas.bbox('all'))); self.lcanvas.bind('<Configure>',lambda e:self.lcanvas.itemconfigure(win,width=e.width))
        self.status=tk.StringVar(value=''); ttk.Label(left,textvariable=self.status,wraplength=320,foreground='#a33b32').pack(fill='x')
        self.actions=ttk.Frame(left); self.actions.pack(fill='x',pady=5)
        menu=tk.Menu(root); self.filemenu=tk.Menu(menu,tearoff=False); menu.add_cascade(label='File',menu=self.filemenu); self.filemenu.add_command(label='Open',command=self.open); self.filemenu.add_command(label='Save',command=self.save); root.config(menu=menu)
        checks=ttk.Frame(right); checks.pack(fill='x'); self.cards=[]
        for name in ('Bending','Deflection'):
            card=ttk.LabelFrame(checks,text=name,padding=8); card.pack(side='left',fill='x',expand=True,padx=3); label=ttk.Label(card,text='—',font=('Segoe UI',11,'bold')); label.pack(anchor='w'); bar=tk.Canvas(card,height=9,background='#dce5e7',highlightthickness=0); bar.pack(fill='x',pady=4); self.cards.append((label,bar))
        rec=ttk.Frame(right); rec.pack(fill='x',pady=5); self.rec=tk.StringVar(); ttk.Label(rec,textvariable=self.rec).pack(side='left'); self.use=ttk.Button(rec,text='Use section',command=self.apply_recommendation); self.use.pack(side='right')
        self.fig=Figure(figsize=(7,6),dpi=100); self.canvas=FigureCanvasTkAgg(self.fig,master=right); self.canvas.get_tk_widget().pack(fill='both',expand=True); self.hover=tk.StringVar(value='Hover over a diagram to inspect values; drag a point-load arrow to move it.'); ttk.Label(right,textvariable=self.hover).pack(fill='x')
        self.canvas.mpl_connect('motion_notify_event',self.motion); self.canvas.mpl_connect('button_press_event',self.press); self.canvas.mpl_connect('button_release_event',self.release)
        self.span.trace_add('write',self.span_changed); self.material.trace_add('write',self.material_changed)
        for var in (self.support,self.section,self.limit): var.trace_add('write',self.queue)
        self.add('Uniform',Load('Uniform',1,0,20)); self.refresh()
    def slide(self,value):
        if not self.busy: self.span.set(f'{float(value):.2f}')
    def span_changed(self,*_):
        try:
            self.busy=True; self.slider.set(float(self.span.get()))
        except ValueError: pass
        finally: self.busy=False
        self.queue()
    def material_changed(self,*_):
        names=list(TABLES[self.material.get()]); self.sections.configure(values=names)
        if self.section.get() not in names: self.section.set(names[0])
        self.queue()
    def add(self,kind,load=None):
        try: L=float(self.span.get())
        except ValueError: L=20
        if load is None: load=Load(kind,5 if kind=='Point' else 1,L if kind=='Point' and self.support.get()=='Cantilever' else L/2 if kind=='Point' else 0,L if kind=='Uniform' else 0)
        f=ttk.LabelFrame(self.loadframe,text=kind,padding=4); f.pack(fill='x',pady=4)
        vs=[tk.StringVar(value=f'{v:g}') for v in (load.magnitude,load.start,load.end)]
        row=(f,kind,vs); ttk.Button(f,text='Remove',command=lambda:self.remove(row)).grid(row=0,column=2,padx=2)
        for i,name in enumerate(['Magnitude','Position' if kind=='Point' else 'Start','End'][:2 if kind=='Point' else 3]):
            ttk.Label(f,text=name).grid(row=i,column=0,sticky='w'); ttk.Entry(f,textvariable=vs[i],width=10).grid(row=i,column=1,pady=2,sticky='ew'); vs[i].trace_add('write',self.queue)
        self.rows.append(row); self.queue()
    def remove(self,row): self.rows.remove(row); row[0].destroy(); self.queue()
    def design(self):
        return Design(self.support.get(),float(self.span.get()),self.material.get(),self.section.get(),int(self.limit.get()),tuple(Load(k,float(v[0].get()),float(v[1].get()),float(v[2].get()) if k=='Uniform' else 0) for _,k,v in self.rows))
    def queue(self,*_):
        if self.pending is not None: self.root.after_cancel(self.pending)
        self.pending=self.root.after(120,self.refresh)
    def refresh(self):
        if self.pending is not None: self.root.after_cancel(self.pending); self.pending=None
        try: self.result=Analysis(self.design()); a=self.result
        except (ValueError,OverflowError) as e:
            self.result=None; self.status.set(str(e)); self.fig.clear(); self.axes=[]; self.canvas.draw_idle(); self.rec.set('No valid design'); self.use.configure(state='disabled')
            for label,bar in self.cards: label.configure(text='—'); bar.delete('all')
            self.export_state(False); return
        self.status.set(''); self.axes=draw(self.fig,a); self.cursor=[]; self.canvas.draw_idle()
        for (label,bar),actual,allow,unit,passed in zip(self.cards,[a.stress,a.deflection],[a.Fb,a.allow_def],['ksi','in'],[a.bending_pass,a.deflection_pass]):
            r=actual/allow; color='#27835c' if r<.7 else '#b47b1b' if r<=1 else '#b73535'; label.configure(text=f'{actual:.3f} / {allow:.3f} {unit}  •  {"PASS" if passed else "FAIL"}  ({r:.0%})',foreground=color); bar.delete('all'); bar.create_rectangle(0,0,max(1,bar.winfo_width(),180)*min(r,1),9,fill=color,outline='')
        self.suggested=a.recommendation(); self.rec.set('Lightest passing: '+(self.suggested or 'None in this material')); self.use.configure(state='normal' if self.suggested else 'disabled'); self.export_state(True)
    def export_state(self,valid): self.filemenu.entryconfigure('Save',state='normal' if valid else 'disabled')
    def save(self):
        self.refresh()
        if not self.result: return
        path=filedialog.asksaveasfilename(defaultextension='.beam.json',filetypes=[('Beam design','*.beam.json'),('JSON','*.json')])
        if path:
            try: save_design(path,self.design())
            except (OSError,ValueError,TypeError) as e: messagebox.showerror('Save failed',str(e))
    def open(self):
        path=filedialog.askopenfilename(filetypes=[('Beam design','*.beam.json'),('JSON','*.json'),('All files','*.*')])
        if not path: return
        try: d=open_design(path)
        except (OSError,ValueError,TypeError,KeyError,OverflowError) as e: messagebox.showerror('Open failed',str(e)); return
        self.support.set(d.support); self.span.set(str(d.span)); self.material.set(d.material); self.section.set(d.section); self.limit.set(str(d.limit))
        for row in self.rows[:]: self.remove(row)
        for l in d.loads: self.add(l.kind,l)
        self.refresh()
    def apply_recommendation(self):
        if self.result and self.suggested: self.section.set(self.suggested)
    def motion(self,event):
        if not self.result or event.inaxes not in self.axes or event.xdata is None: return
        x=max(0,min(self.result.d.span,event.xdata))
        if self.drag is not None: return
        if event.inaxes==self.axes[0]: return
        for line in self.cursor: line.remove()
        self.cursor=[ax.axvline(x,color='#64748b',ls='--',lw=.8) for ax in self.axes[1:]]; v,m,y=self.result.values(x); self.hover.set(f'x = {x:.2f} ft   |   V = {v:.3f} kip   |   M = {m:.3f} kip-ft   |   y = {y:.3f} in'); self.canvas.draw_idle()
    def press(self,event):
        if self.result and self.axes and event.inaxes==self.axes[0] and event.xdata is not None and event.button==1:
            candidates=[(abs(min(float(v[1].get()),self.result.d.span)-event.xdata),v) for _,k,v in self.rows if k=='Point']
            if candidates:
                dist,v=min(candidates,key=lambda item:item[0]); self.drag=v if dist<self.result.d.span*.06 else None
    def release(self,event):
        if self.drag is not None:
            if event.xdata is not None and self.result: self.drag[1].set(f'{min(self.result.d.span,max(0,round(event.xdata*4)/4)):g}')
            self.drag=None

def main():
    root=tk.Tk(); App(root); root.mainloop()
if __name__=='__main__': main()
