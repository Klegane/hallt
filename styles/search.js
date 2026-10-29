/* Local document search. Never fetches or changes the Journal's source text. */
(() => {
  const main = document.getElementById('adventure-start');
  const form = document.querySelector('.journal-search');
  if (!main || !form) return;
  const input = form.querySelector('input');
  const previous = form.querySelector('[data-search-previous]');
  const next = form.querySelector('[data-search-next]');
  const status = form.querySelector('[role="status"]');
  let matches = [], active = -1, searched = '', timer;
  const fold = text => text.normalize('NFD').replace(/\p{M}/gu, '').toLocaleLowerCase('es');

  function clearHighlights() {
    main.querySelectorAll('mark[data-hallt-search]').forEach(mark => mark.replaceWith(document.createTextNode(mark.textContent)));
    main.normalize();
    matches = []; active = -1;
  }

  function updateStatus() {
    previous.disabled = next.disabled = matches.length === 0;
    status.textContent = !searched ? 'Busca por palabra o frase.' : !matches.length ? 'Sin coincidencias.' : active < 0 ? `${matches.length} coincidencias.` : `${active + 1} de ${matches.length} coincidencias.`;
  }

  function selectMatch(index, scroll = true) {
    if (!matches.length) return;
    if (active >= 0) matches[active].forEach(mark => mark.classList.remove('search-current'));
    active = (index + matches.length) % matches.length;
    matches[active].forEach(mark => mark.classList.add('search-current'));
    updateStatus();
    if (scroll) matches[active][0].scrollIntoView({block:'center', behavior:'auto'});
  }

  function search() {
    clearTimeout(timer);
    clearHighlights();
    searched = input.value.trim();
    const query = fold(searched);
    if (!query) { updateStatus(); return; }
    const blocks = new Map();
    const walker = document.createTreeWalker(main, NodeFilter.SHOW_TEXT);
    while (walker.nextNode()) {
      const node = walker.currentNode, parent = node.parentElement;
      if (!parent || parent.closest('script,style,pre,code,.export-data,[hidden]')) continue;
      const details = parent.closest('details');
      if (details && !details.open && !parent.closest('summary')) continue;
      const block = parent.closest('p,h1,h2,h3,h4,h5,h6,li,td,th,figcaption,summary');
      if (!block || !node.data) continue;
      if (!blocks.has(block)) blocks.set(block, []);
      blocks.get(block).push(node);
    }
    const segmentsByNode = new Map();
    for (const nodes of blocks.values()) {
      const text = nodes.map(node => node.data).join('');
      const starts = [], ends = []; let folded = '', offset = 0;
      for (const character of text) {
        const normalized = fold(character);
        for (let i = 0; i < normalized.length; i++) { starts.push(offset); ends.push(offset + character.length); }
        folded += normalized; offset += character.length;
      }
      let position = 0;
      while ((position = folded.indexOf(query, position)) !== -1) {
        const start = starts[position], end = ends[position + query.length - 1];
        const id = matches.length; matches.push([]);
        let nodeStart = 0;
        nodes.forEach(node => {
          const nodeEnd = nodeStart + node.data.length;
          if (start < nodeEnd && end > nodeStart) {
            if (!segmentsByNode.has(node)) segmentsByNode.set(node, []);
            segmentsByNode.get(node).push({start:Math.max(0,start-nodeStart),end:Math.min(node.data.length,end-nodeStart),id});
          }
          nodeStart = nodeEnd;
        });
        position += query.length;
      }
    }
    for (const [node, segments] of segmentsByNode) {
      const fragment = document.createDocumentFragment(); let cursor = 0;
      for (const segment of segments) {
        fragment.append(document.createTextNode(node.data.slice(cursor, segment.start)));
        const mark = document.createElement('mark');
        mark.dataset.halltSearch = String(segment.id);
        mark.textContent = node.data.slice(segment.start, segment.end);
        fragment.append(mark); matches[segment.id].push(mark); cursor = segment.end;
      }
      fragment.append(document.createTextNode(node.data.slice(cursor)));
      node.replaceWith(fragment);
    }
    updateStatus();
  }

  input.addEventListener('input', () => { clearTimeout(timer); timer = setTimeout(search, 180); });
  form.addEventListener('submit', event => {
    event.preventDefault();
    const changed = input.value.trim() !== searched;
    if (changed) search(); else clearTimeout(timer);
    selectMatch(changed || active < 0 ? 0 : active + 1);
  });
  previous.addEventListener('click', () => { if(input.value.trim() !== searched) search(); selectMatch(active < 0 ? matches.length - 1 : active - 1); });
  next.addEventListener('click', () => { if(input.value.trim() !== searched) search(); selectMatch(active < 0 ? 0 : active + 1); });
  input.addEventListener('keydown', event => {
    if (event.key === 'Escape') { event.preventDefault(); input.value = ''; search(); }
    if (event.key === 'Enter' && event.shiftKey) { event.preventDefault(); if(input.value.trim() !== searched) search(); selectMatch(active < 0 ? matches.length - 1 : active - 1); }
  });
})();
