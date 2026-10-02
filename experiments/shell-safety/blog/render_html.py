"""Refresh the offline reading copy from saved charts and article text."""
import base64
from pathlib import Path

from markdown_it import MarkdownIt

HERE = Path(__file__).resolve().parent
body = MarkdownIt().render((HERE / 'POST.md').read_text())
for name in ['repository-decisions', 'dataset-transfer', 'latency', 'native-path']:
    encoded = base64.b64encode((HERE / 'figures' / f'{name}.png').read_bytes()).decode()
    body = body.replace(f'src="figures/{name}.png"', f'src="data:image/png;base64,{encoded}"')
html = '''<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Can a small local model decide whether a shell command is safe?</title>
<style>body{margin:0;background:#f4f6f8;color:#172b41;font:18px/1.65 system-ui,sans-serif}
article{max-width:860px;margin:40px auto;padding:48px;background:white;border-radius:14px}
h1{font-size:42px;line-height:1.15;letter-spacing:-1px}h2{margin-top:40px;font-size:26px}
img{width:100%;height:auto;margin:20px 0}a{color:#126e77}code{font-size:.9em;background:#f1f4f6;padding:2px 4px}
table{width:100%;border-collapse:collapse;font-size:.9em}th,td{padding:.65em;border-bottom:1px solid #dfe2df;text-align:left;vertical-align:top}th{background:#eef3f5}
@media(max-width:650px){article{margin:0;padding:24px}h1{font-size:32px}body{font-size:16px}table{display:block;overflow-x:auto}th,td{min-width:8em}}
@media print{article{margin:0;padding:0}body{background:white}img{break-inside:avoid}}
</style><article>''' + body + '</article></html>'
(HERE / 'POST.html').write_text(html)
print('Rendered offline HTML reading copy.')
