# Hallt

Lector de **El infierno cabalga hacia Hallt** con el texto narrativo del PDF español y la presentación del Journal exportado de Foundry VTT.

Incluye navegación lateral por las seis secciones y una **Guía de dirección** después de la Parte 5: Ventaja de Grupo de **¡A las armas!**, magia de Klara, las 25 pruebas expresas del suplemento con ejemplos, reglas de los peligros y 11 fichas rápidas de PNJ y criaturas. También recoge los personajes sin estadísticas publicadas, sin asignarles valores inventados.

Dispone de enlaces internos a perfiles y reglas, fuentes locales Caslon y un buscador que ignora mayúsculas y tildes e incluye la guía. Los perfiles y reglas anexos conservan su contenido original en inglés. Se ha eliminado la fila repetida de Hunfried Mauss de la tabla española. Las fuentes y las decisiones de dirección están indicadas dentro de la guía.

## Abrir la página

Abre `index.html` directamente en el navegador. La página y sus recursos funcionan sin conexión, sin cuentas ni instalación.

También puedes servir la carpeta con Python:

```sh
python -m http.server 8080 --bind 127.0.0.1
```

Visita `http://127.0.0.1:8080`.

## Estructura

- `index.html`: documento de lectura y anexos.
- `content/guia-direccion.html`: fuente editable del nuevo apartado de dirección.
- `scripts/update_rules_guide.py`: integra la guía en el documento sin reescribir la aventura ni sus perfiles originales.
- `styles/`: estilos de lectura, navegación y búsqueda.
- `fonts/`: archivos de fuentes locales.
- `assets/`: imágenes y recursos gráficos.
- `scripts/validate_site.py`: comprobación de enlaces, recursos y estructura del lector.

No hay proceso de compilación ni servicios externos. `.nojekyll` permite servir los archivos estáticos directamente desde la raíz si se configura GitHub Pages.

## Comprobación

```sh
python scripts/validate_site.py
```

Después de editar `content/guia-direccion.html`, ejecuta primero `python scripts/update_rules_guide.py`. El validador comprueba que la copia incrustada está actualizada, las 25 pruebas, las 11 fichas de PNJ y el enlace lateral debajo de Parte 5.

Los textos, imágenes, fuentes y marcas conservan los derechos de sus respectivos titulares. Este repositorio no añade una licencia sobre materiales de terceros.
