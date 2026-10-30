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
        self.guides = 0
        self.scene_checks = []
        self.npcs = set()

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get('id'):
            if a['id'] in self.ids:
                self.duplicates.append(a['id'])
            self.ids.add(a['id'])
        if tag == 'article' and a.get('data-page-id'):
            self.pages += 1
        if tag == 'article' and a.get('id') == 'guia-direccion':
            self.guides += 1
        if a.get('data-scene-check'):
            self.scene_checks.append(a['data-scene-check'])
        if a.get('data-npc'):
            self.npcs.add(a['data-npc'])
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
page = (ROOT / 'index.html').read_text(encoding='utf-8')
reader.feed(page)
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
if reader.guides != 1:
    errors.append('Se esperaba una guía de dirección')
if reader.scene_checks != [str(n) for n in range(1, 26)]:
    errors.append('Faltan pruebas de escena o no están ordenadas del 1 al 25')
expected_npcs = {'goswin', 'gismondo', 'hel', 'markolf', 'elva', 'anselm',
                 'diomira', 'matabichos', 'ewald', 'engendro', 'lobos'}
if reader.npcs != expected_npcs:
    errors.append(f'Fichas rápidas de PNJ incompletas: {reader.npcs ^ expected_npcs}')
guide_source = (ROOT / 'content/guia-direccion.html').read_text(encoding='utf-8').strip()
embedded = re.search(r'<!-- hallt-gm-guide:start -->\s*(.*?)\s*<!-- hallt-gm-guide:end -->', page, re.S)
if not embedded or embedded.group(1) != guide_source:
    errors.append('Guía incrustada desactualizada: ejecuta scripts/update_rules_guide.py')
navigation = page.split('</nav>', 1)[0]
if not re.search(r'Parte 5: Noche Bruja</a><a href="#guia-direccion">', navigation):
    errors.append('La guía debe aparecer debajo de Parte 5 en el menú lateral')
if embedded:
    narrative = list(re.finditer(r'<article\b[^>]*\bdata-page-id="[^"]+".*?</article>', page, re.S))
    if not narrative or embedded.start() < narrative[-1].end():
        errors.append('La guía debe seguir al último apartado narrativo')
if errors:
    raise SystemExit('\n'.join(errors))
print(f'Correcto: 6 secciones, guía con 25 pruebas y 11 fichas de PNJ, buscador, {len(reader.ids)} anclas y {len(visited)} CSS con sus recursos locales.')
