"""Render publication charts from saved study results; never runs models."""
import os
from pathlib import Path
HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
os.environ.setdefault('MPLCONFIGDIR', str(STUDY.parents[1]/'.experiments/matplotlib'))
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

v2 = json.loads((STUDY/'v2/results/summary.json').read_text())
extra = json.loads((STUDY/'additional/results/summary.json').read_text())
public = json.loads((STUDY/'extension/results/local-summary.json').read_text())
native = json.loads((STUDY/'extension/results/native-full-summary.json').read_text())
qwen = json.loads((STUDY/'general-baseline/results/summary.json').read_text())
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'axes.spines.top':False,
                    'axes.spines.right':False,'axes.spines.left':False,'axes.edgecolor':'#ccd3db',
                    'text.color':'#172b41','axes.labelcolor':'#172b41','xtick.color':'#44576b',
                    'ytick.color':'#172b41','svg.fonttype':'none','figure.facecolor':'#ffffff'})
COLORS = ['#187d83','#c34345','#b07818']
out = HERE/'figures'; out.mkdir(exist_ok=True)
def save(fig,name):
    fig.savefig(out/f'{name}.svg',bbox_inches='tight')
    svg = out/f'{name}.svg'
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
    fig.savefig(out/f'{name}.png',dpi=180,bbox_inches='tight')
    plt.close(fig)

evidence_rows = []
for arm,point in [('app-full','default'),('app-full','selected')]:
    m=v2[arm][point]; evidence_rows.append([m[k] for k in ['legitimate_approvals','deny_approvals','unknown_approvals']])
evidence_rows.append([qwen['test']['by_expected'][key]['predicted']['allow'] for key in ['allow','deny','ask']])
limited_rows = []
m=v2['lancet']['default'];limited_rows.append([m[k] for k in ['legitimate_approvals','deny_approvals','unknown_approvals']])
for name in ['modernbert','kestrel','secguard']:
    m=extra[f'{name}/allow/v2/test'];limited_rows.append([m[k][0] for k in ['allow','deny','ask']])
def repository_chart(name, title, labels, results, height):
    fig,ax=plt.subplots(figsize=(9,height));y=np.arange(len(labels))
    for j,heading in enumerate(['Expected allow','Expected deny','Expected ask']):
        values=[r[j] for r in results]
        ax.barh(y+(j-1)*.22,values,height=.19,color=COLORS[j],label=heading)
        for i,value in enumerate(values):
            ax.text(max(value,.08)+.13,y[i]+(j-1)*.22,str(value),va='center',fontsize=11)
    ax.set(yticks=y,yticklabels=labels,xlim=(0,13.1),ylim=(len(labels)-.45,-.65),
           xticks=[0,3,6,9,12],xlabel='Commands approved (of 12 per expected label)')
    ax.grid(axis='x',alpha=.15);ax.set_axisbelow(True)
    ax.legend(loc='lower left',bbox_to_anchor=(0,1.01),ncol=3,frameon=False,fontsize=11)
    fig.suptitle(title,x=.02,ha='left',fontsize=17,fontweight='bold')
    fig.subplots_adjust(left=.24,right=.96,top=.73,bottom=.16)
    save(fig,name)

repository_chart('repository-evidence','With task and repository evidence',
                 ['AutoShell default','AutoShell strict','Qwen3.5 4B'],evidence_rows,3.6)
repository_chart('repository-limited-input','Without repository file contents',
                 ['LANCET','ModernBERT','Kestrel','secguard*'],limited_rows,4.0)

names=['AutoShell','LANCET Nano','ModernBERT','Kestrel','secguard*']
values=[]
for name in ['public-autoshell-command','public-lancet']:
    s=public[name]['sourceDataset'];values.append([s[x]['unsafe_approvals'] for x in ['shellrisk','shellsafety']])
for name in ['modernbert','kestrel','secguard']:
    values.append([extra[f'{name}/allow/public/{x}']['deny'][0] for x in ['shellrisk','shellsafety']])
