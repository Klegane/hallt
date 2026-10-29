"""Validate the static reader with Python's standard library; no network needed."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import re

ROOT = Path(__file__).resolve().parents[1]

class Reader(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.duplicates = []
        self.references = []
        self.css = []
        self.search = False
        self.pages = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get('id'):
            if a['id'] in self.ids:
                self.duplicates.append(a['id'])
            self.ids.add(a['id'])
        if tag == 'article' and a.get('data-page-id'):
            self.pages += 1
        if tag == 'form' and a.get('role') == 'search':
            self.search = True
        for key in ('src', 'href'):
            if a.get(key):
                self.references.append(a[key])
        if tag == 'link' and a.get('rel') == 'stylesheet':
            self.css.append(a['href'])

def local_path(value, base):
    url = urlsplit(value)
    if url.scheme or url.netloc or not url.path:
        return None
    path = (base / unquote(url.path)).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError(f'Recurso fuera del sitio: {value}')
    return path

reader = Reader()
reader.feed((ROOT / 'index.html').read_text(encoding='utf-8'))
errors = [f'ID duplicado: {value}' for value in reader.duplicates]
for reference in reader.references:
    path = local_path(reference, ROOT)
    if path is not None and not path.is_file():
        errors.append(f'Recurso ausente: {reference}')
    if reference.startswith('#') and unquote(reference[1:]) not in reader.ids:
        errors.append(f'Ancla ausente: {reference}')

visited = set()
pending = [ROOT / name for name in reader.css]
while pending:
    path = pending.pop().resolve()
    if path in visited or not path.is_file():
        continue
    visited.add(path)
    css = re.sub(r'/\*.*?\*/', '', path.read_text(encoding='utf-8'), flags=re.S)
    for match in re.finditer(r'url\(\s*([\'"]?)(.*?)\1\s*\)', css, re.S):
        reference = match.group(2).strip()
        dependency = local_path(reference, path.parent)
        if dependency is not None:
            if not dependency.is_file():
                errors.append(f'Recurso CSS ausente: {path.relative_to(ROOT)} → {reference}')
            elif dependency.suffix == '.css':
                pending.append(dependency)

if reader.pages != 6:
    errors.append(f'Se esperaban 6 páginas narrativas; hay {reader.pages}')
if not reader.search:
    errors.append('Falta el buscador del documento')
if errors:
    raise SystemExit('\n'.join(errors))
print(f'Correcto: 6 secciones, buscador, {len(reader.ids)} anclas y {len(visited)} CSS con sus recursos locales.')
