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
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,
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

rows = []
for arm,point in [('app-full','default'),('app-full','selected'),('lancet','default')]:
    m=v2[arm][point]; rows.append([m[k] for k in ['legitimate_approvals','deny_approvals','unknown_approvals']])
for name in ['modernbert','kestrel','secguard']:
    m=extra[f'{name}/allow/v2/test'];rows.append([m[k][0] for k in ['allow','deny','ask']])
def repository_chart(name, title, labels, results, note, height):
    fig,ax=plt.subplots(figsize=(10,height));y=np.arange(len(labels))
    for j,heading in enumerate(['Allow approved ↑','Deny approved ↓','Ask approved ↓']):
        values=[r[j] for r in results]
        ax.barh(y+(j-1)*.22,values,height=.19,color=COLORS[j],label=heading)
        for i,value in enumerate(values):
            ax.text(max(value,.08)+.13,y[i]+(j-1)*.22,f'{value}/12',va='center',fontsize=9)
    ax.set(yticks=y,yticklabels=labels,xlim=(0,13.6),ylim=(len(labels)-.45,-.65),
           xticks=[0,3,6,9,12],xlabel='Approvals out of 12 cases per label')
    ax.grid(axis='x',alpha=.15);ax.set_axisbelow(True)
    ax.legend(loc='lower left',bbox_to_anchor=(0,1.01),ncol=3,frameon=False,fontsize=10)
    fig.suptitle(title,x=.02,ha='left',fontsize=17,fontweight='bold')
    fig.subplots_adjust(left=.31,right=.94,top=.75,bottom=.20)
    fig.text(.02,.035,note,fontsize=9)
    save(fig,name)

repository_chart('repository-evidence','With task and repository evidence',
                 ['AutoShell · default cutoff','AutoShell · stricter cutoff'],rows[:2],
                 'Same model and inputs; only the approval cutoff changes. Stricter cutoff chosen on development cases.\nAsk = missing evidence: inspect or clarify before approval, not proven harm.',3.8)
repository_chart('repository-limited-input','Without repository file contents',
                 ['LANCET · command','ModernBERT · command + directory','Kestrel · command','secguard* · command'],rows[2:],
                 'These tools use different supplied decision rules and inputs. No cutoff was tuned on these test cases.\n*secguard artifact/runtime needs investigation. Ask = missing evidence, not proven harm.',4.6)

names=['AutoShell\ncommand','LANCET Nano\ncommand','ModernBERT\ncommand + CWD','Kestrel\ncommand','secguard*\ncommand']
values=[]
for name in ['public-autoshell-command','public-lancet']:
    s=public[name]['sourceDataset'];values.append([s[x]['unsafe_approvals'] for x in ['shellrisk','shellsafety']])
for name in ['modernbert','kestrel','secguard']:
    values.append([extra[f'{name}/allow/public/{x}']['deny'][0] for x in ['shellrisk','shellsafety']])
fig,ax=plt.subplots(figsize=(10,4.5));x=np.arange(5)
for j,(title,color) in enumerate([('ShellRisk-Bench','#546b98'),('Shell Safety','#c34345')]):
    bars=ax.bar(x+(j-.5)*.34,[v[j] for v in values],width=.31,color=color,label=title)
    ax.bar_label(bars,labels=[f'{v[j]}/50' for v in values],padding=4,fontsize=10)
ax.set(xticks=x,xticklabels=names,ylim=(0,59),yticks=[0,10,20,30,40,50],ylabel='Unsafe approvals ↓')
ax.legend(frameon=False,loc='upper left');fig.suptitle('A strong score on one dataset may not transfer',x=.02,ha='left',fontsize=17,fontweight='bold')
fig.subplots_adjust(bottom=.24,top=.86,left=.09)
fig.text(.02,.035,'Frozen samples: 100 cases per source, including 50 unsafe cases. Source policies differ.\nNo model in this panel receives repository file contents. *secguard deployment needs investigation.',fontsize=9)
save(fig,'dataset-transfer')

names=['Kestrel · command (Python port)','LANCET Nano · command','ModernBERT · command + CWD','secguard* · command','AutoShell · repository evidence']
times=[extra['kestrel/allow/v2/test']['p50_ms'],v2['lancet']['default']['p50_ms'],extra['modernbert/allow/v2/test']['p50_ms'],extra['secguard/allow/v2/test']['p50_ms'],v2['app-full']['default']['p50_ms']]
fig,ax=plt.subplots(figsize=(10,3.9));y=np.arange(5)
ax.scatter(times,y,s=90,color='#187d83',zorder=3)
for i,t in enumerate(times):ax.text(t*1.3,i,f'{t:,.3f} ms' if t<1 else f'{t:,.1f} ms',va='center',fontsize=10)
ax.set(xscale='log',xlim=(.01,20000),yticks=y,yticklabels=names,xlabel='Median warm inference time in milliseconds · logarithmic scale')
ax.invert_yaxis();ax.grid(axis='x',alpha=.18)
fig.suptitle('Local inference spans microseconds to seconds',x=.02,ha='left',fontsize=18,fontweight='bold')
fig.subplots_adjust(left=.37,bottom=.26,top=.83)
fig.text(.02,.035,'Apple M1 Pro, 16 GB; CPU inference. Different input sizes and runtimes, measured in separate runs.\nExcludes model loading and evidence collection (~41 ms median). *secguard deployment needs investigation.',fontsize=9)
save(fig,'latency')

providers=['Codex','Claude']
groups=[('Allow: supported action','allow'),('Deny: observed conflict','deny'),('Ask: evidence missing','ask')]
fig,axes=plt.subplots(1,3,figsize=(12,4.3),sharey=True)
for ax,(heading,key) in zip(axes,groups):
    total=native['providers']['codex']['counts'][f'comparableLabel_{key}']
    values=[native['providers'][p.lower()]['counts'][f'{key}_candidateToolReturned'] for p in providers]
    bars=ax.bar(providers,values,color=['#187d83','#546b98'],width=.55)
    ax.bar_label(bars,labels=[f'{v}/{total}' for v in values],padding=5,fontsize=11,fontweight='bold')
    ax.set(title=heading,ylim=(0,28),yticks=[0,6,12,18,24],ylabel='Candidate tool returned' if key=='allow' else '')
    ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
fig.suptitle('Native path: agent choice plus permission outcome',x=.02,ha='left',fontsize=18,fontweight='bold')
fig.subplots_adjust(left=.07,right=.99,wspace=.20,top=.72,bottom=.29)
fig.text(.02,.075,'72 cases per provider; 6 Node startup cases/provider excluded here because preload was absent from live tool environment.',fontsize=9)
fig.text(.02,.035,'Ask means inspect or clarify first; a returned tool is not proof of harm. Claude has no separate positive verdict.',fontsize=9)
save(fig,'native-path')
print('Rendered five charts as SVG and PNG.')

# Refresh the standalone HTML with the saved chart images.
import runpy
runpy.run_path(str(HERE / 'render_html.py'))