fig,ax=plt.subplots(figsize=(9,3.8));x=np.arange(5)
for j,(title,color) in enumerate([('ShellRisk-Bench','#546b98'),('Shell Safety','#c34345')]):
    bars=ax.bar(x+(j-.5)*.34,[v[j] for v in values],width=.31,color=color,label=title)
    ax.bar_label(bars,labels=[str(v[j]) for v in values],padding=4,fontsize=11)
ax.set(xticks=x,xticklabels=names,ylim=(0,59),yticks=[0,10,20,30,40,50],ylabel='Unsafe approvals ↓')
ax.legend(frameon=False,loc='upper left');fig.suptitle('Unsafe approvals across public test sets',x=.02,ha='left',fontsize=17,fontweight='bold')
fig.subplots_adjust(bottom=.19,top=.86,left=.10,right=.97)
save(fig,'dataset-transfer')

names=['Kestrel · CPU','LANCET Nano · CPU','ModernBERT · CPU','secguard* · CPU','Qwen3.5 4B · Metal','AutoShell · CPU']
times=[extra['kestrel/allow/v2/test']['p50_ms'],v2['lancet']['default']['p50_ms'],extra['modernbert/allow/v2/test']['p50_ms'],extra['secguard/allow/v2/test']['p50_ms'],qwen['test']['p50_ms'],v2['app-full']['default']['p50_ms']]
fig,ax=plt.subplots(figsize=(9,3.8));y=np.arange(len(names))
ax.scatter([t for i,t in enumerate(times) if i != 4],[i for i in y if i != 4],s=100,color='#187d83',zorder=3,label='CPU')
ax.scatter([times[4]],[4],s=110,marker='D',color='#6d5a9c',zorder=3,label='Metal')
for i,t in enumerate(times):ax.text(t*1.25,i,f'{t:,.3f} ms' if t<1 else f'{t:,.1f} ms',va='center',fontsize=11)
ax.set(xscale='log',xlim=(.01,20000),yticks=y,yticklabels=names,xlabel='Median response time (ms) · log scale')
ax.invert_yaxis();ax.grid(axis='x',alpha=.18)
fig.suptitle('Local model response time',x=.02,ha='left',fontsize=17,fontweight='bold')
fig.subplots_adjust(left=.29,bottom=.18,top=.80,right=.96)
save(fig,'latency')

groups=[('Allow','allow'),('Deny','deny'),('Ask','ask')]
fig,ax=plt.subplots(figsize=(9,3.4));y=np.arange(len(groups))
for offset,provider,color in [(-.18,'codex','#187d83'),(.18,'claude','#546b98')]:
    counts=native['providers'][provider]['counts']
    values=[counts[f'{key}_candidateToolReturned'] for _,key in groups]
    ax.barh(y+offset,values,height=.31,color=color,label=provider.title())
    for i,(_,key) in enumerate(groups):
        total=counts[f'comparableLabel_{key}']
        ax.text(max(values[i],.08)+.25,y[i]+offset,f'{values[i]}/{total}',va='center',fontsize=11,fontweight='bold')
labels=[f"{heading} · {native['providers']['codex']['counts'][f'comparableLabel_{key}']} cases" for heading,key in groups]
ax.set(yticks=y,yticklabels=labels,xlim=(0,30),xticks=[0,6,12,18,24],xlabel='Commands that reached the tool')
ax.invert_yaxis();ax.grid(axis='x',alpha=.15);ax.set_axisbelow(True)
ax.legend(frameon=False,loc='lower left',bbox_to_anchor=(0,1.01),ncol=2)
fig.suptitle('Codex and Claude agent paths',x=.02,ha='left',fontsize=17,fontweight='bold')
fig.subplots_adjust(left=.21,right=.96,top=.73,bottom=.17)
save(fig,'native-path')
print('Rendered five charts as SVG and PNG.')

# Refresh the standalone HTML with the saved chart images.
import runpy
runpy.run_path(str(HERE / 'render_html.py'))
