"""Embed the authored GM guide in the offline reader without rewriting the Journal."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
START = '<!-- hallt-gm-guide:start -->'
END = '<!-- hallt-gm-guide:end -->'


def render():
    path = ROOT / 'index.html'
    page = path.read_text(encoding='utf-8')
    guide = (ROOT / 'content/guia-direccion.html').read_text(encoding='utf-8').strip()
    block = f'{START}\n{guide}\n{END}'
    if START in page:
        page = re.sub(re.escape(START) + r'.*?' + re.escape(END), lambda _: block, page, flags=re.S)
    else:
        # The six Spanish narrative articles precede all original English appendices.
        articles = list(re.finditer(r'<article\b[^>]*\bdata-page-id="[^"]+".*?</article>', page, re.S))
        if len(articles) != 6:
            raise ValueError('Expected the six original narrative articles')
        position = articles[-1].end()
        page = page[:position] + '\n' + block + '\n' + page[position:]
    if '<a href="#guia-direccion">' not in page.split('</nav>', 1)[0]:
        page = page.replace('<form class="journal-search"', '<a href="#guia-direccion">Guía de dirección: reglas y PNJ</a><form class="journal-search"', 1)
    if '<a href="#tarjetas-personaje">' not in page.split('</nav>', 1)[0]:
        page = page.replace('<form class="journal-search"', '<a href="#tarjetas-personaje">Tarjetas de personaje (PDF)</a><form class="journal-search"', 1)
    if 'href="styles/guide.css"' not in page:
        page = page.replace('</head>', '<link rel="stylesheet" href="styles/guide.css"></head>', 1)
    path.write_text(page, encoding='utf-8', newline='\n')


if __name__ == '__main__':
    render()
    print('Guía integrada después de la Parte 5; navegación y búsqueda disponibles.')
