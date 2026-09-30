#!/usr/bin/env python3
"""Reconstrói docs/assets/graph.json (o grafo de docs/Grafo.md) a partir das
páginas de docs/.

O grafo foi criado uma única vez por scripts/mediawiki_to_markdown.py, a
partir da cópia de 2010, e desde então as páginas novas e as ligações novas
não entravam nele. Este script lê os .md actuais e volta a escrever o
ficheiro no mesmo formato, sem correr o conversor (que apagaria as edições
posteriores).

Regras (as mesmas do conversor):
  * nós: as páginas de Acampamentos/, Cargos/, Encontros/, Movimento/ e
    Pessoas/, mais as de Restrito/ (que aparecem como destino de ligações);
    ficam de fora os índices, as categorias, Wikinácios/, "Todos os artigos"
    e "Grafo";
  * só há nó para uma página com pelo menos uma ligação de entrada ou de
    saída para outra destas páginas;
  * ligações: as do corpo da página, sem contar a secção "Páginas que ligam
    para aqui" (é gerada a partir das outras) nem o rodapé de categorias;
  * as páginas restritas estão cifradas, por isso não têm ligações de saída
    (só de entrada), tal como no original.

Uso:
    python3 scripts/actualizar_grafo.py              # escreve o ficheiro
    python3 scripts/actualizar_grafo.py --verificar  # só compara; sai com 1
                                                     # se estiver desactualizado
"""
import json
import re
import sys
import urllib.parse
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DOCS = RAIZ / 'docs'
GRAFO = DOCS / 'assets' / 'graph.json'

# Pastas cujas páginas são nós do grafo.
PASTAS = ('Acampamentos', 'Cargos', 'Encontros', 'Movimento', 'Pessoas',
          'Restrito')
CORTE = '## Páginas que ligam para aqui'
LIGACAO = re.compile(r'\]\((<[^>]*>|[^)\s]*)')


def paginas():
    """Devolve {id: caminho} das páginas que podem ser nós."""
    encontradas = {}
    for caminho in sorted(DOCS.rglob('*.md')):
        rel = caminho.relative_to(DOCS)
        if rel.parts[0] not in PASTAS or rel.name == 'index.md':
            continue
        encontradas[rel.with_suffix('.html').as_posix()] = caminho
    return encontradas


def titulo(caminho):
    for linha in caminho.read_text(encoding='utf-8').splitlines():
        if linha.startswith('# '):
            return linha[2:].strip()
    return caminho.stem


def destinos(caminho, existentes):
    """Ids das páginas para onde o corpo de `caminho` liga."""
    texto = caminho.read_text(encoding='utf-8').split(CORTE)[0]
    texto = re.sub(r'`[^`\n]*`', '', texto)  # exemplos de código não contam
    saida = set()
    for alvo in LIGACAO.findall(texto):
        alvo = alvo.strip('<>').split('#')[0]
        if not alvo.endswith('.md') or re.match(r'[a-z]+:', alvo):
            continue
        alvo = urllib.parse.unquote(alvo)
        try:
            rel = (caminho.parent / alvo).resolve().relative_to(DOCS)
        except ValueError:
            continue
        id_ = rel.with_suffix('.html').as_posix()
        if id_ in existentes and id_ != caminho.relative_to(DOCS).with_suffix(
                '.html').as_posix():
            saida.add(id_)
    return saida


def construir():
    pags = paginas()
    arestas = {}
    for id_, caminho in pags.items():
        if id_.startswith('Restrito/'):
            continue  # cifradas: sem ligações de saída
        arestas[id_] = destinos(caminho, pags)
    ligados = {o for o, ds in arestas.items() if ds}
    ligados |= {d for ds in arestas.values() for d in ds}
    nos = sorted(({'id': i, 'title': titulo(pags[i]),
                   'group': i.split('/')[0]} for i in ligados),
                 key=lambda n: (n['title'], n['id']))
    indice = {n['id']: k for k, n in enumerate(nos)}
    ligacoes = sorted({(indice[o], indice[d]) for o, ds in arestas.items()
                       for d in ds})
    return {'nodes': nos, 'links': [list(p) for p in ligacoes]}


def em_ligacoes(grafo):
    """Conjunto de pares (origem, destino) por id, para comparar."""
    ids = [n['id'] for n in grafo['nodes']]
    return {(ids[a], ids[b]) for a, b in grafo['links']}


def resumo(antigo, novo):
    ni = {n['id'] for n in antigo['nodes']}
    nn = {n['id'] for n in novo['nodes']}
    li, ln = em_ligacoes(antigo), em_ligacoes(novo)
    print(f'Nós: {len(ni)} → {len(nn)} '
          f'(+{len(nn - ni)}, -{len(ni - nn)})')
    print(f'Ligações: {len(li)} → {len(ln)} '
          f'(+{len(ln - li)}, -{len(li - ln)})')
    for id_ in sorted(ni - nn):
        print(f'  nó que deixa de existir: {id_}')


def main():
    verificar = '--verificar' in sys.argv[1:]
    novo = construir()
    antigo = json.loads(GRAFO.read_text(encoding='utf-8'))
    resumo(antigo, novo)
    if em_ligacoes(antigo) == em_ligacoes(novo) and \
            {n['id'] for n in antigo['nodes']} == \
            {n['id'] for n in novo['nodes']}:
        print('O grafo está actualizado.')
        return 0
    if verificar:
        print('O grafo está desactualizado: corra '
              'python3 scripts/actualizar_grafo.py')
        return 1
    GRAFO.write_text(json.dumps(novo, ensure_ascii=False), encoding='utf-8')
    print(f'Escrito {GRAFO.relative_to(RAIZ)}.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
