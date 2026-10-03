#!/usr/bin/env python3
"""Escreve docs/Recentes.md: as 50 páginas do Wikinácios alteradas há menos
tempo, com a data da última alteração, lidas do histórico do git.

Ficam de fora as páginas restritas (Restrito/), os índices, as categorias,
as páginas geradas ("Todos os artigos", "Grafo", "Recentes") e as de
Wikinácios/. O histórico tem de estar completo (no GitHub Actions:
`fetch-depth: 0`); com um clone superficial a lista sairia errada.

Uso:
    python3 scripts/actualizar_recentes.py
"""
import subprocess
import sys
import urllib.parse
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DOCS = RAIZ / 'docs'
SAIDA = DOCS / 'Recentes.md'
LIMITE = 50
EXCLUIDAS = {'Todos os artigos.md', 'Grafo.md', 'Recentes.md', 'index.md'}
PASTAS_EXCLUIDAS = {'Restrito', 'Categorias', 'Wikinácios', 'assets'}


def titulo(caminho):
    for linha in caminho.read_text(encoding='utf-8').splitlines():
        if linha.startswith('# '):
            return linha[2:].strip()
    return caminho.stem


def elegivel(rel):
    return (rel.suffix == '.md' and rel.name != 'index.md'
            and rel.as_posix() not in EXCLUIDAS
            and rel.parts[0] not in PASTAS_EXCLUIDAS)


def ultimas():
    """[(data, caminho relativo a docs/)] das páginas mais recentes."""
    if subprocess.run(['git', 'rev-parse', '--is-shallow-repository'],
                      cwd=RAIZ, capture_output=True, text=True
                      ).stdout.strip() == 'true':
        sys.exit('Histórico incompleto: corra `git fetch --unshallow`.')
    saida = subprocess.run(
        ['git', '-c', 'core.quotepath=off', 'log', '--no-merges',
         '--name-only', '--date=format:%d/%m/%Y', '--format=@@%ad', '--', 'docs'],
        cwd=RAIZ, capture_output=True, text=True, check=True).stdout
    vistas, data = {}, None
    for linha in saida.splitlines():
        if linha.startswith('@@'):
            data = linha[2:]
        elif linha.startswith('docs/'):
            rel = Path(linha).relative_to('docs')
            if rel in vistas or not (DOCS / rel).is_file() or not elegivel(rel):
                continue
            vistas[rel] = data
        if len(vistas) >= LIMITE:
            break
    return [(d, r) for r, d in vistas.items()]  # já por ordem decrescente


def main():
    linhas = [
        '# Recentes', '',
        f'As {LIMITE} páginas alteradas há menos tempo, com a data da última '
        'alteração. As páginas restritas não aparecem.', '',
        '| Página | Alterada em |', '| --- | --- |']
    for data, rel in ultimas():
        ligacao = urllib.parse.quote(rel.as_posix())
        linhas.append(f'| [{titulo(DOCS / rel)}]({ligacao}) '
                      f'| {data} |')
    SAIDA.write_text('\n'.join(linhas) + '\n', encoding='utf-8')
    print(f'{SAIDA.relative_to(RAIZ)} escrito.')


if __name__ == '__main__':
    main()
