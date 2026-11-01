"""Build a portable Webflow export, keeping featured media at original quality."""
from pathlib import Path
from urllib.parse import unquote, urlsplit
from html.parser import HTMLParser
import re, html, json, shutil, posixpath, argparse
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--output', type=Path, default=ROOT / 'dist')
args = parser.parse_args()
SOURCE, OUT = ROOT / 'site', args.output.resolve()
if OUT == SOURCE.resolve() or SOURCE.resolve() in OUT.parents:
    raise SystemExit('Output must not overwrite source files.')
files = {p.relative_to(SOURCE).as_posix(): p for p in SOURCE.rglob('*') if p.is_file()}
by_name = {}
for name in files:
    by_name.setdefault(Path(name).name.lower(), []).append(name)
missing, external, replacements = set(), set(), {}

def resolve(page, value):
    value = html.unescape(value).replace('\\/', '/')
    if not value or value.startswith(('#','mailto:','tel:','data:','javascript:')): return None
    url = urlsplit(value)
    if url.scheme or url.netloc:
        if any(host in url.netloc for host in ('website-files.com','webflow.com')):
            basename = unquote(url.path.rsplit('/',1)[-1])
            basename = re.sub(r'^[0-9a-f]{24}_', '', basename, flags=re.I)
            matches = by_name.get(basename.lower(), [])
            if len(matches) == 1:
                target = matches[0]
                local = posixpath.relpath(target, posixpath.dirname(page) or '.')
                replacements.setdefault(page, {})[value] = local
                return target
        external.add(value)
        return None
    path = unquote(url.path)
    target = posixpath.normpath(path.lstrip('/') if path.startswith('/') else posixpath.join(posixpath.dirname(page),path))
    if target in files: return target
    if target + '.html' in files: return target + '.html'
    if path: missing.add((page, value))
    return None

class References(HTMLParser):
    def __init__(self):
        super().__init__(); self.urls=[]; self.featured=[]; self.in_json=False
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        for key in ('src','href','poster'):
            if key in attrs: self.urls.append(attrs[key])
        if 'srcset' in attrs:
            self.urls.extend(item.strip().rsplit(None,1)[0] for item in attrs['srcset'].split(',') if item.strip())
        if 'data-video-urls' in attrs: self.urls.extend(attrs['data-video-urls'].split(','))
        if 'style' in attrs: self.urls.extend(re.findall(r'url\([\"\x27]?(.*?)[\"\x27]?\)',attrs['style']))
        if tag=='a' and 'thumbnail-block' in attrs.get('class',''): self.featured.append(attrs.get('href',''))
        self.in_json = tag=='script' and attrs.get('type')=='application/json'
    def handle_endtag(self,tag):
        if tag=='script': self.in_json=False
    def handle_data(self,data):
        if self.in_json:
            try: obj=json.loads(data)
            except ValueError: return
            def walk(obj):
                if isinstance(obj,dict):
                    for key,value in obj.items():
                        if key in ('url','thumbnailUrl') and isinstance(value,str): self.urls.append(value)
                        else: walk(value)
                elif isinstance(obj,list):
                    for value in obj: walk(value)
            walk(obj)

texts={name:p.read_text(encoding='utf-8') for name,p in files.items() if name.endswith(('.html','.css','.js'))}
refs={}; featured={'index.html'}
for name,text in texts.items():
    if name.endswith('.html'):
        parser=References(); parser.feed(text); refs[name]=parser.urls
        if name=='index.html':
            featured.update(filter(None,(resolve(name,url) for url in parser.featured)))
    elif name.endswith('.css'): refs[name]=re.findall(r'url\([\"\x27]?(.*?)[\"\x27]?\)',text)
    else: refs[name]=[]
selected=set(texts); protected=set()
for name,urls in refs.items():
    for url in urls:
        target=resolve(name,url)
        if target:
            selected.add(target)
            if name in featured: protected.add(target)
# CSS background media also retains its original quality.
for name,urls in refs.items():
    if name.endswith('.css'):
        protected.update(filter(None,(resolve(name,url) for url in urls)))
if OUT.exists(): shutil.rmtree(OUT)
optimized=0
for name in sorted(selected):
    target=OUT/name; target.parent.mkdir(parents=True,exist_ok=True)
    if name in texts:
        content=texts[name]
        for remote,local in replacements.get(name,{}).items():
            content=content.replace(remote,local).replace(remote.replace('/','\\/'),local.replace('/','\\/'))
        target.write_text(content,encoding='utf-8')
        if name.endswith('.html') and name not in ('index.html','401.html','404.html'):
            alias=OUT/name[:-5]/'index.html'; alias.parent.mkdir(parents=True,exist_ok=True)
            alias.write_text(content.replace('<head>','<head>\n  <base href="../">',1),encoding='utf-8')
    elif name not in protected and files[name].suffix.lower() in ('.jpg','.jpeg','.png'):
        with Image.open(files[name]) as image:
            image=ImageOps.exif_transpose(image)
            image.thumbnail((1920,1920),Image.Resampling.LANCZOS)
            if files[name].suffix.lower() in ('.jpg','.jpeg'):
                image.convert('RGB').save(target,quality=80,optimize=True,progressive=True)
            else: image.save(target,optimize=True)
        if target.stat().st_size > files[name].stat().st_size: shutil.copy2(files[name],target)
        else: optimized+=1
    else: shutil.copy2(files[name],target)
(OUT/'.nojekyll').touch()
size=sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file())
report={'html_pages':sum(n.endswith('.html') for n in files),'source_files':len(files),'published_files':len(selected),'published_bytes':size,'archive_images_optimized':optimized,'featured_pages':sorted(featured),'protected_assets':len(protected),'missing_local_references':sorted(missing),'external_references':sorted(external)}
(ROOT/'migration-audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ('missing_local_references','external_references')},indent=2))
print(f'Missing local references: {len(missing)}; external references: {len(external)}')
if size >= 1_000_000_000: raise SystemExit('Build exceeds the conservative 1 GB budget. Further archive optimization required.')

